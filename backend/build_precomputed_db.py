import os
import json
import random
import sys

print("Building precomputed_feed_db.json for PinPulse Hyper-Local Engine...")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(ROOT_DIR, "local_catalog.json")
OUT_PATH = os.path.join(ROOT_DIR, "precomputed_feed_db.json")

# Ensure catalog exists
if not os.path.exists(CATALOG_PATH):
    print(f"Error: {CATALOG_PATH} not found!")
    sys.exit(1)

print("Loading local catalog into memory...")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    raw_catalog = json.load(f)

print(f"Total catalog items loaded: {len(raw_catalog)}")

# Filter catalog items by gender segment
women_catalog = [p for p in raw_catalog if p.get("gender") in ("women", "unisex")]
men_catalog = [p for p in raw_catalog if p.get("gender") in ("men", "unisex")]
kids_keywords = ("boy", "girl", "kid", "child", "junior", "teen", "baby")
kids_catalog = [
    p for p in raw_catalog 
    if p.get("gender") in ("boys", "girls", "kids") or 
       any(k in str(p.get("category", "")).lower() or k in str(p.get("name", "")).lower() for k in kids_keywords)
]
if not kids_catalog:
    kids_catalog = raw_catalog[:1000]

print(f"Gender pools - Women: {len(women_catalog)}, Men: {len(men_catalog)}, Kids: {len(kids_catalog)}")

ZIP_CODES = {
    "800008": {"city": "Patna", "state": "Bihar", "aov": 1800, "tags": ["ethnic", "silk", "banarasi", "festive", "chariot", "gold"]},
    "302001": {"city": "Jaipur", "state": "Rajasthan", "aov": 2400, "tags": ["bandhani", "gota_patti", "royal", "lehenga", "pink", "choli"]},
    "793001": {"city": "Shillong", "state": "Meghalaya", "aov": 2100, "tags": ["highland", "winter", "knitwear", "jainsem", "korean", "coat"]},
    "752001": {"city": "Puri", "state": "Odisha", "aov": 1500, "tags": ["sambalpuri", "handloom", "ikat", "temple", "bomkai", "tussar"]},
    "682001": {"city": "Kochi", "state": "Kerala", "aov": 2200, "tags": ["kasavu", "kanjeevaram", "coastal", "linen", "white", "gold"]}
}

CREATOR_CHANNELS_MAP = {
    "800008": ["PatnaFashionDiaries", "BihariBrideStyles", "MaithiliVlogs", "PatnaBoutiqueHunter"],
    "302001": ["JaipurPinkVibes", "RajputiRoyalty", "BandhaniDiaries", "PinkCityHauls"],
    "793001": ["ShillongStyleLab", "KhasiFashionVlogs", "HighlandChic", "PoliceBazarTrends"],
    "752001": ["OdiaHandloomDiaries", "PuriFestiveVlogs", "SambalpuriChic", "UtkalFashionHouse"],
    "682001": ["KochiCoutureVlogs", "MalayaliBrideTrends", "KasavuStyleLab", "CoastalKeralaFashion"]
}

BOUTIQUE_DEFS = {
    "800008": [
        {"store_id": "STR_800008_001", "store_name": "Patna Saree Market & Silk House", "locality": "Frazer Road, Patna", "rating": "4.8 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Patna+Saree+Market+Frazer+Road+Patna", "signature": "Banarasi Silk & Zardozi Wedding Lehengas"},
        {"store_id": "STR_800008_002", "store_name": "Hathwa Market Boutique Hub", "locality": "Bakerganj, Patna", "rating": "4.7 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Hathwa+Market+Bakerganj+Patna", "signature": "Chhath Puja Red Silk Sarees & Anarkali Suits"},
        {"store_id": "STR_800008_003", "store_name": "Khetan Super Market Traditional Store", "locality": "Birla Mandir Road, Patna", "rating": "4.6 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Khetan+Super+Market+Patna", "signature": "Bihari Bridal Dupattas & Ethnic Kurti Sets"},
        {"store_id": "STR_800008_004", "store_name": "Maurya Lok Fashion Studio", "locality": "Maurya Lok Complex, Patna", "rating": "4.5 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Maurya+Lok+Patna", "signature": "Indo-Western Ethnic Wear & Designer Suits"}
    ],
    "302001": [
        {"store_id": "STR_302001_001", "store_name": "Johari Bazaar Royal Rajputi Poshak", "locality": "Johari Bazaar, Jaipur", "rating": "4.9 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Johari+Bazaar+Jaipur", "signature": "Royal Rajputi Poshak & Heavy Gota Patti Work"},
        {"store_id": "STR_302001_002", "store_name": "Bapu Bazaar Bandhani Emporium", "locality": "Bapu Bazaar, Jaipur", "rating": "4.8 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Bapu+Bazaar+Jaipur", "signature": "Jaipur Bandhani & Leheriya Pure Georgette Sarees"},
        {"store_id": "STR_302001_003", "store_name": "C-Scheme Designer Handloom Studio", "locality": "C-Scheme, Jaipur", "rating": "4.7 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=C-Scheme+Jaipur", "signature": "Sanganeri Block-Print Cotton Kurtis & Skirts"},
        {"store_id": "STR_302001_004", "store_name": "MI Road Heritage Silk House", "locality": "Mirza Ismail Road, Jaipur", "rating": "4.6 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=MI+Road+Jaipur", "signature": "Brocade Silk Lehengas & Festive Sharara Sets"}
    ],
    "793001": [
        {"store_id": "STR_793001_001", "store_name": "Police Bazar Khasi Traditional Jainsem House", "locality": "Police Bazar, Shillong", "rating": "4.8 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Police+Bazar+Shillong", "signature": "Pure Ryndia & Silk Jainsem Drapes"},
        {"store_id": "STR_793001_002", "store_name": "Laitumkhrah Highland Boutique", "locality": "Laitumkhrah, Shillong", "rating": "4.7 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Laitumkhrah+Shillong", "signature": "Highland Winter Knitwear & Korean Maxi Coats"},
        {"store_id": "STR_793001_003", "store_name": "Cathedral Road Western Bridal Studio", "locality": "Cathedral Road, Shillong", "rating": "4.9 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Cathedral+Road+Shillong", "signature": "Pristine White Lace Gowns & Formal Silk Suits"},
        {"store_id": "STR_793001_004", "store_name": "Bara Bazar Handloom Centre", "locality": "Iewduh (Bara Bazar), Shillong", "rating": "4.5 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Bara+Bazar+Shillong", "signature": "Traditional Meghalayan Shawls & Wrap Skirts"}
    ],
    "752001": [
        {"store_id": "STR_752001_001", "store_name": "Grand Road Sambalpuri Handloom House", "locality": "Grand Road, Puri", "rating": "4.9 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Grand+Road+Puri", "signature": "Authentic Sambalpuri Pure Silk Ikat Sarees"},
        {"store_id": "STR_752001_002", "store_name": "Puri Beach Market Bomkai Emporium", "locality": "Golden Beach Road, Puri", "rating": "4.7 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Beach+Road+Puri", "signature": "Traditional Bomkai Silk Sarees with Temple Borders"},
        {"store_id": "STR_752001_003", "store_name": "Swargadwar Handloom & Handicraft Hub", "locality": "Swargadwar, Puri", "rating": "4.6 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Swargadwar+Puri", "signature": "Margasira Festive Handloom Kurtis & Tussar Silk"},
        {"store_id": "STR_752001_004", "store_name": "Temple Road Odia Craft Studio", "locality": "Near Jagannath Temple, Puri", "rating": "4.8 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Jagannath+Temple+Puri", "signature": "Khandua Pata Sarees & Traditional Puja Wear"}
    ],
    "682001": [
        {"store_id": "STR_682001_001", "store_name": "MG Road Kasavu & Kanjeevaram Saree Palace", "locality": "MG Road, Kochi", "rating": "4.9 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=MG+Road+Kochi", "signature": "Traditional Kerala Kasavu & Kanjeevaram Silk"},
        {"store_id": "STR_682001_002", "store_name": "Broadway Marine Drive Handloom Emporium", "locality": "Marine Drive, Kochi", "rating": "4.7 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Marine+Drive+Kochi", "signature": "Breezy Pure Linen Kurtas & Coastal Maxi Dresses"},
        {"store_id": "STR_682001_003", "store_name": "Lulu Mall Designer Ethnic Studio", "locality": "Edappally, Kochi", "rating": "4.8 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Lulu+Mall+Kochi", "signature": "Modern Indo-Western Kerala Bridal Gowns"},
        {"store_id": "STR_682001_004", "store_name": "Fort Kochi Boho Fashion Boutique", "locality": "Fort Kochi, Kochi", "rating": "4.8 ⭐", "maps_url": "https://www.google.com/maps/search/?api=1&query=Fort+Kochi", "signature": "Handcrafted Organic Cotton Tunics & Coastal Wear"}
    ]
}

def get_image_url(pid):
    img_num = (abs(hash(str(pid))) % 60) + 1
    return f"/catalog/catalog_{img_num}.jpg"

def format_product(item, idx, zip_code):
    pid = item["id"]
    name = item.get("name", "Regional Fashion Item").title()
    brand = item.get("brand", "PinPulse Signature").title()
    price = float(item.get("price", 1299))
    category = item.get("category", "ethnic").title()
    tags = item.get("tags", ["ethnic", "regional"])
    
    # Calculate mock hybrid scores
    vibe_score = round(0.92 + (idx * 0.003) % 0.07, 4)
    creator_score = round(0.89 + (idx * 0.004) % 0.09, 4)
    boutique_score = round(0.88 + (idx * 0.005) % 0.10, 4)
    final_score = round(0.5 * vibe_score + 0.3 * creator_score + 0.2 * boutique_score, 4)

    return {
        "id": pid,
        "name": name,
        "brand": brand,
        "category": category,
        "price": price,
        "image_url": get_image_url(pid),
        "product_url": item.get("product_url", f"https://www.myntra.com/{pid}"),
        "tags": tags,
        "vector_score": vibe_score,
        "tag_score": creator_score,
        "boost_score": 0.95,
        "price_score": 0.90,
        "final_score": final_score,
        "scoring_breakdown": {
            "layer1_personal_vibe": round(0.35 * vibe_score, 4),
            "layer2_creator_trend": round(0.30 * creator_score, 4),
            "layer3_local_boutique": round(0.20 * boutique_score, 4),
            "layer4_festivity": 0.10,
            "layer5_price": 0.05,
            "raw_values": {
                "personal_vibe_similarity": vibe_score,
                "creator_trend_match": creator_score,
                "local_boutique_match": boutique_score,
                "festivity_match": 0.95,
                "price_affinity": 0.90,
                "checkout_velocity_score": 0.88,
                "intent_score": 0.85,
                "cf_score": 0.80
            }
        },
        "reason_labels": [
            f"✨ Top Match for {ZIP_CODES[zip_code]['city']}",
            "🔥 Loved by regional creators",
            "🏬 Trending in local boutiques"
        ]
    }

db = {
    "feed": {},
    "youtube_trends": {},
    "boutique_trends": {}
}

print("Pre-computing regional recommendations per ZIP Code and Gender...")

for zip_code, info in ZIP_CODES.items():
    print(f"Processing ZIP: {zip_code} ({info['city']})...")
    
    # 1. Product Feed per Gender
    for gender, pool in [("women", women_catalog), ("men", men_catalog), ("kids", kids_catalog)]:
        # Select top 50 relevant products
        sampled = random.sample(pool, min(50, len(pool)))
        formatted = [format_product(item, idx, zip_code) for idx, item in enumerate(sampled)]
        formatted.sort(key=lambda x: x["final_score"], reverse=True)
        key = f"{zip_code}_{gender}"
        db["feed"][key] = formatted

    # 2. YouTube Creator Feed (Top 15 items)
    zip_pool = women_catalog if women_catalog else raw_catalog
    sampled_creators = random.sample(zip_pool, 15)
    channels = CREATOR_CHANNELS_MAP[zip_code]
    
    youtube_feed = []
    for idx, item in enumerate(sampled_creators):
        ch = channels[idx % len(channels)]
        pid = item["id"]
        img_url = get_image_url(pid)
        query = f"{ch} {item.get('name', 'fashion')} haul"
        
        youtube_feed.append({
            "video_id": f"creator_{zip_code}_{idx + 1}",
            "youtube_video": {
                "channel": ch,
                "title": f"HUGE {info['city']} Haul: {item.get('name', 'Ethnic Wear').title()}",
                "video_url": f"https://www.youtube.com/results?search_query={query}",
                "thumbnail_url": img_url,
                "views": f"{(15 + (idx * 12)) % 450 + 25}K views"
            },
            "matched_product": {
                "id": pid,
                "name": item.get("name", "Fashion Item").title(),
                "brand": item.get("brand", "PinPulse").title(),
                "price": float(item.get("price", 1299)),
                "image_url": img_url,
                "product_url": item.get("product_url", f"https://www.myntra.com/{pid}"),
                "clip_match_score": f"{94.5 + (idx % 5) * 0.8:.1f}%",
                "final_score": 0.95
            }
        })
    
    db["youtube_trends"][zip_code] = youtube_feed

    # 3. Local Boutique Trends
    stores = BOUTIQUE_DEFS[zip_code]
    boutique_list = []
    
    for s_idx, store in enumerate(stores):
        start = (s_idx * 3) % len(zip_pool)
        store_items = zip_pool[start:start + 4]
        
        dresses = []
        for item in store_items:
            pid = item["id"]
            dresses.append({
                "id": pid,
                "name": item.get("name", "Boutique Collection Item").title(),
                "brand": item.get("brand", store["store_name"]).title(),
                "price": float(item.get("price", 1499)),
                "image_url": get_image_url(pid),
                "product_url": item.get("product_url", f"https://www.myntra.com/{pid}"),
                "final_score": 0.94,
                "clip_match_score": "95.2%",
                "category": "Boutique Collection",
                "tags": ["ethnic", "festive", "traditional", "boutique"]
            })
        
        boutique_list.append({
            "store_id": store["store_id"],
            "store_name": store["store_name"],
            "locality": store["locality"],
            "rating": store["rating"],
            "extracted_visual_trend": store["signature"],
            "maps_url": store["maps_url"],
            "store_dresses": dresses,
            "matched_product": dresses[0]
        })
    
    db["boutique_trends"][zip_code] = {
        "zip_code": zip_code,
        "region_name": info["city"],
        "boutiques": boutique_list
    }

print("Saving precomputed DB to file...")
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2)

file_size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
print(f"Successfully generated {OUT_PATH} ({file_size_mb:.2f} MB)")
