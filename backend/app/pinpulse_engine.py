"""
PinPulse Engine — The master orchestrator.
Combines all scoring pillars, applies vetos, stratification, and state machine routing.
"""

import time
import random
from app.config import CACHE_TTL_SECONDS, EVERGREEN_FIXED_SCORE
from app.scoring_engine import (
    calculate_aesthetic_score,
    calculate_creator_score,
    calculate_boutique_score,
    apply_category_stratification,
    apply_exploration_split,
    calculate_price_affinity_score,
)

class PinPulseEngine:
    def __init__(self, product_catalog, zip_data, festival_rules, creators, stores, cf_lookup=None):
        self.product_catalog = product_catalog
        self.zip_data = zip_data
        self.festival_rules = festival_rules
        self.creators = creators
        self.stores = stores
        self.cf_lookup = cf_lookup or {}

        # State Hysteresis cache
        self._cache = {}
        self._cache_timestamp = 0

    def _get_cache_key(self, zip_code, user_aesthetic):
        return f"{zip_code}_{user_aesthetic}"

    def score_all_products(self, user_context):
        """
        Master scoring function. Runs the PinPulse Weighted pipeline.
        """
        zip_code = user_context.get("zip_code", "800008")
        user_aesthetic = user_context.get("aesthetic", "")
        user_aesthetic_vector = user_context.get("aesthetic_vector", [])
        user_age_group = user_context.get("age_group", "")
        session_cart = user_context.get("session_cart", [])
        interactions = user_context.get("interactions", [])
        
        # New location vector
        location_vector = user_context.get("location_vector", [])

        cache_key = self._get_cache_key(zip_code, user_aesthetic)
        
        now = time.time()
        if (cache_key in self._cache and 
            now - self._cache_timestamp < CACHE_TTL_SECONDS and
            not session_cart and not interactions):
            return self._cache[cache_key]

        zip_info = self.zip_data.get(zip_code, {})
        zip_aov = zip_info.get("aov", 2500)

        # Dynamic Weights Assignment based on UI Vibe Selection
        if user_aesthetic:
            w_vibe, w_location, w_creator, w_boutique = 0.4, 0.1, 0.3, 0.2
        else:
            w_vibe, w_location, w_creator, w_boutique = 0.0, 0.4, 0.3, 0.3

        zip_creators = self.creators.get(zip_code, [])
        zip_stores = self.stores.get(zip_code, [])

        scored_products = []
        for product in self.product_catalog:
            # We skip hard filtering by p_zips in the new full dataset, or adapt if needed
            
            # === PILLAR 1 & 2: Vibe & Location ===
            s_vibe = calculate_aesthetic_score(product, user_aesthetic_vector) if w_vibe > 0 else 0.0
            s_location = calculate_aesthetic_score(product, location_vector) if w_location > 0 else 0.0

            # === PILLAR 3: Creator Trend Score ===
            s_creator = calculate_creator_score(product, zip_creators, user_age_group) if w_creator > 0 else 0.0

            # === PILLAR 4: Boutique Score ===
            s_boutique = calculate_boutique_score(product, zip_stores, zip_aov) if w_boutique > 0 else 0.0

            # === FINAL SCORE: Weighted Sum ===
            final_score = (
                w_vibe * s_vibe
                + w_location * s_location
                + w_creator * s_creator
                + w_boutique * s_boutique
            )

            # === PRICE AFFINITY MULTIPLIER ===
            product_price = product.get("price")
            s_price = calculate_price_affinity_score(product_price, zip_aov)
            final_score *= s_price

            scored_item = product.copy()
            scored_item.update({
                "s_vibe": round(s_vibe, 3),
                "s_location": round(s_location, 3),
                "s_creator": round(s_creator, 3),
                "s_boutique": round(s_boutique, 3),
                "s_price": round(s_price, 3),
                "final_score": round(final_score, 3),
            })

            scored_item["reason_labels"] = self._generate_labels(scored_item, zip_code)
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
        return []

    def simulate_velocity_surge(self, zip_code):
        return {}

    def _generate_labels(self, item, zip_code):
        labels = []
        if item.get("s_creator", 0) > 0.7:
            labels.append("🔥 Loved by creators in your area")
        if item.get("s_boutique", 0) > 0.7:
            labels.append("🏪 Trending in local boutiques")
        if item.get("s_location", 0) > 0.8:
            labels.append(f"📍 Trending in {zip_code}")
        return labels
