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
)
from scoring_engine import (
    calculate_aesthetic_score,
    calculate_festivity_score,
    calculate_creator_score,
    calculate_boutique_score,
    apply_category_stratification,
    apply_exploration_split,
    calculate_price_affinity_score,
)

class PinPulseEngine:
    def __init__(self, product_catalog, zip_data, festival_rules,
                 creators, stores, cf_lookup=None):
        self.product_catalog = product_catalog
        self.zip_data = zip_data
        self.festival_rules = festival_rules
        self.creators = creators
        self.stores = stores
        self.cf_lookup = cf_lookup or {}

        # State Hysteresis cache
        self._cache = {}
        self._cache_timestamp = 0

    def get_context_matrix(self, state="discovery", user_context=None):
        """Get the weight matrix for the current state."""
        return CONTEXT_MATRICES.get(state, CONTEXT_MATRICES["discovery"])

    def _get_cache_key(self, zip_code, state, festival_active, aesthetic, active_date=""):
        return f"{zip_code}_{state}_{festival_active}_{aesthetic}_{active_date}"

    def score_all_products(self, user_context):
        """
        Master scoring function. Runs the PinPulse 4-pillar pipeline + price affinity multiplier.
        """
        zip_code = user_context.get("zip_code", "800008")
        state = user_context.get("state", "discovery")
        user_aesthetic = user_context.get("aesthetic", "")
        user_aesthetic_vector = user_context.get("aesthetic_vector", [])
        user_age_group = user_context.get("age_group", "")
        session_cart = user_context.get("session_cart", [])
        interactions = user_context.get("interactions", [])
        upcoming_events = user_context.get("upcoming_events", [])
        active_date = user_context.get("active_date", "")

        zip_info = self.zip_data.get(zip_code, {})
        active_festival = user_context.get("active_festival")
        if active_festival is None and "active_festival" in zip_info:
            active_festival = zip_info.get("active_festival")
            
        festival_active = active_festival is not None
        cache_key = self._get_cache_key(zip_code, state, festival_active, user_aesthetic, active_date)
        
        now = time.time()
        if (cache_key in self._cache and 
            now - self._cache_timestamp < CACHE_TTL_SECONDS and
            not session_cart and not interactions):
            return self._cache[cache_key]

        weights = self.get_context_matrix(state, user_context)
        zip_aov = zip_info.get("aov", 2500)

        target_color = ""
        target_nature = ""
        festive_context_vector = []
        if active_festival:
            festival_rule = self.festival_rules.get(active_festival, {})
            target_color = festival_rule.get("target_color", "")
            target_nature = festival_rule.get("target_nature", "")
            festive_context_vector = festival_rule.get("vector", [])

        zip_creators = self.creators.get(zip_code, [])
        zip_stores = self.stores.get(zip_code, [])

        scored_products = []
        for product in self.product_catalog:
            p_zips = product.get("zip_codes", [])
            if p_zips and zip_code not in p_zips:
                continue

            # === PILLAR 1: Aesthetic ===
            s_aesthetic = calculate_aesthetic_score(
                product, user_aesthetic, user_aesthetic_vector
            )

            # === PILLAR 2: Festivity ===
            s_current = calculate_festivity_score(
                product, festival_active, target_color, target_nature, festive_context_vector
            )

            s_upcoming = 0.0
            for ev in upcoming_events:
                if str(ev.get("date", "")) == str(active_date):
                    continue
                if not ev.get("is_festive", True):
                    continue

                ev_attire = ev.get("attire_tags", [])
                if not ev_attire:
                    rule = self.festival_rules.get(ev.get("event_name", "").lower(), {})
                    ev_attire = [rule.get("target_color", ""), rule.get("target_nature", "")]

                if ev_attire:
                    ev_attire_lower = [str(x).lower() for x in ev_attire if x]
                    matches = sum(
                        1 for t in product.get("tags", [])
                        if t.lower() in ev_attire_lower
                    )
                    if matches > 0:
                        s_upcoming = max(s_upcoming, min(1.0, 0.35 + 0.2 * matches))

            if s_upcoming > 0:
                s_festivity = min(1.5, 1.0 + 0.5 * s_upcoming)
            else:
                s_festivity = s_current

            # === PILLAR 3: Creator Trend Score ===
            s_creator = calculate_creator_score(product, zip_creators, user_age_group)

            # === PILLAR 4: Boutique Score ===
            s_boutique = calculate_boutique_score(product, zip_stores, zip_aov)

            # === FINAL SCORE: Weighted 4-Pillar Sum ===
            final_score = (
                weights["w_aesthetic"] * s_aesthetic
                + weights["w_festivity"] * s_festivity
                + weights["w_boutique"] * s_boutique
                + weights["w_creator"] * s_creator
            )

            # === PRICE AFFINITY MULTIPLIER (s_price) ===
            product_price = product.get("price")
            s_price = calculate_price_affinity_score(product_price, zip_aov)
            final_score *= s_price

            scored_item = product.copy()
            scored_item.update({
                "s_aesthetic": round(s_aesthetic, 3),
                "s_festivity": round(s_festivity, 3),
                "s_creator": round(s_creator, 3),
                "s_boutique": round(s_boutique, 3),
                "s_price": round(s_price, 3),
                "final_score": round(final_score, 3),
                "state": state,
            })

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
        
        if item.get("s_boutique", 0) > 0.7:
            labels.append("🏪 Trending in local boutiques")
        
        if item.get("s_cf", 0) > 0.5:
            labels.append("👥 People also bought this")
        
        return labels
