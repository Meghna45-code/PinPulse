import json
import numpy as np
import sys
import os

sys.path.append(os.path.abspath("app"))
from main import get_vibe_vector, RAW_CATALOG

v = get_vibe_vector("cottagecore")
dresses = [
    p for p in RAW_CATALOG 
    if any(k in (str(p.get("name","")) + " " + str(p.get("category",""))).lower() for k in ["dress", "maxi", "midi", "skirt", "gown", "anarkali"])
]

vecs = np.array([p.get("text_vector") or p.get("image_vector") or [0.0]*512 for p in dresses], dtype=np.float32)
sims = vecs @ np.array(v, dtype=np.float32)
top_indices = np.argsort(sims)[-5:][::-1]

print(f"TOTAL DRESSES EVALUATED: {len(dresses)}")
for rank, idx in enumerate(top_indices, 1):
    item = dresses[idx]
    score = float(sims[idx])
    name = item.get("name", "Cottagecore Dress")
    category = item.get("category", "Dress")
    price = item.get("price", 1499)
    url = item.get("product_url") or f"https://www.myntra.com/dresses/{item.get('id')}"
    image = item.get("image_url") or ""
    print(f"RANK: {rank}")
    print(f"NAME: {name}")
    print(f"CATEGORY: {category}")
    print(f"PRICE: Rs. {price}")
    print(f"SCORE: {score:.4f}")
    print(f"URL: {url}")
    print(f"IMAGE: {image}")
    print("-" * 50)
