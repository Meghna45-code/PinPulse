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
            # Dynamic fallback: Find up to 3 complementary products based on tag overlap
            current_product = None
            if int_key is not None:
                current_product = next((p for p in product_catalog if p.get("id") == int_key), None)
            
            if not current_product:
                return []

            current_tags = set(current_product.get("tags", []))
            candidates = []
            
            for p in product_catalog:
                p_id = p.get("id")
                if p_id == int_key:
                    continue
                
                p_tags = set(p.get("tags", []))
                overlap = len(current_tags.intersection(p_tags))
                
                # Boost accessories and footwear to complete the look
                p_category = str(p.get("category", "")).lower()
                if "accessory" in p_category or "footwear" in p_category or "bag" in p_category:
                    overlap += 2.0
                
                candidates.append((p, overlap))
                
            candidates.sort(key=lambda x: x[1], reverse=True)
            return [x[0] for x in candidates[:3]]

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


