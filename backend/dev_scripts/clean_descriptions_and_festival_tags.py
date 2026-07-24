import json
import os

CATALOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))

print(f"Loading catalog from {CATALOG_PATH}...")
cat = json.load(open(CATALOG_PATH, "r", encoding="utf-8"))

print("Scrapping LLM/Excel descriptions and standardizing catalog attributes...")

for p in cat:
    name = p.get("name", "").strip()
    category = p.get("category", "").strip()
    material = p.get("material", "").strip()
    tags = p.get("tags", [])
    
    # 1. Clean description: pure concise factual product specification
    if material and material != "cotton":
        p["description"] = f"{name} in premium {material} ({category})"
    elif category:
        p["description"] = f"{name} ({category})"
    else:
        p["description"] = name

    # 2. Tag alignment for regional dresses
    name_lower = name.lower()
    desc_lower = (p.get("description") or "").lower()
    combined_text = name_lower + " " + desc_lower + " " + " ".join(tags)

    # Shillong (793001) regional tags
    if any(k in combined_text for k in ["jainsem", "dakmanda", "khasi", "garo", "wangala", "shillong", "meghalaya"]):
        if "793001" not in p.get("zip_codes", []):
            p.setdefault("zip_codes", []).append("793001")
        for tag in ["jainsem", "dakmanda", "traditional", "shillong", "meghalaya", "ethnic"]:
            if tag not in p["tags"]:
                p["tags"].append(tag)

    # Rajasthan (302001) regional tags
    if any(k in combined_text for k in ["bandhani", "leheriya", "gota patti", "rajasthani", "jaipur", "bandhej", "marwar"]):
        if "302001" not in p.get("zip_codes", []):
            p.setdefault("zip_codes", []).append("302001")
        for tag in ["bandhani", "leheriya", "gota_patti", "rajasthani", "jaipur", "traditional", "ethnic"]:
            if tag not in p["tags"]:
                p["tags"].append(tag)

    # Odisha (752001) regional tags
    if any(k in combined_text for k in ["sambalpuri", "tussar", "ikat", "odisha", "puri", "paithani", "bomkai"]):
        if "752001" not in p.get("zip_codes", []):
            p.setdefault("zip_codes", []).append("752001")
        for tag in ["sambalpuri", "tussar_silk", "ikat", "traditional", "odisha", "puri", "ethnic"]:
            if tag not in p["tags"]:
                p["tags"].append(tag)

    # Kochi / Kerala (682001) regional tags
    if any(k in combined_text for k in ["kasavu", "mundu", "kerala", "kochi", "onam", "vishu", "thalikettu"]):
        if "682001" not in p.get("zip_codes", []):
            p.setdefault("zip_codes", []).append("682001")
        for tag in ["kasavu_weave", "mundu", "kerala", "traditional", "ethnic"]:
            if tag not in p["tags"]:
                p["tags"].append(tag)

    # Patna / Bihar (800008) regional tags
    if any(k in combined_text for k in ["bhagalpuri", "chhath", "bihar", "patna", "ilkal", "taant"]):
        if "800008" not in p.get("zip_codes", []):
            p.setdefault("zip_codes", []).append("800008")
        for tag in ["bhagalpuri_silk", "traditional", "patna", "bihar", "ethnic", "saree"]:
            if tag not in p["tags"]:
                p["tags"].append(tag)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(cat, f, indent=2)

print(f"Successfully cleaned descriptions and tags for all {len(cat)} products in local_catalog.json!")
