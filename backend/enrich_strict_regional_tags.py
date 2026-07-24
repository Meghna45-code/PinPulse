import json
import os

cat_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
js_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))

with open(cat_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

# Classification rules based on cultural attire keywords
def classify_product_region(p):
    name = (p.get("name") or "").lower()
    desc = (p.get("description") or "").lower()
    tags = [t.lower() for t in p.get("tags", [])]
    cat = (p.get("category") or "").lower()
    
    text = f"{name} {desc} {' '.join(tags)} {cat}"
    
    # 1. KERALA / KOCHI (682001)
    if any(k in text for k in ["kasavu", "kerala", "mundu", "ramraj", "vishu", "onam", "thalikettu", "pookalam", "kanjeevaram"]):
        return ["682001"]
        
    # 2. RAJASTHAN / JAIPUR (302001)
    if any(k in text for k in ["rajasthan", "rajasthani", "bandhani", "bandhej", "leheriya", "gota patti", "gotta patti", "chanderi", "jaisalmer", "jodhpur", "angrakha", "marwar", "pushkar", "teej"]):
        return ["302001"]
        
    # 3. ODISHA / PURI (752001)
    if any(k in text for k in ["sambalpuri", "ikat", "bomkai", "pasapalli", "odisha", "odia", "nuakhai", "raja parba", "rath yatra"]):
        return ["752001"]
        
    # 4. MEGHALAYA / SHILLONG (793001)
    if any(k in text for k in ["jainsem", "khasi", "garo", "dakmanda", "shillong", "highland", "nongkrem", "wangala", "cherry blossom", "pashmina shawl", "woollen shawl"]):
        return ["793001"]
        
    # 5. BIHAR / PATNA (800008)
    if any(k in text for k in ["bhagalpuri", "madhubani", "chhath", "bihar", "bihari", "patna", "taant", "ilkal", "basanti yellow", "sandhya arghya"]):
        return ["800008"]

    # Pan-India Neutral Basics
    return []

categorized = {
    "682001": 0,
    "302001": 0,
    "752001": 0,
    "793001": 0,
    "800008": 0,
    "pan_india": 0
}

for p in catalog:
    region = classify_product_region(p)
    if region:
        p["zip_codes"] = region
        categorized[region[0]] += 1
    else:
        # Keep existing if specific, or leave empty for pan-india
        existing = p.get("zip_codes", [])
        if existing and len(existing) == 1:
            categorized[existing[0]] += 1
        else:
            p["zip_codes"] = []
            categorized["pan_india"] += 1

print("Strict Regional Classification Summary:")
print("="*60)
print(f"Patna (800008): {categorized['800008']} items")
print(f"Kochi (682001): {categorized['682001']} items")
print(f"Puri (752001): {categorized['752001']} items")
print(f"Rajasthan (302001): {categorized['302001']} items")
print(f"Shillong (793001): {categorized['793001']} items")
print(f"Pan-India Neutral: {categorized['pan_india']} items")
print("="*60)

with open(cat_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2)

js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Saved strictly regionalized catalog to {cat_path} & {js_path}!")
