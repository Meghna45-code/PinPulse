"""
========================================================================================
PINPULSE NATIONAL FESTIVALS DEFINITIONS & QUERIES
========================================================================================
Authoritative specifications for the 6 National Festivals in the PinPulse engine:
1. Republic Day (Jan 26)
2. Holi (Mar 3)
3. Independence Day (Aug 15)
4. Durga Puja / Dussehra (Oct 18)
5. Diwali (Nov 8)
6. Christmas / Solstice (Dec 25)
========================================================================================
"""

NATIONAL_FESTIVAL_DEFINITIONS = {
    "republic_day": {
        "name": "Republic Day",
        "date": "2026-01-26",
        "key": "jan_26",
        "description": "A formal, patriotic, and crisp winter/spring transition aesthetic honoring the Indian constitution. It heavily leans on handlooms and structured silhouettes.",
        "outfit_combinations": [
            "Crisp white Chikankari Kurta + straight cotton trousers + Tricolor chiffon dupatta",
            "Nehru/Modi Jacket + tailored linen shirt + formal trousers",
            "Handloom Cotton Saree with a subtle tricolor border + high-neck boat blouse",
            "White short Kurti + slim-fit blue jeans + oxidized silver earrings",
            "Men: Khadi Kurta + crisp white Pyjama + draped saffron stole"
        ],
        "color_combinations": [
            "Crisp White + Saffron accent",
            "Pure White + Emerald Green accent",
            "Navy Blue + Off-White",
            "Khaki + Saffron",
            "Pure White + Tricolor (Orange/White/Green)"
        ],
        "fabrics": ["Khadi Cotton", "Linen", "Chanderi", "Pure Cotton", "Handloom Silk"],
        "patterns": ["Solid/Plain (Dominant)", "Chikankari (White-on-white thread embroidery)", "Subtle woven borders", "Block print (minimalist)", "Thin vertical stripes"],
        "keywords": ["white", "saffron", "green", "tricolor", "khadi", "linen", "chanderi", "handloom", "chikankari", "nehru_jacket", "modi_jacket", "formal", "stripes", "block_print"]
    },
    "holi": {
        "name": "Holi (Festival of Colors)",
        "date": "2026-03-03",
        "key": "mar_3",
        "description": "A messy, vibrant, highly breathable, and inherently 'disposable' aesthetic. The clothing acts as a blank canvas for the colored powder (Gulal).",
        "outfit_combinations": [
            "Loose white cotton Kurta + old faded blue jeans + colorful Bandhani dupatta",
            "White sleeveless tank top + denim cut-off shorts + dark sunglasses",
            "White Chikankari maxi dress + bright multi-colored Phulkari dupatta",
            "Men: Oversized white graphic tee + comfortable track pants/shorts",
            "Simple white Salwar suit + waterproof cross-body bag"
        ],
        "color_combinations": [
            "Stark White + Neon Pink (Gulal) splashes",
            "Ivory + Bright Yellow",
            "Pure White + Indigo Blue",
            "Light Grey + Vibrant Orange",
            "Stark White + Multi-color Tie-Dye"
        ],
        "fabrics": ["Lightweight Muslin", "Cambric Cotton", "Old/Distressed Denim", "Rayon", "Terry/Jersey"],
        "patterns": ["Tie-Dye (Shibori / Leheriya)", "Solid (acting as a canvas)", "Ombre gradients", "Abstract color splashes", "Playful graphic prints"],
        "keywords": ["white", "muslin", "cotton", "denim", "tie-dye", "phulkari", "bandhani", "shibori", "leheriya", "neon_pink", "yellow", "indigo", "orange", "multi-color", "casual", "graphic_tee"]
    },
    "independence_day": {
        "name": "Independence Day",
        "date": "2026-08-15",
        "key": "aug_15",
        "description": "Similar color palette to Republic Day, but adapted for the August monsoon season. It is more casual, fluid, and fusion-oriented.",
        "outfit_combinations": [
            "Saffron A-line Kurti + white Palazzos + green draped scarf",
            "White casual shirt + dark denim + saffron/green sneakers",
            "Cotton Anarkali suit in tricolor hues + silver Jhumkas",
            "Handloom Saree in green/orange + sleeveless blouse",
            "Men: Short printed Kurta + chinos + leather sandals"
        ],
        "color_combinations": [
            "Saffron + Emerald Green",
            "Crisp White + Deep Orange",
            "Indigo Blue + White",
            "Mint Green + Coral",
            "Saffron + Navy Blue"
        ],
        "fabrics": ["Rayon", "Georgette (Monsoon-friendly/quick-dry)", "Cotton Blend", "Kota Doria (Lightweight and sheer)", "Crepe"],
        "patterns": ["Ikat", "Block print florals", "Tricolor broad stripes", "Woven geometric borders", "Bandhani dots"],
        "keywords": ["saffron", "emerald_green", "white", "orange", "indigo", "mint_green", "rayon", "georgette", "kota_doria", "crepe", "ikat", "block_print", "bandhani", "stripes", "anarkali", "kurti", "fusion"]
    },
    "durga_puja": {
        "name": "Durga Puja / Dussehra",
        "date": "2026-10-18",
        "key": "oct_18",
        "description": "A grand, culturally rich, evening-heavy aesthetic marking the beginning of the major festive season. It prioritizes heavy traditional silks and striking contrasts.",
        "outfit_combinations": [
            "Lal Paar Saree (White saree with thick red border) + puff-sleeve blouse + gold jewelry",
            "Heavy silk straight Kurta + Churidar + embellished Dupatta",
            "Embroidered Lehenga Choli + waist belt (Kamarbandh)",
            "Anarkali gown with heavy Zari work + statement choker",
            "Men: Silk Dhoti + Embroidered Panjabi (Kurta) + shawl"
        ],
        "color_combinations": [
            "Crimson Red + Pure White",
            "Deep Maroon + Gold",
            "Mustard Yellow + Deep Red",
            "Royal Blue + Silver Zari",
            "Emerald Green + Solid Gold"
        ],
        "fabrics": ["Garad Silk / Tant (Bengal handlooms)", "Banarasi Silk", "Tussar Silk", "Heavy Brocade", "Organza"],
        "patterns": ["Thick Zari borders", "Temple borders (Triangular edges)", "Woven Buti (small gold floral/polka motifs)", "Jamdani motifs", "Heavy gold embroidery"],
        "keywords": ["garad_silk", "tant", "banarasi", "tussar_silk", "brocade", "organza", "lal_paar", "saree", "anarkali", "lehenga", "dhoti", "panjabi", "zari", "temple_border", "jamdani", "embroidery", "crimson", "red", "maroon", "gold"]
    },
    "diwali": {
        "name": "Diwali (Festival of Lights)",
        "date": "2026-11-08",
        "key": "nov_8",
        "description": "Maximum glamour, opulence, and nighttime luxury. This is the biggest fashion event of the year, focusing on sparkling embellishments and rich, heavy fabrics.",
        "outfit_combinations": [
            "Heavily embellished Lehenga + sheer net Dupatta + Kundan jewelry",
            "Sequin Saree + metallic sleeveless/halter blouse",
            "Sharara suit with heavy mirror work + short Kurti",
            "Indo-western draped gown with an attached dupatta",
            "Men: Velvet Sherwani + Silk Churidar + embroidered Mojaris"
        ],
        "color_combinations": [
            "Midnight Blue + Metallic Silver",
            "Rose Gold + Emerald Green",
            "Rani Pink (Hot Pink) + Mustard Yellow",
            "Deep Wine/Burgundy + Gold",
            "Black + Metallic Gold (for evening Taash/Card parties)"
        ],
        "fabrics": ["Velvet", "Raw Silk", "Sequin-studded Georgette", "Satin", "Tissue Silk"],
        "patterns": ["Mirror work (Abhla Bharat)", "Heavy Zari / Zardosi", "Sequin gradients", "Gota Patti (Gold/Silver ribbon applique)", "Metallic Foil print"],
        "keywords": ["velvet", "raw_silk", "georgette", "satin", "tissue_silk", "lehenga", "sequin_saree", "sharara", "sherwani", "mirror_work", "zari", "zardosi", "gota_patti", "foil_print", "midnight_blue", "rose_gold", "rani_pink", "burgundy", "black", "gold"]
    },
    "christmas": {
        "name": "Christmas / Solstice",
        "date": "2026-12-25",
        "key": "dec_25",
        "description": "A cozy, winter-festive, highly westernized aesthetic. It revolves around evening parties, winter layering, and bold, festive colors.",
        "outfit_combinations": [
            "Red velvet slip dress + faux fur coat + knee-high boots",
            "Oversized knit cardigan + plaid mini skirt + sheer black tights",
            "Chunky turtleneck sweater + faux leather pants + ankle boots",
            "Sequin party dress + tailored black overcoat + stilettos",
            "Men: Tailored trench coat + dark denim + Chelsea boots"
        ],
        "color_combinations": [
            "Cherry Red + Forest Green",
            "Burgundy + Black",
            "Emerald Green + Metallic Silver",
            "Cream + Chocolate Brown",
            "Gold + Stark White"
        ],
        "fabrics": ["Heavy Wool / Cashmere", "Velvet / Velour", "Faux Leather / PU", "Tweed", "Lurex (Metallic thread knit)"],
        "patterns": ["Tartan / Plaid", "Cable Knit (Structural pattern)", "Fair Isle (Winter sweater patterns)", "Solid high-gloss (for leather/velvet)", "Houndstooth"],
        "keywords": ["heavy_wool", "cashmere", "velvet", "leather", "tweed", "lurex", "slip_dress", "cardigan", "turtleneck", "plaid_skirt", "trench_coat", "tartan", "plaid", "cable_knit", "fair_isle", "houndstooth", "cherry_red", "forest_green", "burgundy", "black", "silver"]
    }
}
