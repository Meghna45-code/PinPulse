"""
re_embed_all.py
---------------
Re-computes the 512-dim aesthetic vibe vector for every product in
local_catalog.json and pushes updated embeddings to Supabase.

Run once after any changes to get_vibe_vector() in embed_catalog.py.
"""

import os
import json
import logging
import sys
import numpy as np
from dotenv import load_dotenv

# Pull in the updated get_vibe_vector from embed_catalog
from embed_catalog import get_vibe_vector

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("re_embed_all")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))


def re_embed_all():
    # ── Load catalog ────────────────────────────────────────────────────────────
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error("local_catalog.json not found. Run import_excel.py first.")
        sys.exit(1)

    with open(LOCAL_CATALOG_FILE, "r") as f:
        catalog = json.load(f)

    logger.info(f"Loaded {len(catalog)} products from local_catalog.json.")

    # ── Re-compute embeddings ───────────────────────────────────────────────────
    for i, product in enumerate(catalog):
        tags         = product.get("tags", [])
        category_str = product.get("category", "") or ""
        # 'nature' is the DB column name for aesthetic nature
        nature_str   = product.get("nature", "") or ""
        # Also fold in description words as a lightweight proxy for aesthetics
        desc         = product.get("description", "") or ""

        new_embedding = get_vibe_vector(
            tags,
            category_str=category_str,
            aesthetic_str=f"{nature_str} {desc}"
        )
        product["embedding"] = new_embedding

        if (i + 1) % 50 == 0:
            logger.info(f"  Re-embedded {i + 1}/{len(catalog)} products...")

    logger.info(f"Re-embedding complete for all {len(catalog)} products.")

    # ── Save local catalog ──────────────────────────────────────────────────────
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=4)
    logger.info("Saved updated local_catalog.json.")

    # ── Push to Supabase in chunks ──────────────────────────────────────────────
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase credentials missing. Skipping remote update.")
        return

    try:
        from supabase import create_client
        sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        CHUNK_SIZE = 50
        chunks = [catalog[i:i + CHUNK_SIZE] for i in range(0, len(catalog), CHUNK_SIZE)]

        for idx, chunk in enumerate(chunks):
            for p in chunk:
                sb.table("products").update(
                    {"embedding": p["embedding"]}
                ).eq("id", p["id"]).execute()
            logger.info(f"  Updated chunk {idx + 1}/{len(chunks)} in Supabase.")

        logger.info(f"✅ All {len(catalog)} embeddings updated in Supabase!")

    except Exception as e:
        logger.error(f"Supabase update failed: {e}")


if __name__ == "__main__":
    re_embed_all()
