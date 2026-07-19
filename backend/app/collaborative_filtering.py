"""
Collaborative Filtering Engine — Co-Purchase Mapping with probabilistic strengths.
Handles PDP shelf recommendations and home feed re-ranking.
"""

class CollaborativeFilteringEngine:
    def __init__(self, cf_lookup_data):
        self.cf_lookup = cf_lookup_data

    def get_pdp_recommendations(self, product_id, product_catalog):
        """Returns items for the 'People Also Bought' shelf, sorted by strength."""
        # Normalize lookup keys for int vs string compatibility
        lookup_key = product_id
        try:
            lookup_key = int(product_id)
        except ValueError:
            pass

        str_key = str(lookup_key)
        int_key = None
        if isinstance(lookup_key, int):
            int_key = lookup_key
        elif isinstance(lookup_key, str) and lookup_key.isdigit():
            int_key = int(lookup_key)

        target_lookup = None
        if int_key is not None and int_key in self.cf_lookup:
            target_lookup = self.cf_lookup[int_key]
        elif str_key in self.cf_lookup:
            target_lookup = self.cf_lookup[str_key]

        if not target_lookup:
            return []

        # Get recommendations and sort them by strength (highest first)
        recs = sorted(
            target_lookup["recommendations"],
            key=lambda x: x["strength"],
            reverse=True,
        )

        rec_ids = []
        for rec in recs:
            r_id = rec["id"]
            try:
                r_id = int(r_id)
            except ValueError:
                pass
            rec_ids.append(r_id)

        # Return full product objects in the correct order
        result = []
        for rid in rec_ids:
            for item in product_catalog:
                item_id = item["id"]
                try:
                    item_id = int(item_id)
                except ValueError:
                    pass
                if item_id == rid:
                    result.append(item)
                    break
        return result

    def recalculate_home_feed(self, product_catalog, user_session_cart, current_mode_weights):
        """Applies probabilistic score bumps based on cart contents."""
        active_cf_boosts = {}  # Dictionary mapping item_id -> highest strength

        # 1. Extract and map probabilities for everything in the cart
        for item_id in user_session_cart:
            try:
                item_id = int(item_id)
            except ValueError:
                pass

            str_key = str(item_id)
            int_key = None
            if isinstance(item_id, int):
                int_key = item_id
            elif isinstance(item_id, str) and item_id.isdigit():
                int_key = int(item_id)

            target_lookup = None
            if int_key is not None and int_key in self.cf_lookup:
                target_lookup = self.cf_lookup[int_key]
            elif str_key in self.cf_lookup:
                target_lookup = self.cf_lookup[str_key]

            if target_lookup:
                for rec in target_lookup["recommendations"]:
                    rec_id = rec["id"]
                    try:
                        rec_id = int(rec_id)
                    except ValueError:
                        pass
                    rec_strength = rec["strength"]

                    # If multiple cart items recommend the same product, take max
                    if rec_id not in active_cf_boosts or rec_strength > active_cf_boosts[rec_id]:
                        active_cf_boosts[rec_id] = rec_strength

        # 2. Score the catalog
        ranked_catalog = []
        w = current_mode_weights
        w6 = 0.3 if active_cf_boosts else 0.0  # CF layer weight

        for item in product_catalog:
            item_id = item["id"]
            try:
                item_id = int(item_id)
            except ValueError:
                pass

            # Retrieve the specific probability strength (defaults to 0.0)
            cf_strength = active_cf_boosts.get(item_id, 0.0)

            # Base Tri-Layer Score + CF layer
            base_score = (
                (w.get("w_aesthetic", 0) * item.get("s_aesthetic", 0))
                + (w.get("w_fabric", 0) * item.get("s_fabric", 0))
                + (w.get("w_festivity", 0) * item.get("s_festivity", 0))
                + (w.get("w_creator", 0) * item.get("s_creator", 0))
                + (w.get("w_boutique", 0) * item.get("s_boutique", 0))
            )

            # Final Score now scales the CF boost by its actual statistical strength
            final_score = base_score + (w6 * cf_strength)

            item_copy = item.copy()
            item_copy["final_score"] = round(final_score, 3)
            item_copy["cf_boost_applied"] = round(w6 * cf_strength, 3)
            ranked_catalog.append(item_copy)

        # 3. Sort descending by the final score
        return sorted(ranked_catalog, key=lambda x: x["final_score"], reverse=True)
