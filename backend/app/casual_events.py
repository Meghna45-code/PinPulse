"""
========================================================================================
PINPULSE CASUAL EVENTS DEFINITIONS & QUERIES
========================================================================================
Authoritative specifications for the 3 Casual Academic & Lifestyle Events in PinPulse:
1. School & College Farewell Gala (April 10)
2. Annual Convocation & Graduation (May 15)
3. College Admissions & Back-to-Campus (July 15)
========================================================================================
"""

CASUAL_EVENT_DEFINITIONS = {
    "farewell_gala": {
        "name": "School & College Farewell Gala",
        "date": "2026-04-10",
        "key": "apr_10",
        "description": "A highly aspirational, 'coming-of-age' evening aesthetic. For many Gen Z users, this is their first time purchasing formal evening wear or a cocktail saree. It focuses on glamour, draping, and photogenic nighttime elements.",
        "outfit_combinations": [
            "Pre-stitched ruffle Chiffon Saree + sequined halter blouse + minimal diamond jewelry",
            "Indo-Western draped Satin gown + statement drop earrings + stiletto heels",
            "Flared Georgette Maxi Dress with a thigh-high slit + metallic clutch",
            "Men: Slim-fit Navy Blue tailored suit + crisp white shirt (no tie) + leather loafers",
            "Men: Black tuxedo-style blazer + fitted black turtleneck + tailored trousers"
        ],
        "color_combinations": [
            "Midnight Blue + Metallic Silver",
            "Jet Black + Rose Gold",
            "Pastel Lilac + Crystal White",
            "Deep Emerald Green + Champagne",
            "Burgundy + Charcoal"
        ],
        "fabrics": [
            "Flowy Chiffon",
            "Satin / Silk-Satin",
            "Georgette",
            "Sequined Mesh / Net",
            "Tropical Wool Blends (for men's spring suiting)"
        ],
        "patterns": [
            "Solid high-gloss (letting fabric drape work)",
            "Sequin gradients / Ombre",
            "Tone-on-tone self-embroidery",
            "Subtle floral sequin borders",
            "Abstract metallic foil prints"
        ],
        "keywords": ["chiffon", "satin", "georgette", "sequin", "ruffle", "saree", "gown", "maxi_dress", "suit", "blazer", "tuxedo", "turtleneck", "midnight_blue", "rose_gold", "lilac", "emerald", "burgundy", "silver"]
    },
    "convocation_graduation": {
        "name": "Annual Convocation & Graduation",
        "date": "2026-05-15",
        "key": "may_15",
        "description": "A highly formal, proud, and modest daytime aesthetic. Because this involves wearing heavy graduation gowns over clothes in summer heat, underlying fashion is crisp, highly breathable, and structurally elegant.",
        "outfit_combinations": [
            "Crisp Handloom Cotton Saree (light colored) + high-neck boat blouse",
            "Straight-cut Chanderi Silk Kurta + matching cigarette pants + subtle pearl studs",
            "Tailored high-waisted linen trousers + tucked-in silk button-down blouse",
            "Men: Charcoal grey formal suit + pastel blue/pink shirt + matching tie",
            "Men: Solid formal Silk Kurta + white Churidar + structured Nehru/Modi Jacket"
        ],
        "color_combinations": [
            "Pure White + Solid Gold / Cream",
            "Ivory + Navy Blue",
            "Beige + Deep Maroon",
            "Charcoal Grey + Crisp White",
            "Pastel Peach + Off-White"
        ],
        "fabrics": [
            "Crisp Handloom Cotton",
            "Chanderi / Cotton-Silk blend",
            "Fine Linen",
            "Raw Silk (for Kurtas and Nehru jackets)",
            "Worsted Wool (for formal suits)"
        ],
        "patterns": [
            "Solid/Plain (Dominant for academic settings)",
            "Micro-checks or subtle pinstripes",
            "Subtle woven gold/silver borders on sarees",
            "Minimalist block print motifs",
            "Woven textured slub"
        ],
        "keywords": ["handloom_cotton", "chanderi", "cotton_silk", "linen", "raw_silk", "worsted_wool", "saree", "kurta", "cigarette_pants", "suit", "nehru_jacket", "modi_jacket", "white", "gold", "ivory", "navy", "charcoal", "peach"]
    },
    "admissions_back_to_campus": {
        "name": "College Admissions & Back-to-Campus",
        "date": "2026-07-15",
        "key": "jul_15",
        "description": "A monsoon-ready, utilitarian, and highly trend-driven everyday aesthetic. Merges comfort with first day impression, heavily influenced by global streetwear and weather practicality.",
        "outfit_combinations": [
            "Oversized graphic tee + baggy relaxed-fit denim jeans + chunky water-resistant sneakers",
            "Ribbed crop tank top + oversized open flannel shirt + parachute cargo pants",
            "Cropped lightweight windbreaker + wide-leg track pants + waterproof tote bag",
            "Men: Striped oversized polo shirt + straight-cut corduroy pants + retro sneakers",
            "Men: Nylon rain-proof bomber jacket + dark wash jeans + combat-style boots"
        ],
        "color_combinations": [
            "Indigo Blue Denim + Stark White",
            "Olive Drab Green + Black",
            "Mustard Yellow + Navy Blue",
            "Light Wash Blue + Pastel Pink",
            "Charcoal Grey + Neon Green accents"
        ],
        "fabrics": [
            "Heavyweight Cotton (graphic tees)",
            "Breathable / Stretch Denim",
            "Ripstop Nylon (parachute pants/windbreakers)",
            "French Terry (lightweight hoodies)",
            "Ribbed Cotton-Elastane"
        ],
        "patterns": [
            "Collegiate / Varsity typography",
            "Thick horizontal 90s stripes",
            "Color-blocking (windbreakers)",
            "Acid-wash / Faded gradients",
            "Subdued camouflage or grid prints"
        ],
        "keywords": ["heavyweight_cotton", "denim", "ripstop_nylon", "french_terry", "ribbed", "graphic_tee", "flannel", "cargo_pants", "windbreaker", "polo", "corduroy", "bomber_jacket", "varsity", "stripes", "color_block", "acid_wash", "olive", "indigo", "mustard"]
    }
}
