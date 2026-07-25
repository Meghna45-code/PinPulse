"""
========================================================================================
PINPULSE KOCHI / KERALA (PIN 682001) LOCAL EVENTS DEFINITIONS & QUERIES
========================================================================================
Authoritative specifications for the 4 Local Events in Fort Kochi, Kerala (PIN 682001):
1. Kochi-Muziris Biennale Peak (Jan 20)
2. Vishu / Malayali New Year (Apr 14)
3. Onam / Thiruvonam Harvest (Aug 27)
4. Kochi Coastal & NRI Wedding Season (Thalikettu) (Dec 27)
========================================================================================
"""

KOCHI_EVENT_DEFINITIONS = {
    "biennale_peak": {
        "name": "Kochi-Muziris Biennale Peak",
        "date": "2026-01-20",
        "key": "jan_20",
        "zip_code": "682001",
        "description": "International arts festival. Focuses on daytime-friendly, highly breathable, sustainable, and artsy/bohemian aesthetics.",
        "outfit_combinations": [
            "Loose Linen maxi dress + canvas tote bag + chunky leather sandals",
            "Oversized Khadi button-down shirt + baggy linen trousers + statement sunglasses",
            "Sleeveless crop top + flowy boho/Ikat printed skirt + oxidized silver jewelry",
            "Men: Mandarin collar linen shirt + cotton chino shorts/pants + loafers",
            "Handloom fusion tunic + wide-leg pants + cross-body sling bag"
        ],
        "color_combinations": [
            "Beige + Olive Green",
            "Indigo Blue + Off-White",
            "Rust/Terracotta + Mustard Yellow",
            "Charcoal Grey + Natural Linen (Cream)",
            "Pastel Peach + Muted Teal"
        ],
        "fabrics": [
            "Pure Linen (dominant)",
            "Khadi Cotton",
            "Hemp blends",
            "Breathable Muslin",
            "Organic Cotton"
        ],
        "patterns": [
            "Abstract / Artsy brush-stroke prints",
            "Solid earthy tones (color-blocking)",
            "Ikat weaves",
            "Minimalist stripes",
            "Asymmetrical cuts"
        ],
        "keywords": ["linen", "maxi_dress", "khadi", "linen_trousers", "crop_top", "ikat_skirt", "chinno", "tunic", "muslin", "organic_cotton", "artsy", "bohemian", "beige", "olive", "indigo", "terracotta"]
    },
    "vishu_festival": {
        "name": "Vishu / Malayali New Year",
        "date": "2026-04-14",
        "key": "apr_14",
        "zip_code": "682001",
        "description": "Malayali spring New Year. Peak summer heat preference for light, breathable Balaramapuram/Chendamangalam handloom cottons with gold Kasavu borders.",
        "outfit_combinations": [
            "Traditional Kerala Kasavu Saree + contrast green or red blouse + simple gold chain",
            "Kerala Set Mundu (two-piece drape) + traditional matching blouse",
            "Kids: Traditional Pattu Pavadai (Silk skirt and top)",
            "Men: Crisp white half-sleeve shirt + Gold-bordered Kasavu Mundu (Dhoti)",
            "Light cotton Kurti in off-white tones + matching leggings"
        ],
        "color_combinations": [
            "Pure White + Solid Gold",
            "Cream / Off-White + Emerald Green",
            "Off-White + Bright Crimson Red",
            "Golden Yellow + White"
        ],
        "fabrics": [
            "Kerala Handloom Cotton (Balaramapuram/Chendamangalam)",
            "Tissue Cotton",
            "Light Cotton-Silk blend",
            "Rayon"
        ],
        "patterns": [
            "Plain body with Gold Zari (Kasavu) borders",
            "Small woven Peacock or Mango motifs on Pallu",
            "Solid white/cream base",
            "Thin colored stripes alongside gold border"
        ],
        "keywords": ["kasavu_saree", "set_mundu", "mundu", "pattu_pavadai", "balaramapuram", "chendamangalam", "tissue_cotton", "cotton_silk", "zari", "gold_border", "peacock_motif", "mango_motif", "white", "gold", "cream", "emerald"]
    },
    "onam_harvest": {
        "name": "Onam / Thiruvonam Harvest",
        "date": "2026-08-27",
        "key": "aug_27",
        "zip_code": "682001",
        "description": "Kerala's biggest festival and peak minimalist elegance. Perfect for making Pookkalams and enjoying the grand Sadya feast.",
        "outfit_combinations": [
            "Heavy Tissue Kasavu Saree + heavily embroidered contrast blouse + gold temple jewelry (Palakkamalai/Kaasumala)",
            "Kerala Mural painted Kasavu Saree + matching gold blouse",
            "Dhavani (Half Saree) set for young women in traditional Kerala tones",
            "Men: Premium Silk Kurta or Silk Shirt + Heavy Kasavu Mundu",
            "Set Mundu with rich woven borders"
        ],
        "color_combinations": [
            "Cream/Off-White + Pure Gold (ultimate Onam palette)",
            "Gold + Deep Maroon accents",
            "Off-White + Bright Violet/Pink borders",
            "Solid Gold + Green"
        ],
        "fabrics": [
            "Premium Kerala Kasavu Handloom",
            "Tissue Silk (glossy & rich)",
            "Kanjeevaram Silk (for blouses)",
            "Pure Muslin"
        ],
        "patterns": [
            "Thick Kasavu borders (Chutti patterns)",
            "Kerala Mural art prints (Krishna/Radha/Lotus motifs)",
            "Woven temple borders (Kumbham)",
            "Coin motifs (Kaasu) woven into fabric"
        ],
        "keywords": ["tissue_kasavu", "kasavu", "set_mundu", "mundu", "mural_saree", "dhavani", "half_saree", "silk_kurta", "tissue_silk", "kanjeevaram", "chutti", "mural_art", "temple_border", "kaasu", "cream", "gold", "maroon"]
    },
    "kochi_wedding": {
        "name": "Kochi Coastal & NRI Wedding Season (Thalikettu)",
        "date": "2026-12-27",
        "key": "dec_27",
        "zip_code": "682001",
        "description": "Peak NRI wedding season in Fort Kochi. Rich, opulent, coastal-friendly aesthetic mixing Hindu, Christian, and Muslim wedding traditions.",
        "outfit_combinations": [
            "Heavy Kanjeevaram Silk Saree (Hindu brides) + Antique gold/diamond layered jewelry + Jasmine flowers",
            "Western White Lace Bridal Gown + trailing veil (Christian weddings)",
            "Bridesmaids: Matching Pastel or Rose Gold Tissue Sarees",
            "Men: Tailored 3-piece Tuxedo suits (Christian weddings)",
            "Men: Heavy Silk Kurta + Silk Mundu (Hindu/Traditional weddings)"
        ],
        "color_combinations": [
            "Rich Antique Gold + Deep Maroon",
            "Pure White + Silver (Christian Brides)",
            "Emerald Green + Antique Gold",
            "Rose Gold + Ivory",
            "Magenta + Mustard Yellow"
        ],
        "fabrics": [
            "Kanjeevaram Pure Silk",
            "Lace & Tulle (gowns)",
            "Pure Raw Silk",
            "Heavy Satin",
            "Tissue Silk"
        ],
        "patterns": [
            "Heavy Zari brocade",
            "Floral lace appliqués and beadwork",
            "Traditional Kanjeevaram checks/stripes",
            "Solid silk with heavy contrast borders",
            "Pearl and sequin embellishments"
        ],
        "keywords": ["kanjeevaram_silk", "bridal_gown", "lace", "tulle", "raw_silk", "satin", "tissue_saree", "tuxedo", "silk_kurta", "silk_mundu", "zari_brocade", "lace_applique", "antique_gold", "maroon", "white", "emerald", "rose_gold"]
    }
}
