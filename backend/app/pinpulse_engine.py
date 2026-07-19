"""
PinPulse Engine — The master orchestrator.
Combines all scoring pillars, applies vetos, stratification, and state machine routing.
"""

import time
import random
from config import (
    CONTEXT_MATRICES,
    CACHE_TTL_SECONDS,
    EVERGREEN_FIXED_SCORE,
    LOW_STOCK_THRESHOLD,
    LOW_STOCK_PENALTY,
)
from scoring_engine import (
    calculate_aesthetic_score,
    calculate_fabric_score,
    calculate_festivity_score,
    calculate_creator_score,
    calculate_boutique_score,
    calculate_velocity_score,
    apply_category_stratification,
    apply_exploration_split,
)
from intent_decay import IntentDecayEngine
from collaborative_filtering import CollaborativeFilteringEngine

class PinPulseEngine:
    def __init__(self, product_catalog, zip_data, festival_rules, weather_rules,
                 creators, stores, cf_lookup):
        self.product_catalog = product_catalog
        self.zip_data = zip_data
        self.festival_rules = festival_rules
        self.weather_rules = weather_rules
        self.creators = creators
        self.stores = stores
        self.cf_engine = CollaborativeFilteringEngine(cf_lookup)
        self.intent_engine = IntentDecayEngine()
        self.cf_lookup = cf_lookup

        # State Hysteresis cache
        self._cache = {}
        self._cache_timestamp = 0

    def get_context_matrix(self, state="discovery", user_context=None):
        """Get the weight matrix for the current state, dynamically blending weights based on user interaction levels."""
        if not user_context:
            return CONTEXT_MATRICES.get(state, CONTEXT_MATRICES["discovery"])
            
        base_weights = CONTEXT_MATRICES["discovery"].copy()
        
        interactions = user_context.get("interactions", [])
        cart = user_context.get("session_cart", [])
        active_festival = user_context.get("active_festival")
        
        # Count specific action types in the interaction logs
        creator_clicks = sum(1 for x in interactions if x.get("action_type") == "creator")
        boutique_clicks = sum(1 for x in interactions if x.get("action_type") == "boutique")
        
        # Calculate blend factors (0.0 to 1.0)
        # 3 clicks of creator videos shifts you fully to creator social commerce weights
        t_creator = min(1.0, creator_clicks * 0.33)
        # 3 clicks of local boutique lists shifts you fully to boutique weights
        t_boutique = min(1.0, boutique_clicks * 0.33)
        # Cart items shift you towards high intent
        t_intent = min(1.0, len(cart) * 0.50)
        # Festive is binary based on whether a holiday is currently active
        t_festive = 1.0 if active_festival else 0.0
        
        # Target matrices
        c_discovery = CONTEXT_MATRICES["discovery"]
        c_social = CONTEXT_MATRICES["social_commerce"]
        c_boutique = CONTEXT_MATRICES["hyper_local_boutique"]
        c_intent = CONTEXT_MATRICES["high_intent"]
        c_festive = CONTEXT_MATRICES["festive_season"]
        
        # Blend them:
        blended = {}
        for key in base_weights.keys():
            mix_val = (
                (1.0 - t_creator) * (1.0 - t_boutique) * (1.0 - t_intent) * (1.0 - t_festive) * c_discovery[key]
                + t_creator * c_social[key]
                + t_boutique * c_boutique[key]
                + t_intent * c_intent[key]
                + t_festive * c_festive[key]
            )
            blended[key] = mix_val
            
        # Re-normalize to make sure they sum to exactly 1.0
        total = sum(blended.values())
        if total > 0:
            for key in blended:
                blended[key] = round(blended[key] / total, 4)
        else:
            return CONTEXT_MATRICES["discovery"]
                
        return blended

    def _get_cache_key(self, zip_code, state, festival_active, aesthetic):
        return f"{zip_code}_{state}_{festival_active}_{aesthetic}"

    def score_all_products(self, user_context):
        """
        Master scoring function. Runs the full PinPulse pipeline.
        
        user_context = {
            "zip_code": "800008",
            "aesthetic": "ethnic",
            "aesthetic_vector": [...],
            "age_group": "gen-z",
            "state": "discovery",
            "session_cart": [],
            "interactions": [],
            "time_offset_hours": 0,
            "weather_condition": "hot_humid",  # Optional override
            "active_festival": "chhath_puja",  # Optional override
            "active_date": "2026-10-28",        # Current date string
            "upcoming_events": [...]             # Calendar events in the next 7 days
        }
        Upcoming festival priority: events in the next 7 days get a 1.5x festivity
        score boost vs the currently active festival (1.0x).
        """
        zip_code = user_context.get("zip_code", "800008")
        state = user_context.get("state", "discovery")
        user_aesthetic = user_context.get("aesthetic", "")
        user_aesthetic_vector = user_context.get("aesthetic_vector", [])
        user_age_group = user_context.get("age_group", "")
        session_cart = user_context.get("session_cart", [])
        interactions = user_context.get("interactions", [])
        time_offset = user_context.get("time_offset_hours", 0)
        # Upcoming festival context (next 7 days)
        upcoming_events = user_context.get("upcoming_events", [])
        active_date = user_context.get("active_date", "")
 
        # Resolve ZIP-based data
        zip_info = self.zip_data.get(zip_code, {})
        weather_condition = user_context.get("weather_condition") or zip_info.get("weather_conditions", "hot_humid")
        active_festival = user_context.get("active_festival")
        if active_festival is None and "active_festival" in zip_info:
            active_festival = zip_info.get("active_festival")
            
        festival_active = active_festival is not None
        cache_key = self._get_cache_key(zip_code, state, festival_active, user_aesthetic)
        
        now = time.time()
        # Bypass cache if cart has items or interactions exist to keep UI reactive
        if (cache_key in self._cache and 
            now - self._cache_timestamp < CACHE_TTL_SECONDS and
            not session_cart and not interactions):
            return self._cache[cache_key]

        # Get context-specific weights dynamically blended based on user journey
        weights = self.get_context_matrix(state, user_context)

        zip_aov = zip_info.get("aov", 2500)

        # Get allowable materials from weather rules
        weather_rule = self.weather_rules.get(weather_condition, {})
        allowable_materials = weather_rule.get("allowable_materials", ["cotton", "linen"])
        allowable_materials_vector = weather_rule.get("vector", [])

        # Get festival rules
        target_color = ""
        target_nature = ""
        festive_context_vector = []
        if active_festival:
            festival_rule = self.festival_rules.get(active_festival, {})
            target_color = festival_rule.get("target_color", "")
            target_nature = festival_rule.get("target_nature", "")
            festive_context_vector = festival_rule.get("vector", [])

        # Get creators and stores for this ZIP
        zip_creators = self.creators.get(zip_code, [])
        zip_stores = self.stores.get(zip_code, [])

        # Apply time offset to interactions (for Time Warp demo)
        adjusted_interactions = []
        for interaction in interactions:
            adj = interaction.copy()
            adj["hours_elapsed"] = interaction.get("hours_elapsed", 0) + time_offset
            adjusted_interactions.append(adj)

        # Apply intent decay modifiers
        catalog_with_intent = self.intent_engine.apply_session_modifiers(
            [p.copy() for p in self.product_catalog],
            adjusted_interactions,
            self.cf_lookup,
        )

        # Score each product across all pillars
        scored_products = []
        for product in catalog_with_intent:
            # === PILLAR 1: Aesthetic ===
            s_aesthetic = calculate_aesthetic_score(
                product, user_aesthetic, user_aesthetic_vector
            )

            # === PILLAR 2: Fabric/Weather ===
            s_fabric = calculate_fabric_score(
                product, allowable_materials, allowable_materials_vector
            )

            # === WEATHER SOFT PENALTY (was hard veto) ===
            # Instead of dropping products with poor fabric-weather match,
            # apply a heavy score multiplier so they sink to the bottom.
            if s_fabric < 0.2:
                s_fabric = 0.05  # Very low score but still included

            # === PILLAR 3: Festivity (Current vs Upcoming 7-Day Priority Boost) ===
            # Current event: standard score (1.0x)
            s_current = calculate_festivity_score(
                product, festival_active, target_color, target_nature, festive_context_vector
            )

            # Upcoming events: check if product matches any festival in next 7 days
            # Upcoming match gets 1.5x priority over the currently active festival
            s_upcoming = 0.0
            for ev in upcoming_events:
                # Skip if this upcoming event is the same as current active date
                if str(ev.get("date", "")) == str(active_date):
                    continue
                # Skip non-festive events (e.g. weddings are already scored separately)
                if not ev.get("is_festive", True):
                    continue

                ev_attire = ev.get("attire_tags", [])
                if not ev_attire:
                    # Try looking up festival rules by name
                    rule = self.festival_rules.get(ev.get("event_name", "").lower(), {})
                    ev_attire = [rule.get("target_color", ""), rule.get("target_nature", "")]

                # Count tag overlaps between product and upcoming event attire
                if ev_attire:
                    ev_attire_lower = [str(x).lower() for x in ev_attire if x]
                    matches = sum(
                        1 for t in product.get("tags", [])
                        if t.lower() in ev_attire_lower
                    )
                    if matches > 0:
                        # Boost proportional to overlap count, capped at 1.0
                        s_upcoming = max(s_upcoming, min(1.0, 0.35 + 0.2 * matches))

            if s_upcoming > 0:
                # Upcoming events get highest priority: boost up to 1.5
                s_festivity = min(1.5, 1.0 + 0.5 * s_upcoming)
            else:
                # Fall back to current active festival score
                s_festivity = s_current

            # === STEP 2 Creator Trend Score ===
            s_creator = calculate_creator_score(product, zip_creators, user_age_group)

            # === STEP 3 Boutique Score ===
            s_boutique = calculate_boutique_score(product, zip_stores, zip_aov)

            # === Velocity Score ===
            s_velocity = calculate_velocity_score(product)

            # === Intent (from decay engine) ===
            s_intent = product.get("s_intent", 0.0)

            # === CF Score (from cart) ===
            s_cf = 0.0
            if session_cart:
                for cart_item_id in session_cart:
                    # Support both string and int lookup
                    cart_key = cart_item_id
                    try:
                        cart_key = int(cart_item_id)
                    except ValueError:
                        pass
                    
                    lookup_item = None
                    if cart_key in self.cf_lookup:
                        lookup_item = self.cf_lookup[cart_key]
                    elif str(cart_key) in self.cf_lookup:
                        lookup_item = self.cf_lookup[str(cart_key)]

                    if lookup_item:
                        for rec in lookup_item["recommendations"]:
                            rec_id = rec["id"]
                            product_id = product["id"]
                            try:
                                rec_id = int(rec_id)
                            except ValueError:
                                pass
                            try:
                                product_id = int(product_id)
                            except ValueError:
                                pass
                                
                            if rec_id == product_id:
                                s_cf = max(s_cf, rec["strength"])

            # === FINAL SCORE: Weighted Sum ===
            final_score = (
                weights["w_aesthetic"] * s_aesthetic
                + weights["w_fabric"] * s_fabric
                + weights["w_festivity"] * s_festivity
                + weights["w_boutique"] * s_boutique
                + weights["w_creator"] * s_creator
                + weights["w_cf"] * s_cf
                + weights["w_intent"] * s_intent
                + weights["w_velocity"] * s_velocity
            )

            # === INVENTORY PENALTY ===
            if product.get("stock_level", 50) < LOW_STOCK_THRESHOLD:
                final_score *= LOW_STOCK_PENALTY

            # Build the scored item
            scored_item = product.copy()
            scored_item.update({
                "s_aesthetic": round(s_aesthetic, 3),
                "s_fabric": round(s_fabric, 3),
                "s_festivity": round(s_festivity, 3),
                "s_creator": round(s_creator, 3),
                "s_boutique": round(s_boutique, 3),
                "s_velocity": round(s_velocity, 3),
                "s_intent": round(s_intent, 3),
                "s_cf": round(s_cf, 3),
                "final_score": round(final_score, 3),
                "state": state,
            })

            # Generate "Why this is here?" labels for top items
            scored_item["reason_labels"] = self._generate_labels(
                scored_item, active_festival, zip_code
            )

            scored_products.append(scored_item)

        # Sort by final_score descending
        scored_products.sort(key=lambda x: x["final_score"], reverse=True)

        # Apply Category Stratification (prevent Feed Collapse)
        scored_products = apply_category_stratification(scored_products)

        # Apply Exploration vs Exploitation split
        scored_products = apply_exploration_split(scored_products)

        # Cache results
        self._cache[cache_key] = scored_products
        self._cache_timestamp = now

        return scored_products

    def get_pdp_recommendations(self, product_id):
        """Get 'People Also Bought This With...' shelf items."""
        return self.cf_engine.get_pdp_recommendations(product_id, self.product_catalog)

    def simulate_velocity_surge(self, zip_code):
        """
        Dev Panel trigger: Simulate a local velocity surge.
        Returns hardcoded theme + matched items.
        """
        # Hardcoded themes per ZIP for instant demo
        themes = {
            "800008": {
                "theme": "Midnight Blue Festive Bodycons & Modern Lehengas",
                "matched_ids": [3, 7, 12, 45, 88],
            },
            "800001": {
                "theme": "Midnight Blue Festive Bodycons & Modern Lehengas",
                "matched_ids": [3, 7, 12, 45, 88],
            },
            "682001": {
                "theme": "Emerald Green Occasion Wear",
                "matched_ids": [5, 22, 67, 91, 102],
            },
            "560034": {
                "theme": "Emerald Green Occasion Wear",
                "matched_ids": [5, 22, 67, 91, 102],
            },
            "752001": {
                "theme": "Rose Gold Silk Sarees & Traditional Drapes",
                "matched_ids": [1, 15, 34, 56, 78],
            },
            "110049": {
                "theme": "Rose Gold Silk Sarees & Traditional Drapes",
                "matched_ids": [1, 15, 34, 56, 78],
            },
        }
        
        default_theme = {
            "theme": "Vibrant Ethnic Fusion Wear",
            "matched_ids": [1, 3, 5, 7, 12],
        }
        
        result = themes.get(zip_code, default_theme)
        
        # Get full product objects for matched items
        matched_products = []
        for pid in result["matched_ids"]:
            for product in self.product_catalog:
                prod_id = product["id"]
                try:
                    prod_id = int(prod_id)
                except ValueError:
                    pass
                if prod_id == pid:
                    matched_products.append(product)
                    break
        
        return {
            "theme": result["theme"],
            "products": matched_products,
            "log": f"[SYSTEM] 5 velocity spikes detected. [LLM] Theme generated: {result['theme']}. [VECTOR] {len(matched_products)} items matched.",
        }

    def _generate_labels(self, item, active_festival, zip_code):
        """Generate 'Why this is here?' UI labels for top items."""
        labels = []
        
        if item.get("s_festivity", 0) > 0.7 and active_festival:
            labels.append(f"✨ Trending in {zip_code} for {active_festival}")
        
        if item.get("s_creator", 0) > 0.7:
            labels.append("🔥 Loved by creators in your area")
        
        if item.get("s_fabric", 0) > 0.8:
            labels.append("☀️ Perfect for your area's current weather")
        
        if item.get("s_boutique", 0) > 0.7:
            labels.append("🏪 Trending in local boutiques")
        
        if item.get("s_cf", 0) > 0.5:
            labels.append("👥 People also bought this")
        
        return labels
