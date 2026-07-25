"""
PinPulse Scoring Engine — The core recommendation logic.
Implements the Tri-Layer scoring with 512-dimensional vectors.
"""

import math
import numpy as np
from config import (
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
    Pillar 1: Pure CLIP Image Vector Visual Matching (100% Image Vector).
    Computes 512-dimension continuous cosine similarity dot product against product's visual image_vector.
    """
    if not user_aesthetic_vector:
        return 0.5

    # 1. Image CLIP Visual Vector Cosine Similarity (100% Visual Matching)
    image_vector = product.get("image_vector") or product.get("vector") or product.get("embedding")
    sim_image = 0.5
    if image_vector:
        raw_i = cosine_similarity(user_aesthetic_vector, image_vector)
        sim_image = normalize_cosine_score(raw_i)

    # 2. Pure Visual Image Embedding Score
    hybrid_sim = sim_image

    # Exact nature/category match boost
    user_key = (user_aesthetic or "").lower()
    product_nature = (product.get("nature") or "").lower()
    product_cat = (product.get("category") or "").lower()
    if product_nature == user_key or product_cat == user_key:
        hybrid_sim = min(1.0, hybrid_sim + 0.20)

    return float(np.clip(hybrid_sim, 0.05, 1.0))

def calculate_festivity_score(product, festival_active, target_color, target_nature, festive_context_vector):
    """
    Pillar 3: Spatial-Temporal Festivity Matching (S_festivity).
    No festival = 1.0 (neutral). Festival active: exact match or CLIP image_vector cosine similarity.
    """
    if not festival_active:
        return 1.0  # No penalty when no festival
    
    product_color = product.get("color", "").lower()
    product_nature = product.get("nature", "").lower()
    
    if product_color == target_color.lower() and product_nature == target_nature.lower():
        return 1.0
    
    # Hard penalty for casual modern items (hoodies, denim shirt dresses, tracksuits) during traditional festivals
    tags_lower = [t.lower() for t in product.get("tags", [])]
    cat_lower = product.get("category", "").lower()
    is_casual = any(t in tags_lower for t in ["hoodie", "sweatshirt", "athleisure", "tracksuit", "denim", "streetwear", "sporty"]) or \
                cat_lower in ["urban athleisure", "high-street rebel", "y2k nostalgia"]
    
    is_ethnic = any(t in tags_lower for t in ["ethnic", "festive", "silk", "traditional", "saree", "lehenga", "kurta", "sherwani", "handloom", "ceremonial"]) or \
                cat_lower in ["festive glam", "heritage traditionalist", "earthy handloom"]
    
    if is_casual and not is_ethnic:
        return 0.05

    product_combined_vector = product.get("image_vector") or product.get("event_vector", []) or product.get("vector", [])
    if not product_combined_vector or not festive_context_vector:
        return 0.3
    raw = cosine_similarity(festive_context_vector, product_combined_vector)
    return normalize_cosine_score(raw)

def calculate_creator_score(product, creators, user_age_group):
    """
    Pillar 4: Creator-based Scoring with 100% CLIP Image Vector Matching.
    Matches creator thumbnail CLIP vector against product visual image_vector.
    """
    if product.get("is_evergreen", False):
        return EVERGREEN_FIXED_SCORE
    
    max_score = 0.0
    product_img_vector = product.get("image_vector") or product.get("vector") or product.get("embedding")
    
    for creator in creators:
        creator_vector = creator.get("embedding", creator.get("vector", []))
        if not creator_vector or not product_img_vector:
            continue
        
        # Pure Image Vector Visual Similarity
        base_score = normalize_cosine_score(cosine_similarity(creator_vector, product_img_vector))
        
        # Age Penalty
        product_age = product.get("age_group", "").lower()
        creator_age = creator.get("demographic", "").lower()
        age_penalty = 1.0 if product_age == creator_age else 0.1
        
        # Engagement Weight (subscriber_weight)
        subscriber_weight = creator.get("subscriber_weight", 1.0)
        
        creator_score = base_score * age_penalty * subscriber_weight
        max_score = max(max_score, creator_score)
    
    return max_score

def calculate_boutique_score(product, stores, zip_aov):
    """
    Pillar 5: Local Boutique Scoring with 100% CLIP Image Vector Matching.
    Matches boutique inventory aesthetic & rating against product visual image_vector.
    """
    if product.get("is_evergreen", False):
        return EVERGREEN_FIXED_SCORE
    
    max_score = 0.0
    product_img_vector = product.get("image_vector") or product.get("vector") or product.get("embedding")
    product_category = product.get("category", "").lower()
    
    for store in stores:
        store_vector = store.get("embedding", store.get("vector", []))
        if not store_vector or not product_img_vector:
            continue
        
        # Pure Image Vector Visual Similarity
        base_score = normalize_cosine_score(cosine_similarity(store_vector, product_img_vector))
        
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

    return max_score

def apply_category_stratification(ranked_items, min_categories=MIN_CATEGORIES_TOP_10):
    """
    Priority-Preserving Stratification:
    Ranks 1-4: Strictly reserved for top-scoring Vibe-matched items (e.g., Sarees, Kurtas, Sherwanis).
    Ranks 5+: Category diversity (gowns, streetwear, accessories) injected afterwards.
    """
    if len(ranked_items) <= 4:
        return ranked_items

    # Keep top 4 items strictly in their earned priority positions
    protected_top_4 = ranked_items[:4]
    rest = ranked_items[4:]

    # Apply category diversity to remaining items (ranks 5+)
    categories_seen = set(item.get("category", "unknown") for item in protected_top_4)
    stratified_rest = []
    overflow = []

    for item in rest:
        cat = item.get("category", "unknown")
        if cat not in categories_seen:
            categories_seen.add(cat)
            stratified_rest.append(item)
        else:
            overflow.append(item)

    return protected_top_4 + stratified_rest + overflow

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
    
    # Inject picks into top_pool at random positions (from index 6 to 15)
    for item in discovery_picks:
        insert_idx = random.randint(6, min(15, len(top_pool)))
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
