"""
========================================================================================
PINPULSE PURI / ODISHA (PIN 752001) LOCAL EVENTS DEFINITIONS & QUERIES
========================================================================================
Authoritative specifications for the 5 Local Events in Puri, Odisha (PIN 752001):
1. Makar Mela (Jan 14)
2. Pahili Raja & Raja Sankranti (Jun 14-15)
3. Puri Rath Yatra Chariot Procession (Jul 16)
4. Nuakhai Harvest Festival (Sep 15)
5. Odisha Winter Wedding Season (Margasira/Pausha Pheras) (Dec 20)
========================================================================================
"""

PURI_EVENT_DEFINITIONS = {
    "makar_mela": {
        "name": "Makar Mela",
        "date": "2026-01-14",
        "key": "jan_14",
        "zip_code": "752001",
        "description": "Coastal winter harvest festival. Mild thandi with preference for traditional heavy handlooms (Tussar Silk, Sambalpuri Ikat) and warm layering shawls.",
        "outfit_combinations": [
            "Tussar silk saree with temple border + full-sleeve blouse",
            "Sambalpuri Kurta + straight cotton pants",
            "Ethnic wear topped with warm handwoven shawl",
            "Men: Silk kurta + dhoti + draped dushala (shawl)"
        ],
        "color_combinations": [
            "Mustard Yellow + Earthy Brown",
            "Deep Orange + Maroon",
            "Off-white + Rust"
        ],
        "fabrics": [
            "Tussar Silk",
            "Heavy Handloom Cotton",
            "Woolen blends (shawls)"
        ],
        "patterns": [
            "Ikat (Sambalpuri tie-dye)",
            "Temple borders (Kumbha)",
            "Solid earthy tones"
        ],
        "keywords": ["tussar_silk", "sambalpuri", "temple_border", "kumbha", "ikat", "dushala", "shawl", "mustard_yellow", "deep_orange", "maroon", "rust", "handloom"]
    },
    "raja_sankranti": {
        "name": "Pahili Raja & Raja Sankranti",
        "date": "2026-06-15",
        "key": "jun_15",
        "zip_code": "752001",
        "description": "Unique festival celebrating womanhood and earth's fertility. Girls wear new clothes and enjoy swings (hichka). Fresh, pastel, and comfortable vibe.",
        "outfit_combinations": [
            "Pastel Sambalpuri cotton saree + contrasting blouse",
            "Flared cotton Anarkali or Kurti + loose palazzos (comfortable for swings)",
            "Bright new floral printed dresses for girls",
            "Men: Casual pastel short kurtas + jeans"
        ],
        "color_combinations": [
            "Pastel Pink + Mint Green",
            "Sky Blue + Crisp White",
            "Bright Yellow + Orange"
        ],
        "fabrics": [
            "Sambalpuri Cotton",
            "Mulmul (Muslin)",
            "Breathable Linen"
        ],
        "patterns": [
            "Floral block prints",
            "Traditional Ikat butti (small dots/motifs)",
            "Plain body with contrast border"
        ],
        "keywords": ["sambalpuri_cotton", "mulmul", "muslin", "linen", "anarkali", "kurti", "palazzo", "floral_block", "ikat_butti", "pastel_pink", "mint_green", "sky_blue", "yellow"]
    },
    "rath_yatra": {
        "name": "Puri Rath Yatra Chariot Procession",
        "date": "2026-07-16",
        "key": "jul_16",
        "zip_code": "752001",
        "description": "Puri's grandest festival. Considering crowd and July humidity, clothing is ultra-breathable, devoted to Lord Jagannath's iconic colors (Yellow, Saffron, White, Red).",
        "outfit_combinations": [
            "Yellow or Saffron Sambalpuri cotton saree + simple sleeveless blouse",
            "Men: Pure white cotton Kurta + Pyjama",
            "Streetwear Bhakti: Oversized Jagannath graphic t-shirt + cargo pants (Gen Z)",
            "Casual t-shirt + Devotional printed stoles (Gamocha)"
        ],
        "color_combinations": [
            "Bright Yellow + Saffron (iconic Jagannath colors)",
            "Pure White + Red",
            "Deep Crimson + Black"
        ],
        "fabrics": [
            "Pure breathable Cotton (ideal for humidity)",
            "Lightweight Linen",
            "Khandua Pata (rituals/VIPs)"
        ],
        "patterns": [
            "Lord Jagannath face motifs",
            "Khandua text weaves (Geeta Govinda lines)",
            "Solid devotional colors"
        ],
        "keywords": ["sambalpuri", "cotton", "linen", "khandua_pata", "saree", "kurta", "jagannath_graphic", "gamocha", "bright_yellow", "saffron", "white", "red", "devotional"]
    },
    "nuakhai": {
        "name": "Nuakhai Harvest Festival",
        "date": "2026-09-15",
        "key": "sep_15",
        "zip_code": "752001",
        "description": "Odisha's major harvest festival showcasing Western Odisha handlooms (Pasapali, Bomkai).",
        "outfit_combinations": [
            "Pasapali (chessboard print) handloom saree + matching blouse",
            "Bomkai cotton suit + heavy woven dupatta",
            "Ethnic fusion kurtis + oxidized silver jewelry",
            "Men: Traditional Kurta pyjama + Sambalpuri jacket"
        ],
        "color_combinations": [
            "Red + Black + White (classic Pasapali)",
            "Turmeric Yellow + Deep Green",
            "Maroon + Gold"
        ],
        "fabrics": [
            "Western Odisha Handlooms",
            "Bomkai Cotton",
            "Rayon"
        ],
        "patterns": [
            "Pasapali (Checkerboard pattern)",
            "Traditional nature-inspired Ikat weaves",
            "Contrast Pallu geometric designs"
        ],
        "keywords": ["pasapali", "bomkai", "handloom", "saree", "cotton_suit", "dupatta", "kurti", "sambalpuri_jacket", "checkerboard", "ikat", "red", "black", "yellow", "green", "maroon"]
    },
    "puri_wedding": {
        "name": "Odisha Winter Wedding Season (Margasira/Pausha Pheras)",
        "date": "2026-12-20",
        "key": "dec_20",
        "zip_code": "752001",
        "description": "Pleasant winter wedding season in Puri. Royal heritage and heavy silk (Khandua Pata, Tussar Silk).",
        "outfit_combinations": [
            "Heavy Khandua Pata or Tussar Silk Saree + traditional gold temple jewelry",
            "Rich embroidered Lehenga choli (modern brides/guests)",
            "Men: Ceremonial Velvet Sherwani + silk dhoti",
            "Heavy Banarasi fusion suits"
        ],
        "color_combinations": [
            "Crimson Red + Pure Gold",
            "Deep Maroon + Emerald Green",
            "Royal Blue + Silver Zari"
        ],
        "fabrics": [
            "Khandua Silk",
            "Premium Tussar Silk",
            "Silk Velvet (Sherwani)",
            "Heavy Brocade"
        ],
        "patterns": [
            "Heavy Zari work",
            "Mythological woven motifs (Odisha tradition)",
            "Intricate Gota/Zardosi embroidery"
        ],
        "keywords": ["khandua_pata", "tussar_silk", "velvet", "brocade", "saree", "lehenga", "sherwani", "dhoti", "zari", "zardosi", "temple_jewelry", "crimson_red", "maroon", "royal_blue", "gold"]
    }
}
