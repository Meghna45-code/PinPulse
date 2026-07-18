"""
Collaborative Filtering Engine — Co-Purchase Mapping with probabilistic strengths.
Handles PDP shelf recommendations and home feed re-ranking.
"""


class CollaborativeFilteringEngine:
    def __init__(self, cf_lookup_data):
        self.cf_lookup = cf_lookup_data

    def get_pdp_recommendations(self, product_id, product_catalog):
        """Returns items for the 'People Also Bought' shelf, sorted by strength."""
        if product_id not in self.cf_lookup:
            return []

        # Get recommendations and sort them by strength (highest first)
        recs = sorted(
            self.cf_lookup[product_id]["recommendations"],
            key=lambda x: x["strength"],
            reverse=True,
        )

        rec_ids = [rec["id"] for rec in recs]
        # Return full product objects in the correct order
        result = []
        for rid in rec_ids:
            for item in product_catalog:
                if item["id"] == rid:
                    result.append(item)
                    break
        return result

    def recalculate_home_feed(self, product_catalog, user_session_cart, current_mode_weights):
        """Applies probabilistic score bumps based on cart contents."""
        active_cf_boosts = {}  # Dictionary mapping item_id -> highest strength

        # 1. Extract and map probabilities for everything in the cart
        for item_id in user_session_cart:
            if item_id in self.cf_lookup:
                for rec in self.cf_lookup[item_id]["recommendations"]:
                    rec_id = rec["id"]
                    rec_strength = rec["strength"]

                    # If multiple cart items recommend the same product, take max
                    if rec_id not in active_cf_boosts or rec_strength > active_cf_boosts[rec_id]:
                        active_cf_boosts[rec_id] = rec_strength

        # 2. Score the catalog
        ranked_catalog = []
        w = current_mode_weights
        w6 = 0.3 if active_cf_boosts else 0.0  # CF layer weight

        for item in product_catalog:
            # Retrieve the specific probability strength (defaults to 0.0)
            cf_strength = active_cf_boosts.get(item["id"], 0.0)

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
