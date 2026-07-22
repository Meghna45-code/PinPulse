"""
PinPulse Scoring Engine — The core recommendation logic.
Implements the Tri-Layer scoring with 512-dimensional vectors.
"""

import math
import numpy as np
from config import (
    WEATHER_VETO_THRESHOLD,
    EVERGREEN_FIXED_SCORE,
    RELEVANCE_ALPHA,
    MIN_CATEGORIES_TOP_10,
    EXPLOITATION_RATIO,
)

def cosine_similarity(vec_a, vec_b):
    """Calculate cosine similarity between two 512-dimensional vectors."""
    if not vec_a or not vec_b:
        return 0.0

    def parse_vector(v):
        if isinstance(v, str):
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            cleaned = v.strip("[]{}")
            return [float(x) for x in cleaned.split(",") if x.strip()]
        return v

    try:
        a = np.array(parse_vector(vec_a), dtype=float)
        b = np.array(parse_vector(vec_b), dtype=float)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))
    except Exception:
        return 0.0

def normalize_cosine_score(raw_score):
    """Min-Max Normalization: maps [-1, 1] to [0, 1]."""
    return (raw_score + 1) / 2

def calculate_aesthetic_score(product, user_aesthetic, user_aesthetic_vector):
    """
    Pillar 1: User Aesthetic Matching (S_aesthetic).
    Evaluates semantic tag overlap so user selected vibe dominates ranking.
    """
    user_key = (user_aesthetic or "").lower()
    tags = [t.lower() for t in product.get("tags", [])]
    category = (product.get("category") or "").lower()
    nature = (product.get("nature") or "").lower()

    vibe_tags_map = {
        "heritage_traditionalist": ["traditional", "silk", "heavy", "classic", "ethnic", "saree", "kanjeevaram", "banarasi", "zari", "gold", "temple", "mundu", "sherwani", "jainsem"],
        "festive_glam": ["festive", "bright", "red", "embellished", "celebration", "lehenga", "anarkali", "ceremonial", "heavy_silk", "maroon", "gold", "brocade", "embroidery"],
        "indie_fusion": ["fusion", "cotton", "prints", "oxidized", "casual-ethnic", "block-print", "indigo", "kurta", "denim", "boho", "handblock", "ethnic"],
        "high_street_rebel": ["streetwear", "oversized", "edgy", "grunge", "layered", "cargo", "graphic", "hoodie", "denim", "modern", "rebel", "baggy"],
        "coastal_tropical": ["breathable", "pastel", "floral", "linen", "coastal", "summer", "cotton", "light", "breezy", "sundress", "resort"],
        "winter_academia": ["winter", "layered", "preppy", "knitwear", "smart-casual", "trench", "plaid", "woolen", "jacket", "cardigan", "warm", "shawl", "velvet"],
        "y2k_nostalgia": ["y2k", "vibrant", "retro", "pop", "gen-z", "crop", "baggy", "bucket-hat", "synthetic", "colorful", "neon", "bold"],
        "minimalist_essentials": ["minimal", "neutral", "solid", "clean", "basic", "white", "beige", "black", "fitted", "structured"],
        "earthy_handloom": ["handloom", "organic", "earthy", "comfortable", "khadi", "ochre", "olive", "sustainable", "natural", "artisanal"],
        "urban_athleisure": ["sporty", "activewear", "comfortable", "casual", "sneakers", "tracksuit", "ribbed", "athletic", "gym", "jogger"]
    }

    target_tags = vibe_tags_map.get(user_key, [user_key])
    matches = sum(1 for t in tags if t in target_tags)

    if matches > 0:
        return min(1.0, 0.45 + (matches * 0.15))
    if nature == user_key or category == user_key:
        return 1.0

    product_vector = product.get("aesthetic_vector", [])
    if product_vector and user_aesthetic_vector:
        raw = cosine_similarity(user_aesthetic_vector, product_vector)
        return max(0.1, normalize_cosine_score(raw) * 0.3)

    return 0.1

def calculate_fabric_score(product, allowable_materials, allowable_materials_vector):
    """
    Pillar 2: Climate-Fabric Matching (S_fabric).
    Exact material match = 1.0, otherwise cosine similarity.
    """
    product_material = product.get("material", "")
    if product_material.lower() in [m.lower() for m in allowable_materials]:
        return 1.0
    product_fabric_vector = product.get("fabric_vector", [])
    if not product_fabric_vector or not allowable_materials_vector:
        return 0.5
    raw = cosine_similarity(allowable_materials_vector, product_fabric_vector)
    return normalize_cosine_score(raw)

def calculate_festivity_score(product, festival_active, target_color, target_nature, festive_context_vector):
    """
    Pillar 3: Spatial-Temporal Festivity Matching (S_festivity).
    No festival = 1.0 (neutral). Festival active: exact match or cosine similarity.
    """
    if not festival_active:
        return 1.0  # No penalty when no festival
    
    product_color = product.get("color", "").lower()
    product_nature = product.get("nature", "").lower()
    
    if product_color == target_color.lower() and product_nature == target_nature.lower():
        return 1.0
    
    product_combined_vector = product.get("event_vector", [])
    if not product_combined_vector or not festive_context_vector:
        return 0.3
    raw = cosine_similarity(festive_context_vector, product_combined_vector)
    return normalize_cosine_score(raw)

def calculate_creator_score(product, creators, user_age_group):
    """
    Step 2 Trend Sensing: Creator-based scoring.
    Uses Max Match Rule across all creators.
    Includes: Age Penalty, Engagement Weight, Evergreen Bypass.
    """
    if product.get("is_evergreen", False):
        return EVERGREEN_FIXED_SCORE
    
    max_score = 0.0
    product_vector = product.get("aesthetic_vector", [])
    
    for creator in creators:
        creator_vector = creator.get("embedding", creator.get("vector", []))
        if not creator_vector or not product_vector:
            continue
        
        # Base Score: Cosine Similarity
        base_score = normalize_cosine_score(
            cosine_similarity(creator_vector, product_vector)
        )
        
        # Age Penalty
        product_age = product.get("age_group", "").lower()
        creator_age = creator.get("demographic", "").lower()
        age_penalty = 1.0 if product_age == creator_age else 0.1
        
        # Engagement Weight (subscriber_weight)
        subscriber_weight = creator.get("subscriber_weight", 1.0)
        
        # Final Creator Score for this creator
        creator_score = base_score * age_penalty * subscriber_weight
        max_score = max(max_score, creator_score)
    
    return max_score

def calculate_boutique_score(product, stores, zip_aov):
    """
    Step 3 Local Store (Boutique) Score.
    Includes: Stretched rating, review count penalty, category gate, price-affinity.
    """
    if product.get("is_evergreen", False):
        return EVERGREEN_FIXED_SCORE
    
    max_score = 0.0
    product_vector = product.get("aesthetic_vector", [])
    product_category = product.get("category", "").lower()
    
    for store in stores:
        store_vector = store.get("embedding", store.get("vector", []))
        if not store_vector or not product_vector:
            continue
        
        # Base cosine similarity
        base_score = normalize_cosine_score(
            cosine_similarity(store_vector, product_vector)
        )
        
        # Stretched Rating: W_rating = max(0, (Rating - 3.0) / 2.0)
        rating = store.get("rating", 3.0)
        w_rating = max(0.0, (rating - 3.0) / 2.0)
        
        # Review count penalty
        review_count = store.get("review_count", 0)
        if review_count < 50:
            w_rating *= 0.5
        
        # Category-Specific Weighting Gate
        # Only heavily apply for Ethnic/Occasion; slash for Western/Casual
        if product_category in ["ethnic", "occasion", "festive", "traditional"]:
            category_gate = 1.0
        else:
            category_gate = 0.2
        
        # Price-Affinity Clamping
        store_cost = store.get("estimated_cost", 0)
        if store_cost > zip_aov * 2:
            price_penalty = 0.3
        else:
            price_penalty = 1.0
        
        store_score = base_score * w_rating * category_gate * price_penalty
        max_score = max(max_score, store_score)
    
    return max_score

def calculate_velocity_score(product):
    """
    Velocity scoring based on relative delta (Z-Score approach).
    Trend triggers when velocity spikes 200% above moving average.
    """
    baseline = product.get("baseline_sales", 1)
    current = product.get("current_sales", 0)
    
    if baseline <= 0:
        return 0.0
    
    delta_ratio = current / baseline
    
    # Normalize: a 3x spike (200% above baseline) = 1.0
    # Below baseline = 0.0
    if delta_ratio <= 1.0:
        return 0.0
    
    velocity = min(1.0, (delta_ratio - 1.0) / 2.0)
    return velocity

def apply_category_stratification(ranked_items, min_categories=MIN_CATEGORIES_TOP_10):
    """
    Category Stratification: Ensure top 10 items have at least 4 distinct categories.
    Prevents 'Wall of Yellow' / Feed Collapse.
    """
    if len(ranked_items) <= min_categories:
        return ranked_items
    
    top_10 = ranked_items[:10]
    remaining = ranked_items[10:]
    
    # Check category diversity in top 10
    categories_seen = set()
    stratified = []
    overflow = []
    
    for item in top_10:
        cat = item.get("category", "unknown")
        if cat not in categories_seen or len(categories_seen) >= min_categories:
            categories_seen.add(cat)
            stratified.append(item)
        else:
            overflow.append(item)
    
    # If we need more diversity, pull from remaining
    if len(categories_seen) < min_categories:
        for item in remaining:
            cat = item.get("category", "unknown")
            if cat not in categories_seen:
                categories_seen.add(cat)
                stratified.insert(len(stratified), item)
                if len(categories_seen) >= min_categories:
                    break
    
    # Rebuild: stratified top + overflow + remaining
    result = stratified + overflow + [i for i in remaining if i not in stratified]
    return result

def apply_exploration_split(ranked_items):
    """
    Exploration vs Exploitation: 90% top-scored + 10% discovery items.
    Discovery = items with high vibe but low velocity (hidden gems).
    The discovery items are randomly injected into the top results (positions 3-15)
    so users actually get a chance to see them.
    """
    if len(ranked_items) < 10:
        return ranked_items
    
    split_point = int(len(ranked_items) * EXPLOITATION_RATIO)
    top_pool = list(ranked_items[:split_point])
    discovery_pool = list(ranked_items[split_point:])
    
    # Pick random discovery items (high aesthetic but low velocity)
    import random
    discovery_count = max(1, int(len(ranked_items) * (1 - EXPLOITATION_RATIO)))
    discovery_picks = random.sample(
        discovery_pool, min(discovery_count, len(discovery_pool))
    )
    
    # Remove picked discovery items from the catalog pool to prevent duplicate entries
    remaining_discovery = [item for item in discovery_pool if item not in discovery_picks]
    
    # Inject picks into top_pool at random positions (e.g. from index 3 to 15, or len(top_pool))
    for item in discovery_picks:
        insert_idx = random.randint(3, min(15, len(top_pool)))
        top_pool.insert(insert_idx, item)
        
    return top_pool + remaining_discovery

def get_boosted_score(product_vector, trend_vector, alpha=RELEVANCE_ALPHA):
    """
    Relevance Confidence Threshold: Don't boost if similarity < alpha.
    Prevents trending noise from boosting unrelated products.
    """
    if not product_vector or not trend_vector:
        return 0.0
    similarity = normalize_cosine_score(
        cosine_similarity(product_vector, trend_vector)
    )
    if similarity < alpha:
        return 0.0
    return similarity

def estimate_user_age(cart_products, wishlist_products, default_age_group):
    """
    Estimate the user's age demographic group based on products in cart and wishlist.
    - 'gen-z' (approx 20)
    - 'millennial' (approx 32)
    - 'mid-age' (approx 50)
    """
    total_age = 0
    count = 0
    
    # Merge both item lists
    all_items = cart_products + wishlist_products
    if not all_items:
        return default_age_group.lower().strip()
        
    for item in all_items:
        age_str = item.get("age_group", "").lower().strip()
        if "gen-z" in age_str or "gen z" in age_str:
            total_age += 20
            count += 1
        elif "millennial" in age_str:
            total_age += 32
            count += 1
        elif "mid-age" in age_str or "senior" in age_str or "mid age" in age_str:
            total_age += 50
            count += 1
            
    if count == 0:
        return default_age_group.lower().strip()
        
    avg_age = total_age / count
    if avg_age < 26:
        return "gen-z"
    elif avg_age < 40:
        return "millennial"
    else:
        return "mid-age"

def calculate_age_appropriateness_score(product_age_group, user_age_group):
    """
    Age Appropriateness Score:
    Match = 1.0, Adjacent = 0.5, Mismatch = 0.1
    """
    p_age = product_age_group.lower().strip().replace(" ", "-")
    u_age = user_age_group.lower().strip().replace(" ", "-")
    
    if p_age == u_age:
        return 1.0
    
    # Adjacent check
    if (p_age == "gen-z" and u_age == "millennial") or (p_age == "millennial" and u_age == "gen-z"):
        return 0.5
    if (p_age == "millennial" and u_age == "mid-age") or (p_age == "mid-age" and u_age == "millennial"):
        return 0.5
        
    # Heavy mismatch
    return 0.1

def calculate_price_affinity_score(product_price, zip_aov):
    """
    ZIP Code AOV Price-Affinity Scoring:
    - Product Price <= AOV * 1.2: Score = 1.0 (affordable)
    - Product Price between AOV * 1.2 and AOV * 2.0: Linear decay from 1.0 to 0.2
    - Product Price > AOV * 2.0: Score = 0.2 (heavy penalty)
    """
    price = float(product_price) if product_price is not None else 1099.0
    aov = float(zip_aov) if zip_aov is not None else 2500.0
    
    if price <= aov * 1.2:
        return 1.0
    elif price <= aov * 2.0:
        # Linear decay formula
        fraction = (price - aov * 1.2) / (aov * 0.8)
        return round(1.0 - fraction * 0.8, 3)
    else:
        return 0.2
