"""
========================================================================================
PINPULSE PATNA (PIN 800008) LOCAL EVENTS DEFINITIONS & QUERIES
========================================================================================
Authoritative specifications for the 5 Local Events in Patna, Bihar (PIN 800008):
1. Makar Sankranti Harvest (Jan 14)
2. Saraswati Puja / Vasant Panchami (Feb 2)
3. Bihar Diwas / Bihar Day (Mar 22)
4. Chhath Puja Peak (Nov 15)
5. Patna Winter Wedding Season (Vivah Panchami Lagan) (Dec 10)
========================================================================================
"""

PATNA_EVENT_DEFINITIONS = {
    "makar_sankranti": {
        "name": "Makar Sankranti Harvest",
        "date": "2026-01-14",
        "key": "jan_14",
        "zip_code": "800008",
        "description": "A daytime, winter-casual aesthetic centered around kite-flying, bonfires, and community gatherings. Merges traditional ethnic wear with heavy, warm layering.",
        "outfit_combinations": [
            "Woolen-blend straight Kurti + thermal leggings + heavy woven shawl (Dushala)",
            "Mustard yellow cotton Kurta + dark denim jeans + sleeveless woolen sweater vest",
            "Casual printed Salwar Kameez + contrasting Pashmina-style dupatta",
            "Men: Khadi Kurta + comfortable Pyjama + heavy woolen Kashmiri shawl draped over one shoulder",
            "Men: Full-sleeve Henley/Turtleneck worn underneath a traditional half-sleeve Modi jacket"
        ],
        "color_combinations": [
            "Mustard Yellow + Earthy Brown",
            "Deep Rust + Charcoal Grey",
            "Warm Marigold + Navy Blue",
            "Saffron + Off-White",
            "Maroon + Beige"
        ],
        "fabrics": [
            "Heavy/Slub Cotton",
            "Wool-blends / Acrylic Wool",
            "Khadi",
            "Fleece (for hidden inner layering)",
            "Rayon (thick variants)"
        ],
        "patterns": [
            "Solid with woven textured slubs",
            "Simple Bandhani (tie-dye) dots",
            "Woven geometric borders on shawls",
            "Subtle block print motifs",
            "Plain colors (base for heavy winterwear)"
        ],
        "keywords": ["woolen", "kurti", "dushala", "mustard_yellow", "cotton_kurta", "sweater_vest", "pashmina", "dupatta", "khadi", "kashmiri_shawl", "modi_jacket", "slub_cotton", "fleece", "bandhani", "block_print", "saffron", "maroon"]
    },
    "saraswati_puja": {
        "name": "Saraswati Puja / Vasant Panchami",
        "date": "2026-02-02",
        "key": "feb_2",
        "zip_code": "800008",
        "description": "The ultimate spring transition festival, dominated entirely by students and young adults. Bright, photogenic, revolving around 'Basanti' (Spring Yellow).",
        "outfit_combinations": [
            "Bright yellow Chiffon/Georgette Saree + contrasting red sleeveless blouse + oxidized silver earrings",
            "Yellow Anarkali suit + white Churidar + sheer yellow Dupatta",
            "Chikankari Kurta in pastel yellow + white Palazzos + Juttis",
            "Men: Bright yellow/mustard Silk Kurta + crisp white Churidar",
            "Men: Light yellow short Kurti + slim-fit blue jeans + white sneakers"
        ],
        "color_combinations": [
            "Basanti Yellow + Crimson Red",
            "Pure Yellow + Crisp White",
            "Mustard + Emerald Green",
            "Pastel Lemon + Silver",
            "Bright Yellow + Hot Pink accents"
        ],
        "fabrics": [
            "Chiffon (flowy, manageable sarees)",
            "Georgette",
            "Cotton Silk",
            "Organza (stiffer, premium look)",
            "Cambric Cotton"
        ],
        "patterns": [
            "Solid Yellow (dominant)",
            "Thin Zari (gold) borders",
            "Yellow-on-yellow self-embroidery",
            "Subtle floral prints",
            "Foil print accents"
        ],
        "keywords": ["yellow_saree", "chiffon", "georgette", "anarkali", "churidar", "chikankari", "palazzo", "juttis", "silk_kurta", "cotton_silk", "organza", "basanti_yellow", "crimson_red", "zari", "foil_print", "mustard"]
    },
    "bihar_diwas": {
        "name": "Bihar Diwas / Bihar Day",
        "date": "2026-03-22",
        "key": "mar_22",
        "zip_code": "800008",
        "description": "A pride-driven, heritage aesthetic showcasing indigenous Bihari textiles, art forms (Madhubani / Mithila), and breathable handlooms.",
        "outfit_combinations": [
            "Bhagalpuri Silk (Tussar) Saree with Madhubani painted borders + elbow-length blouse",
            "Straight-cut linen Salwar suit featuring traditional Mithila art on the Dupatta",
            "Handloom cotton Kurti + straight pants + woven terracotta-colored scarf",
            "Men: Tussar silk Kurta + classic Dhoti + Madhubani-painted stole",
            "Men: Linen short shirt + tailored trousers + traditional woven Nehru Jacket"
        ],
        "color_combinations": [
            "Natural Beige/Tussar + Crimson Red",
            "Indigo Blue + Off-White",
            "Terracotta Rust + Black",
            "Mustard + Deep Brown",
            "Olive Green + Natural Linen (Cream)"
        ],
        "fabrics": [
            "Bhagalpuri Tussar Silk (crown jewel of Bihar textiles)",
            "Handloom Cotton",
            "Linen",
            "Khadi Silk",
            "Madhubani-painted Muslin"
        ],
        "patterns": [
            "Madhubani / Mithila Art (intricate folk paintings)",
            "Woven textured stripes (Bhagalpuri style)",
            "Indigo block prints",
            "Kalamkari",
            "Plain handloom finish with rich borders"
        ],
        "keywords": ["bhagalpuri_silk", "tussar_silk", "madhubani", "mithila_art", "linen", "handloom_cotton", "khadi_silk", "muslin", "salwar", "dhoti", "nehru_jacket", "kalamkari", "terracotta", "indigo", "beige"]
    },
    "chhath_puja": {
        "name": "Chhath Puja Peak",
        "date": "2026-11-15",
        "key": "nov_15",
        "zip_code": "800008",
        "description": "The most sacred, emotion-heavy festival in Bihar. Strictly traditional, highly modest, pure non-synthetic fabrics for water rituals.",
        "outfit_combinations": [
            "Pure Cotton Saree in vibrant red or yellow + matching modest blouse",
            "Heavy Banarasi Silk Saree + heavy gold jewelry (for evening home gatherings)",
            "Vermillion red Salwar suit with heavy Dupatta draping + Alta",
            "Men: Traditional unstitched Dhoti (for water rituals)",
            "Men: Heavy silk Kurta-Pyjama set (for evening Prasad distribution)"
        ],
        "color_combinations": [
            "Saffron Orange + Bright Red (definitive Arghya colors)",
            "Vibrant Yellow + Vermillion",
            "Deep Maroon + Solid Gold",
            "Rani Pink + Orange",
            "Pure White + Red Border"
        ],
        "fabrics": [
            "Pure unblended Cotton (mandatory for water ritual)",
            "Banarasi Brocade Silk",
            "Chanderi Cotton",
            "Pure Muslin",
            "Katan Silk"
        ],
        "patterns": [
            "Solid colors with thick contrasting Zari borders",
            "Heavy Brocade weaving",
            "Gota Patti borders on dupattas",
            "Paisley (Ambi) motifs",
            "Minimalist traditional checks"
        ],
        "keywords": ["pure_cotton", "banarasi_silk", "chanderi", "muslin", "katan_silk", "saree", "salwar", "dhoti", "silk_kurta", "zari_border", "brocade", "gota_patti", "paisley", "saffron", "vermillion", "maroon", "gold"]
    },
    "patna_wedding": {
        "name": "Patna Winter Wedding Season (Vivah Panchami Lagan)",
        "date": "2026-12-10",
        "key": "dec_10",
        "zip_code": "800008",
        "description": "Maximum opulence meets North Indian winter. Heavily layered, rich in texture, grand under stage lighting.",
        "outfit_combinations": [
            "Heavy velvet Lehenga + double Dupatta drape + Kundan jewelry set",
            "Heavily woven Banarasi Silk Saree + full-sleeve velvet blouse + thick embellished shawl",
            "Flared Anarkali gown with Zardosi work + Churidar + velvet Potli",
            "Men: Heavy Velvet or Brocade Sherwani + contrasting Safa (Turban) + embroidered Mojaris",
            "Men: Silk Kurta + Churidar + heavily embroidered Pashmina-style shawl"
        ],
        "color_combinations": [
            "Deep Crimson Red + Antique Gold",
            "Deep Maroon + Emerald Green",
            "Midnight Blue + Rose Gold",
            "Rich Plum/Wine + Silver",
            "Mustard Yellow + Magenta"
        ],
        "fabrics": [
            "Heavy Velvet",
            "Banarasi Katan Silk",
            "Raw Silk (structural sherwanis/lehengas)",
            "Heavy Georgette with inner lining",
            "Silk-Pashmina blends"
        ],
        "patterns": [
            "Zardosi (heavy metallic thread embroidery)",
            "All-over Zari Brocade",
            "Kundan / Stone embellishments",
            "Scalloped embroidered borders",
            "Sequin mesh work"
        ],
        "keywords": ["velvet", "banarasi_silk", "raw_silk", "georgette", "pashmina", "lehenga", "saree", "anarkali", "sherwani", "mojaris", "zardosi", "zari_brocade", "kundan", "crimson_red", "maroon", "gold", "midnight_blue"]
    }
}
