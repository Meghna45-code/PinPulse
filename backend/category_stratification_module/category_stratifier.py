"""
Category Stratification & Diversity Reranking Module (Standalone Demo)
========================================================================
Implements Score-Gated Diversity Stratification:
  - Caps maximum items per fashion category in top pool
  - Prevents single-category dominance while preserving relevance thresholds
  - Isolated standalone module for demonstration purposes (NOT wired into live recommendation pipeline)
"""

def apply_category_stratification(scored_items, min_score_threshold=0.20, max_per_category=2, pool_size=20):
    """
    Applies diversity stratification to a list of scored products.
    
    Args:
        scored_items (list[dict]): Products sorted by matching score descending.
        min_score_threshold (float): Minimum score required to earn a category diversity slot.
        max_per_category (int): Max allowed items per category in diversity pool.
        pool_size (int): Size of top pool to stratify.
        
    Returns:
        list[dict]: Diversified and re-ranked product list.
    """
    if not scored_items:
        return []

    # Sort initial pool by score descending
    items = sorted(scored_items, key=lambda x: x.get("final_score", 0), reverse=True)
    pool = items[:pool_size]
    
    category_counts = {}
    diversity_slots = []
    remainder = []
    
    for item in pool:
        cat = item.get("category", "other")
        count = category_counts.get(cat, 0)
        score = item.get("final_score", 0)
        
        if score >= min_score_threshold and count < max_per_category:
            category_counts[cat] = count + 1
            diversity_slots.append(item)
        else:
            remainder.append(item)
            
    merged = diversity_slots + remainder + items[pool_size:]
    
    # Deduplicate while preserving order
    seen_ids = set()
    deduped = []
    for item in merged:
        item_id = item.get("id") or item.get("product_id")
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            deduped.append(item)
            
    return deduped

if __name__ == "__main__":
    demo_products = [
        {"id": 1, "name": "Banarasi Silk Saree", "category": "Saree", "final_score": 0.95},
        {"id": 2, "name": "Kanjeevaram Silk Saree", "category": "Saree", "final_score": 0.92},
        {"id": 3, "name": "Chanderi Silk Saree", "category": "Saree", "final_score": 0.90},
        {"id": 4, "name": "Zardozi Lehenga", "category": "Lehenga", "final_score": 0.88},
        {"id": 5, "name": "Gota Patti Lehenga", "category": "Lehenga", "final_score": 0.85},
        {"id": 6, "name": "Anarkali Kurti Set", "category": "Kurti", "final_score": 0.82},
    ]
    
    print("=" * 60)
    print("DEMO: CATEGORY STRATIFICATION MODULE")
    print("=" * 60)
    print("Original Items:")
    for p in demo_products:
        print(f"  [{p['category']}] {p['name']} -> {p['final_score']*100:.1f}%")
        
    stratified = apply_category_stratification(demo_products, max_per_category=2)
    print("\nStratified Items (Max 2 per category in pool):")
    for p in stratified:
        print(f"  [{p['category']}] {p['name']} -> {p['final_score']*100:.1f}%")
