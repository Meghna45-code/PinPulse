"""
Intent Decay Engine — Time-based behavioral modifiers with exponential decay.
Handles wishlist/cart boosts and buy suppressions.
"""

import math
from config import INTENT_DECAY_CONFIG

class IntentDecayEngine:
    def __init__(self):
        self.CONFIG = INTENT_DECAY_CONFIG

    def calculate_decayed_score(self, action_type, hours_elapsed):
        """Calculates the current modifier based on exponential decay."""
        if action_type not in self.CONFIG:
            return 0.0

        initial = self.CONFIG[action_type]["initial"]
        half_life = self.CONFIG[action_type]["half_life_hours"]

        # Exponential decay formula: Initial * 0.5^(t/H)
        current_modifier = initial * math.pow(0.5, (hours_elapsed / half_life))
        return round(current_modifier, 4)

    def apply_session_modifiers(self, product_catalog, user_interactions, cf_lookup):
        """
        Loops through user history, calculates decayed boosts/penalties,
        and applies them to the catalog.
        """
        item_modifiers = {}

        # 1. Calculate modifiers based on history
        for interaction in user_interactions:
            item_id = interaction["item_id"]
            action = interaction["action_type"]
            hours = interaction["hours_elapsed"]

            # Safe conversion of item_id type
            try:
                item_id = int(item_id)
            except ValueError:
                pass

            modifier = self.calculate_decayed_score(action, hours)

            # Apply to the exact item
            item_modifiers[item_id] = item_modifiers.get(item_id, 0.0) + modifier

            # Apply to the Collaborative Filtering cluster (if positive intent)
            lookup_key = item_id
            if lookup_key not in cf_lookup and str(lookup_key) in cf_lookup:
                lookup_key = str(lookup_key)
            elif lookup_key not in cf_lookup and isinstance(lookup_key, str) and lookup_key.isdigit():
                if int(lookup_key) in cf_lookup:
                    lookup_key = int(lookup_key)

            if action in ["wishlist", "cart"] and lookup_key in cf_lookup:
                for rec in cf_lookup[lookup_key].get("recommendations", []):
                    rec_id = rec["id"]
                    try:
                        rec_id = int(rec_id)
                    except ValueError:
                        pass
                    # Scale cluster boost by the statistical strength of the pairing
                    cluster_boost = modifier * rec["strength"]
                    item_modifiers[rec_id] = item_modifiers.get(rec_id, 0.0) + cluster_boost

        # 2. Inject modifiers into the catalog scoring
        for item in product_catalog:
            item_id = item["id"]
            try:
                item_id = int(item_id)
            except ValueError:
                pass
            # S_intent replaces the old S_cf to encompass all behavioral modifiers
            item["s_intent"] = item_modifiers.get(item_id, 0.0)

        return product_catalog
