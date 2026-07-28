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

    def get_context_matrix(self, state=None, user_context=None):
        user_context = user_context or {}
        user_aesthetic = user_context.get("aesthetic", "")
        if user_aesthetic:
            return {"w_vibe": 0.8, "w_location": 0.05, "w_creator": 0.1, "w_boutique": 0.05, "w_festivity": 0.1}
        return {"w_vibe": 0.5, "w_location": 0.2, "w_creator": 0.15, "w_boutique": 0.15, "w_festivity": 0.1}

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
        weights = self.get_context_matrix(None, user_context)
        w_vibe = weights["w_vibe"]
        w_location = weights["w_location"]
        w_creator = weights["w_creator"]
        w_boutique = weights["w_boutique"]

        zip_creators = self.creators.get(zip_code, [])
        zip_stores = self.stores.get(zip_code, [])

        # Helper to check if a product is an Indian/Eastern ethnic garment
        def _is_ethnic_garment(p):
            full_text = (
                str(p.get("name", "")) + " " +
                str(p.get("category", "")) + " " +
                str(p.get("nature", "")) + " " +
                str(p.get("description", "")) + " " +
                " ".join(p.get("tags", []))
            ).lower()
            ethnic_kw = [
                "kurta", "kurti", "saree", "sari", "anarkali", "dupatta", "ethnic", "lehenga", 
                "kaftan", "palazzo", "churidar", "salwar", "sherwani", "bandhgala", "nehru", 
                "handloom", "banarasi", "chanderi", "gotapatti", "zardozi", "block print", 
                "handblock", "tussar", "ikat", "jainsem", "poshak", "sharara", "gharara", 
                "traditional", "indian", "desi", "deshi", "fusion wear", "bengali", "bihari",
                "bandhani", "leheriya", "ajrakh", "chikankari", "phulkari", "kantha"
            ]
            return any(kw in full_text for kw in ethnic_kw)

        # Strict Aesthetic Category Pre-filtering for 100% Visual Parity
        vibe_key = (user_aesthetic or "").lower().strip()
        filtered_catalog = self.product_catalog

        if "traditional" in vibe_key or "universal" in vibe_key or "heritage" in vibe_key:
            eth_items = [
                p for p in self.product_catalog if _is_ethnic_garment(p)
            ]
            if eth_items:
                filtered_catalog = eth_items
        elif "old_money" in vibe_key or "old money" in vibe_key:
            om_items = [
                p for p in self.product_catalog
                if any(k in (str(p.get("name","")) + " " + str(p.get("category","")) + " " + str(p.get("description",""))).lower() for k in ["linen dress", "midi dress", "linen shirt", "linen trousers", "wide leg", "trench coat", "turtleneck", "wool trousers", "tennis skirt", "pleated skirt", "polo", "blazer", "cashmere", "tailored"])
                and any(c in (str(p.get("name","")) + " " + str(p.get("color","")) + " " + str(p.get("description",""))).lower() for c in ["cream", "beige", "white", "navy", "olive", "camel", "charcoal", "burgundy"])
                and not _is_ethnic_garment(p)
            ]
            if om_items:
                filtered_catalog = om_items
        elif "cottage" in vibe_key:
            cot_items = [
                p for p in self.product_catalog
                if any(k in (str(p.get("name","")) + " " + str(p.get("category","")) + " " + str(p.get("description",""))).lower() for k in ["floral", "dress", "skirt", "one-piece", "one piece", "maxi", "midi", "puffy", "puff sleeve", "flowy", "tiered", "ruffle", "lace", "cardigan", "prairie", "blouse", "sundress", "frill"])
                and not _is_ethnic_garment(p)
                and not any(dark in (str(p.get("name","")) + " " + str(p.get("color",""))).lower() for dark in ["black", "charcoal", "dark goth", "goth"])
            ]
            if cot_items:
                filtered_catalog = cot_items
        elif "alt" in vibe_key or "grunge" in vibe_key:
            alt_items = [
                p for p in self.product_catalog
                if any(k in (str(p.get("name","")) + " " + str(p.get("category",""))).lower() for k in ["cargo", "graphic", "tee", "denim", "leather", "jacket", "boots", "hoodie", "streetwear", "biker", "black"])
                and not _is_ethnic_garment(p)
            ]
            if alt_items:
                filtered_catalog = alt_items

        # Fast Vector Matrix Candidate Pruning over filtered catalog
        target_candidates = filtered_catalog
        if len(filtered_catalog) > 500 and user_aesthetic_vector:
            try:
                import numpy as np
                v_arr = np.array(user_aesthetic_vector, dtype=np.float32)
                clean_vecs = []
                for p in filtered_catalog:
                    v = p.get("text_vector") or p.get("image_vector")
                    if isinstance(v, list) and len(v) == 512:
                        clean_vecs.append(v)
                    else:
                        clean_vecs.append([0.0] * 512)
                vec_mat = np.array(clean_vecs, dtype=np.float32)
                
                sims = vec_mat @ v_arr
                top_k = min(500, len(filtered_catalog))
                top_idx = np.argpartition(sims, -top_k)[-top_k:]
                target_candidates = [filtered_catalog[i] for i in top_idx]
            except Exception:
                target_candidates = filtered_catalog[:500]

        scored_products = []
        for product in target_candidates:
            # We skip hard filtering by p_zips in the new full dataset, or adapt if needed
            
            # === PILLAR 1 & 2: Vibe & Location ===
            s_vibe = calculate_aesthetic_score(product, user_aesthetic_vector) if w_vibe > 0 else 0.0
            s_location = calculate_aesthetic_score(product, location_vector) if w_location > 0 else 0.0

            # Creator and Boutique scoring completely disabled per user request
            s_creator = 0.0
            s_boutique = 0.0

            # === FINAL SCORE: Pure Vibe & Location Score ===
            # Re-normalize weights so Vibe and Location fill 100% of score when vibe is selected
            if w_vibe > 0:
                final_score = s_vibe
            else:
                final_score = s_location

            # === PRICE AFFINITY MULTIPLIER ===
            product_price = product.get("price")
            s_price = calculate_price_affinity_score(product_price, zip_aov)
            final_score *= s_price

            scored_item = product.copy()
            scored_item.update({
                "s_vibe": round(s_vibe, 3),
                "s_aesthetic": round(s_vibe, 3),
                "s_location": round(s_location, 3),
                "s_creator": 0.0,
                "s_boutique": 0.0,
                "s_festivity": round(s_vibe, 3),
                "s_price": round(s_price, 3),
                "final_score": round(final_score, 3),
            })

            scored_item["reason_labels"] = self._generate_labels(scored_item, zip_code)
            scored_products.append(scored_item)

        # Sort by final_score descending
        scored_products.sort(key=lambda x: x["final_score"], reverse=True)

        # Category Stratification completely disabled per user request (pure similarity ranking)

        # Apply Exploration vs Exploitation split (deterministic with cache_key as seed)
        scored_products = apply_exploration_split(scored_products, seed_key=cache_key)

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
