"""
========================================================================================
PINPULSE JAIPUR / RAJASTHAN (PIN 302001) LOCAL EVENTS DEFINITIONS & QUERIES
========================================================================================
Authoritative specifications for the 8 Local Events in Jaipur, Rajasthan (PIN 302001):
1. Jaipur International Kite Festival (Jan 03 & 14)
2. Jaisalmer Desert Festival (Feb 15)
3. Jaipur Elephant & Holi Festival (Mar 20)
4. Royal Gangaur Festival Procession (Apr 04)
5. Swarn Teej Festival Jaipur (Aug 12)
6. Marwar Folk Music Festival (Oct 20)
7. Pushkar Camel Fair & Cultural Night (Nov 18)
8. Jaipur Royal Rajwara Wedding Season (Dev Uthan Lagan - Dec 15)
========================================================================================
"""

JAIPUR_EVENT_DEFINITIONS = {
    "kite_festival": {
        "name": "Jaipur International Kite Festival",
        "date": "2026-01-14",
        "key": "jan_14",
        "zip_code": "302001",
        "description": "A daytime, rooftop-heavy, winter-casual aesthetic requiring mobility for kite-flying while retaining a bright, festive vibe against chilly January winds.",
        "outfit_combinations": [
            "Mustard yellow block-print flared Anarkali + cotton leggings + woolen shawl",
            "Short Bagru-print Kurti + distressed blue denim + oxidized silver Jhumkas",
            "Straight cotton Kurta + solid Palazzos + contrasting Phulkari/woven dupatta",
            "Men: Short cotton Kurta + slim jeans + sleeveless woolen Nehru/Bandi jacket",
            "Men: Solid white Kurta-Pyjama + bright yellow/orange draped stole"
        ],
        "color_combinations": [
            "Marigold Yellow + Sky Blue",
            "Tangerine + Crisp White",
            "Turmeric Yellow + Rust",
            "Cobalt Blue + Bright Orange",
            "Crimson + Mustard"
        ],
        "fabrics": [
            "Medium-weight Cotton",
            "Khadi",
            "Denim",
            "Rayon",
            "Acrylic-Wool blends"
        ],
        "patterns": [
            "Sanganeri Block Print",
            "Subtle Leheriya",
            "Polka dots",
            "Solid brights with woven borders",
            "Geometric Ikat"
        ],
        "keywords": ["sanganeri", "block_print", "anarkali", "bagru", "kurti", "jhumkas", "palazzo", "phulkari", "bandi_jacket", "nehru_jacket", "leheriya", "mustard_yellow", "tangerine", "cobalt_blue", "khadi", "denim"]
    },
    "desert_festival": {
        "name": "Jaisalmer Desert Festival",
        "date": "2026-02-15",
        "key": "feb_15",
        "zip_code": "302001",
        "description": "A highly ethnic, folk-inspired, 'Banjara' (nomadic) aesthetic emphasizing heavy textures and striking desert contrasts.",
        "outfit_combinations": [
            "Koti (Mirror-work ethnic jacket) + plain black or white Kurti + flared skirt",
            "Heavy Bandhani (tie-dye) Maxi dress + oxidized silver choker (Banjara style)",
            "Flared cotton Lehenga (Ghagra) + contrasting crop top (Choli) + draped Odhni",
            "Men: Pathani suit + brightly colored, tightly wrapped Safa (Turban)",
            "Men: Asymmetric hem Kurta + Jodhpuri trousers + leather Mojaris"
        ],
        "color_combinations": [
            "Deep Magenta + Indigo Blue",
            "Camel Brown + Metallic Mirror-Silver",
            "Deep Rust + Black",
            "Teal + Hot Pink",
            "Blood Red + Ochre"
        ],
        "fabrics": [
            "Thick Handloom Cotton",
            "Mashru Silk (Silk-cotton blend)",
            "Gamcha Cotton",
            "Georgette",
            "Khadi Silk"
        ],
        "patterns": [
            "Bandhani / Bandhej",
            "Abhla Bharat (Heavy Mirror-work)",
            "Patchwork",
            "Thread-tassel embellishments",
            "Ajrakh"
        ],
        "keywords": ["mirror_work", "koti", "bandhani", "bandhej", "banjara", "ghagra", "choli", "odhni", "pathani", "safa", "jodhpuri", "mojaris", "mashru_silk", "ajrakh", "magenta", "indigo", "teal", "rust"]
    },
    "elephant_holi": {
        "name": "Jaipur Elephant & Holi Festival",
        "date": "2026-03-20",
        "key": "mar_20",
        "zip_code": "302001",
        "description": "A regal yet playful springtime aesthetic infused with royal Rajasthani trims and a focus on premium, breathable cottons.",
        "outfit_combinations": [
            "White Mulmul (Muslin) Anarkali with silver Gota trim + Rainbow Leheriya Dupatta",
            "Sleeveless white Kurti + flared white Palazzos + waterproof crossbody bag",
            "Flowy Tiered Maxi Dress in pastel tones + statement sunglasses",
            "Men: White Chikankari Kurta + comfortable white trousers + Bandhani stole",
            "Men: Crisp linen short-sleeve shirt + cotton shorts"
        ],
        "color_combinations": [
            "Pure White + Fuchsia Pink (Gulal)",
            "Ivory + Rainbow (Multi-color tie-dye)",
            "Saffron + Magenta",
            "Lemon Yellow + Bright Green",
            "Pearl White + Silver Gota accents"
        ],
        "fabrics": [
            "Mulmul (Ultra-fine Muslin Cotton)",
            "Kota Doria (Lightweight, sheer grid cotton)",
            "Chiffon",
            "Fine Linen",
            "Cambric Cotton"
        ],
        "patterns": [
            "Leheriya (Diagonal wave tie-dye)",
            "Minimal Gota Patti",
            "Solid white (acting as canvas)",
            "Abstract color-bleed",
            "Floral block prints"
        ],
        "keywords": ["mulmul", "muslin", "kota_doria", "chiffon", "linen", "anarkali", "gota_patti", "leheriya", "chikankari", "bandhani", "fuchsia", "saffron", "magenta", "white", "silver"]
    },
    "gangaur_festival": {
        "name": "Royal Gangaur Festival Procession",
        "date": "2026-04-04",
        "key": "apr_04",
        "zip_code": "302001",
        "description": "A deeply traditional women's festival honoring Goddess Parvati. Ornate daytime festival requiring heavy jewelry and classic Rajputi silhouettes.",
        "outfit_combinations": [
            "Heavy Gota Patti Georgette Lehenga + matching Choli + Kundan jewelry",
            "Rajputi Poshak (traditional 4-piece dress: Kanchali, Kurti, Ghagra, Odhni)",
            "Red Bandhej Saree with heavy Zari borders + elbow-length gold blouse",
            "Sharara suit with heavy Marodi embroidery + Maang Tikka",
            "Men: Royal Jodhpuri Suit (Bandhgala) + tailored trousers + pocket square"
        ],
        "color_combinations": [
            "Vermilion Red + Pure Gold",
            "Rani Pink (Hot Pink) + Silver",
            "Deep Orange + Gold",
            "Emerald Green + Magenta",
            "Turmeric Yellow + Red"
        ],
        "fabrics": [
            "Pure Georgette",
            "Crepe Silk",
            "Chanderi",
            "Modal Silk",
            "Satin"
        ],
        "patterns": [
            "Heavy Gota Patti",
            "Bandhej",
            "Mothra (Criss-cross checked tie-dye)",
            "Zari borders",
            "Foil Stamping"
        ],
        "keywords": ["gota_patti", "rajputi_poshak", "kanchali", "ghagra", "odhni", "bandhej", "sharara", "marodi_embroidery", "bandhgala", "jodhpuri", "georgette", "crepe_silk", "chanderi", "mothra", "vermilion", "rani_pink", "gold"]
    },
    "teej_festival": {
        "name": "Swarn Teej Festival Jaipur",
        "date": "2026-08-12",
        "key": "aug_12",
        "zip_code": "302001",
        "description": "A monsoon festival celebrating rains, nature, and marital bliss. Exclusively dominated by shades of Green (Sawan) and rain-inspired patterns.",
        "outfit_combinations": [
            "Emerald Green Leheriya Saree + contrasting red/gold blouse + green glass bangles",
            "Green Silk Lehenga + Gota Patti Dupatta draped Gujarati style",
            "Flared green Anarkali suit + Churidar + Polki earrings",
            "Men: Mint or Emerald Green Kurta + crisp white Pyjama",
            "Half-Saree (Langa Voni) in green and yellow tones"
        ],
        "color_combinations": [
            "Emerald Green + Gold (dominant Teej palette)",
            "Mint Green + Silver",
            "Parrot Green + Rani Pink",
            "Deep Forest Green + Mustard Yellow",
            "Teal + Magenta"
        ],
        "fabrics": [
            "Georgette (quick-drying, fluid)",
            "Organza",
            "Silk Blend",
            "Chanderi Cotton",
            "Chiffon"
        ],
        "patterns": [
            "Leheriya (representing flow of rain)",
            "Gota Patti",
            "Floral Jaal (all-over vine patterns)",
            "Chevron (Zig-zag)",
            "Solid green body with heavy borders"
        ],
        "keywords": ["emerald_green", "leheriya", "saree", "silk_lehenga", "gota_patti", "anarkali", "churidar", "green_kurta", "langa_voni", "georgette", "organza", "chanderi", "mint_green", "parrot_green", "gold"]
    },
    "marwar_festival": {
        "name": "Marwar Folk Music Festival",
        "date": "2026-10-20",
        "key": "oct_20",
        "zip_code": "302001",
        "description": "A bohemian, Indo-western fusion aesthetic merging global festival styling with indigenous Indian textiles.",
        "outfit_combinations": [
            "Draped Dhoti pants + heavily embroidered crop top + sheer cape",
            "Indigo block-print Maxi dress + oxidized silver coin necklace + leather boots",
            "Angrakha-style short tunic + ripped mom jeans + silver bangles",
            "Men: Asymmetric overlapping Kurta + dark chinos + Chelsea boots",
            "Men: Indigo Bagru-print short shirt + layered beaded necklaces + denim"
        ],
        "color_combinations": [
            "Indigo Blue + Mustard Yellow",
            "Earthy Rust + Turquoise",
            "Terracotta + Olive Green",
            "Deep Maroon + Black",
            "Mud Brown + Antique Silver"
        ],
        "fabrics": [
            "Indigo-dyed Cotton",
            "Khadi",
            "Linen",
            "Tussar Silk",
            "Suede"
        ],
        "patterns": [
            "Bagru Print",
            "Ajrakh",
            "Coin/Cowrie shell trims",
            "Geometric Block Prints",
            "Distressed/Frayed edges"
        ],
        "keywords": ["dhoti_pants", "bagru_print", "indigo", "maxi_dress", "angrakha", "ajrakh", "khadi", "linen", "tussar_silk", "suede", "mustard_yellow", "terracotta", "turquoise", "maroon", "boho", "fusion"]
    },
    "pushkar_fair": {
        "name": "Pushkar Camel Fair & Cultural Night",
        "date": "2026-11-18",
        "key": "nov_18",
        "zip_code": "302001",
        "description": "Rustic, nomadic, and geared for cold desert nights. Blends heavy winter layering with vibrant, tribal Rajasthan art.",
        "outfit_combinations": [
            "Long handloom Angrakha Kurta + thick cotton palazzos + heavy woven shawl",
            "Gamcha-print layered dress + denim jacket + oxidized choker",
            "Woolen Kurti + straight pants + Kutch-embroidered heavy Dupatta",
            "Men: Khadi Kurta + structured Velvet Bandhgala jacket + Jodhpuri pants",
            "Men: Heavy cotton Kurta + draped Pashmina shawl + leather sandals"
        ],
        "color_combinations": [
            "Camel/Sand + Deep Maroon",
            "Ochre + Indigo",
            "Crimson + Charcoal Grey",
            "Deep Turquoise + Rust",
            "Magenta + Black"
        ],
        "fabrics": [
            "Thick Handloom Cotton",
            "Raw Silk",
            "Wool-blends (heavy shawls)",
            "Velvet (Bandi jackets)",
            "Mashru"
        ],
        "patterns": [
            "Thread Embroidery (Phulkari/Kutch)",
            "Sanganeri floral motifs",
            "Tribal / Nomadic motifs",
            "Woven textured slub",
            "Patchwork (Appliqué)"
        ],
        "keywords": ["angrakha", "palazzo", "shawl", "gamcha", "kutch_embroidery", "bandhgala", "jodhpuri", "pashmina", "raw_silk", "velvet", "mashru", "phulkari", "sanganeri", "ochre", "crimson", "turquoise", "maroon"]
    },
    "jaipur_wedding": {
        "name": "Jaipur Royal Rajwara Wedding Season (Dev Uthan Lagan)",
        "date": "2026-12-15",
        "key": "dec_15",
        "zip_code": "302001",
        "description": "Absolute maximum opulence ('Maharaja/Maharani' aesthetic). Combines freezing desert winter with heavy Kundan jewelry, rich velvets, and 3D metallic embroidery.",
        "outfit_combinations": [
            "Heavy Silk Velvet Lehenga + double Dupatta drape + heavy Kundan/Polki Choker",
            "Pure Rajputi Poshak in Silk + Borla + Aad (neckpiece)",
            "Banarasi Brocade Silk Saree + full-sleeve velvet blouse",
            "Men: Heavy Velvet or Brocade Sherwani with Zardosi work + embroidered Safa + Kalgi",
            "Men: Silk Achkan + Churidar + embroidered Mojaris"
        ],
        "color_combinations": [
            "Deep Maroon + Antique Gold",
            "Navy Blue + Silver Zari",
            "Emerald Green + Rose Gold",
            "Royal Purple + Solid Gold",
            "Ivory + Pastel Meenakari/Kundan colors"
        ],
        "fabrics": [
            "Silk Velvet (dominant for Jaipur winter weddings)",
            "Pure Raw Silk",
            "Banarasi Brocade",
            "Heavy Net",
            "Pure Tissue Silk"
        ],
        "patterns": [
            "Zardosi (3D metallic wire embroidery)",
            "Dabka and Marodi work",
            "Heavy Gota Patti Jaal",
            "Kundan / Stone pasting"
        ],
        "keywords": ["silk_velvet", "raw_silk", "banarasi_brocade", "tissue_silk", "velvet_lehenga", "rajputi_poshak", "sherwani", "achkan", "safa", "mojaris", "zardosi", "dabka", "marodi", "gota_patti", "kundan", "maroon", "gold", "navy", "emerald", "purple"]
    }
}
