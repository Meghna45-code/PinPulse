import os
import json
import random
import logging
import numpy as np
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("embed_catalog")

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Target image directory in frontend public assets
CATALOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "catalog"))
LOCAL_CATALOG_FILE = os.path.join(os.path.dirname(__file__), "local_catalog.json")

# Define the 60 product catalog items mapped with Zip Codes & Wedding/Event tags
# zip_codes: empty list [] means globally available, ['752001'] means local to Odisha (micro-creators)
PRODUCTS_SOURCE = [
    # === REGIONAL WEDDING & CEREMONIAL ===
    
    # --- Patna Wedding (15 Items) ---
    {
        "id": 1,
        "name": "Crimson Banarasi Silk Saree",
        "description": "Premium heavy pure silk Banarasi saree with detailed gold zari brocade, curated for wedding pheras.",
        "category": "festive",
        "tags": ["ethnic", "festive", "silk", "zari", "traditional", "saree", "heavy_silk", "traditional_embroidery", "ceremonial", "crimson", "gold"],
        "zip_codes": [],
        "base_color": (139, 0, 0), "accent_color": (218, 165, 32)
    },
    {
        "id": 2,
        "name": "Maroon Designer Sherwani",
        "description": "Luxurious groom sherwani in heavy raw silk, detailed with hand-stitched traditional embroidery.",
        "category": "festive",
        "tags": ["ethnic", "festive", "silk", "sherwani", "traditional", "men", "heavy_silk", "traditional_embroidery", "ceremonial", "maroon", "gold"],
        "zip_codes": [],
        "base_color": (80, 0, 0), "accent_color": (218, 165, 32)
    },
    {
        "id": 3,
        "name": "Saffron Matripooja Kurta",
        "description": "Comfortable pure cotton short kurta, perfect for morning Haldi and Matripooja rituals.",
        "category": "casual",
        "tags": ["casual", "summer", "cotton", "breathable", "kurta", "yellow", "saffron", "ethnic"],
        "zip_codes": [],
        "base_color": (255, 140, 0), "accent_color": (255, 255, 255)
    },
    {
        "id": 4,
        "name": "Yellow Haldi Salwar Suit",
        "description": "Lightweight cotton printed salwar suit in bright turmeric yellow for pre-wedding ceremonies.",
        "category": "casual",
        "tags": ["casual", "summer", "cotton", "breathable", "suit", "yellow", "ethnic"],
        "zip_codes": [],
        "base_color": (255, 215, 0), "accent_color": (255, 255, 255)
    },
    {
        "id": 5,
        "name": "Fuchsia Mooh Dikhayi Saree",
        "description": "Premium fuchsia pink georgette saree with fuchsia/gold border, ideal for post-wedding Vidaai.",
        "category": "festive",
        "tags": ["ethnic", "festive", "saree", "magenta", "fuchsia", "gold"],
        "zip_codes": [],
        "base_color": (255, 0, 127), "accent_color": (218, 165, 32)
    },
    {
        "id": 6,
        "name": "Bhagalpuri Silk Saree",
        "description": "Traditional handloom Bhagalpuri silk saree, celebrating Bihar Diwas regional heritage.",
        "category": "festive",
        "tags": ["ethnic", "festive", "silk", "saree", "traditional", "bhagalpuri-silk", "patna"],
        "zip_codes": [],
        "base_color": (128, 0, 0), "accent_color": (245, 222, 179)
    },
    {
        "id": 7,
        "name": "Chhath Puja Saffron Dhoti Set",
        "description": "Pure cotton saffron dhoti and white kurta set for performing Sandhya and Usha Arghya.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "dhoti", "saffron", "yellow", "white", "patna", "chhath-puja"],
        "zip_codes": [],
        "base_color": (255, 140, 0), "accent_color": (255, 255, 255)
    },
    {
        "id": 8,
        "name": "Patna Sahib Prakash Parv Kurta",
        "description": "High-quality white cotton-silk kurta set, formal and respectful for Prakash Parv celebrations.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "white", "blue", "saffron", "patna"],
        "zip_codes": [],
        "base_color": (245, 245, 240), "accent_color": (0, 0, 128)
    },
    {
        "id": 9,
        "name": "Saraswati Puja Yellow Saree",
        "description": "Bright yellow organza saree with minimal border, customized for Vasant Panchami college wear.",
        "category": "festive",
        "tags": ["ethnic", "festive", "saree", "yellow", "patna"],
        "zip_codes": [],
        "base_color": (255, 223, 0), "accent_color": (255, 255, 255)
    },
    {
        "id": 10,
        "name": "Shravani Mela Saffron T-Shirt",
        "description": "Vibrant saffron cotton printed casual tee for Kanwar Yatra pilgrims transiting Patna.",
        "category": "casual",
        "tags": ["casual", "cotton", "breathable", "saffron"],
        "zip_codes": [],
        "base_color": (255, 99, 71), "accent_color": (255, 255, 255)
    },
    {
        "id": 11,
        "name": "Tricolour Fusion Nehru Jacket",
        "description": "Vibrant raw-silk Nehru waistcoat in saffron and white trims, paired with green kurta for national days.",
        "category": "festive",
        "tags": ["ethnic", "festive", "kurta", "nehru-jacket", "patna", "saffron", "white", "green", "formal"],
        "zip_codes": [],
        "base_color": (0, 128, 80), "accent_color": (255, 255, 255)
    },
    {
        "id": 12,
        "name": "Patna Book Fair Smart Blazer",
        "description": "Smart casual cotton blazer, lightweight and stylish for walking campus or Book Fairs.",
        "category": "streetwear",
        "tags": ["streetwear", "casual", "jacket", "smart_casual", "patna", "blazer", "formal"],
        "zip_codes": [],
        "base_color": (85, 107, 47), "accent_color": (200, 200, 200)
    },
    {
        "id": 13,
        "name": "Jitiya Vrat Red Saree",
        "description": "Crimson red cotton-georgette saree, traditionally worn by mothers during Jitiya fasting.",
        "category": "festive",
        "tags": ["ethnic", "festive", "saree", "red", "maroon", "traditional"],
        "zip_codes": [],
        "base_color": (165, 42, 42), "accent_color": (255, 255, 255)
    },
    {
        "id": 14,
        "name": "Patna Film Fest Glam Kurta",
        "description": "Designer contemporary georgette kurta in charcoal grey, ideal for movie premieres.",
        "category": "festive",
        "tags": ["ethnic", "festive", "kurta", "glam", "patna"],
        "zip_codes": [],
        "base_color": (50, 50, 50), "accent_color": (200, 200, 200)
    },
    {
        "id": 15,
        "name": "Embellished Wedding Chunri",
        "description": "Bright red heavy bridal dupatta/chunri with golden gota-patti and traditional embroidery.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional_embroidery", "ceremonial", "red", "gold"],
        "zip_codes": [],
        "base_color": (200, 0, 0), "accent_color": (218, 165, 32)
    },

    # --- Kochi Wedding (15 Items) ---
    {
        "id": 16,
        "name": "Premium Kasavu Wedding Saree",
        "description": "Traditional Kerala handloom off-white cotton saree woven with thick gold zari border.",
        "category": "festive",
        "tags": ["ethnic", "festive", "saree", "kasavu_weave", "off-white", "cream", "gold", "ceremonial"],
        "zip_codes": [],
        "base_color": (250, 245, 230), "accent_color": (218, 165, 32)
    },
    {
        "id": 17,
        "name": "Kasavu Zari Mundu Set",
        "description": "Pure cotton traditional Kerala double mundu paired with a cream silk shirt for weddings.",
        "category": "festive",
        "tags": ["ethnic", "festive", "mundu", "kasavu_weave", "white", "cream", "gold", "ceremonial", "men"],
        "zip_codes": [],
        "base_color": (255, 253, 245), "accent_color": (218, 165, 32)
    },
    {
        "id": 18,
        "name": "Engagement Pastel Jainsem",
        "description": "Elegant lavender and silver georgette Jainsem, a crossover fusion design for modern engagements.",
        "category": "festive",
        "tags": ["ethnic", "festive", "semi-ethnic", "mint", "peach", "lavender", "pastel"],
        "zip_codes": [],
        "base_color": (230, 210, 250), "accent_color": (200, 200, 255)
    },
    {
        "id": 19,
        "name": "Designer Reception Gown",
        "description": "Stunning royal blue contemporary georgette gown, sequined for post-wedding receptions.",
        "category": "festive",
        "tags": ["ethnic", "festive", "contemporary_fusion", "royal-blue", "wine", "black", "silver"],
        "zip_codes": [],
        "base_color": (0, 35, 102), "accent_color": (192, 192, 192)
    },
    {
        "id": 20,
        "name": "Kochi Biennale Linen Shirt",
        "description": "Artsy beige relaxed-fit organic linen shirt, breathable for contemporary art gallery walks.",
        "category": "casual",
        "tags": ["casual", "summer", "linen", "breathable", "artsy", "bohemian", "sustainable", "modern"],
        "zip_codes": [],
        "base_color": (240, 235, 220), "accent_color": (100, 100, 100)
    },
    {
        "id": 21,
        "name": "Makaravilakku Black Mundu",
        "description": "Strict ritualistic black cotton mundu and matching upper shawl for Sabarimala observers.",
        "category": "festive",
        "tags": ["ethnic", "traditional", "black", "saffron", "mundu", "dhoti"],
        "zip_codes": [],
        "base_color": (10, 10, 10), "accent_color": (255, 255, 255)
    },
    {
        "id": 22,
        "name": "Chandanakudam Embroidered Kurta",
        "description": "Islamic festive wear: emerald green pathani suit with modest ethnic collar embroidery.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "Islamic", "modest", "embroidered"],
        "zip_codes": [],
        "base_color": (0, 80, 40), "accent_color": (218, 165, 32)
    },
    {
        "id": 23,
        "name": "Coastal Boat Race Casuals",
        "description": "Ocean blue extra-breathable cotton tank and shorts set, ideal for hot humid boat races.",
        "category": "casual",
        "tags": ["casual", "summer", "cotton", "breathable", "coastal"],
        "zip_codes": [],
        "base_color": (30, 144, 255), "accent_color": (255, 255, 255)
    },
    {
        "id": 24,
        "name": "Cochin Carnival Party Tee",
        "description": "Vibrant graphic streetwear tee with a bohemian print celebrating Fort Kochi beach parties.",
        "category": "streetwear",
        "tags": ["streetwear", "casual", "vibrant", "party", "bohemian", "modern"],
        "zip_codes": [],
        "base_color": (255, 20, 147), "accent_color": (0, 255, 255)
    },
    {
        "id": 25,
        "name": "Vishu Golden Kasavu Kurti",
        "description": "Contemporary cotton kurti with traditional Kerala gold border highlights, ideal for Vishu.",
        "category": "festive",
        "tags": ["ethnic", "festive", "yellow", "gold", "cream", "kasavu_weave"],
        "zip_codes": [],
        "base_color": (255, 250, 240), "accent_color": (218, 165, 32)
    },
    {
        "id": 26,
        "name": "Easter Sunday Modest Dress",
        "description": "Modest and elegant sky-blue A-line midi dress, premium church formal wear.",
        "category": "festive",
        "tags": ["ethnic", "festive", "modest", "formal", "premium", "pastel"],
        "zip_codes": [],
        "base_color": (135, 206, 250), "accent_color": (255, 255, 255)
    },
    {
        "id": 27,
        "name": "Rosh Hashanah Modest Suit",
        "description": "Subtle premium off-white linen ethnic salwar suit, perfect for Jew Town Synagogue services.",
        "category": "festive",
        "tags": ["ethnic", "festive", "subtle", "modest", "premium", "elegant"],
        "zip_codes": [],
        "base_color": (245, 245, 240), "accent_color": (200, 200, 200)
    },
    {
        "id": 28,
        "name": "Gold Border Kasavu Dupatta",
        "description": "Kerala handloom off-white cotton dupatta detailed with fine golden thread weaves.",
        "category": "festive",
        "tags": ["ethnic", "festive", "kasavu_weave", "gold"],
        "zip_codes": [],
        "base_color": (255, 255, 250), "accent_color": (218, 165, 32)
    },
    {
        "id": 29,
        "name": "Contemporary Designer Tuxedo",
        "description": "Sleek wine-red contemporary tuxedo jacket with metallic silver buttons for receptions.",
        "category": "streetwear",
        "tags": ["streetwear", "contemporary_fusion", "wine", "silver", "men"],
        "zip_codes": [],
        "base_color": (115, 10, 30), "accent_color": (192, 192, 192)
    },
    {
        "id": 30,
        "name": "Artsy Asymmetrical Kurta",
        "description": "Asymmetric indigo dyed cotton kurta, designed for art gallery previews in Kochi.",
        "category": "casual",
        "tags": ["casual", "cotton", "artsy", "bohemian"],
        "zip_codes": [],
        "base_color": (0, 0, 139), "accent_color": (255, 255, 255)
    },

    # --- Odisha Festival & Local Boutique Handlooms (15 Items) ---
    # locked strictly to zip code 752001 (Odisha) to demonstrate local handloom support
    {
        "id": 31,
        "name": "[Sambalpuri Weaves] Silk Saree",
        "description": "Premium hand-woven Sambalpuri silk saree with traditional ikat border and shell work, ideal for Rath Yatra.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "silk", "saree", "sambalpuri", "ikat", "handloom"],
        "zip_codes": ["752001"],
        "base_color": (139, 0, 0), "accent_color": (218, 165, 32)
    },
    {
        "id": 32,
        "name": "[Boutique Katki] Ikat Kurta",
        "description": "Authentic hand-woven cotton Ikat kurta for men, comfortable for festive temple walks.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "kurta", "cotton", "ikat", "handloom", "men"],
        "zip_codes": ["752001"],
        "base_color": (0, 100, 80), "accent_color": (255, 255, 255)
    },
    {
        "id": 33,
        "name": "[Puri Handlooms] Tussar Silk Saree",
        "description": "Elegant traditional Tussar silk saree in golden beige, crafted by Gopalpur weavers.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "silk", "saree", "tussar_silk", "handloom"],
        "zip_codes": ["752001"],
        "base_color": (245, 222, 179), "accent_color": (139, 69, 19)
    },
    {
        "id": 34,
        "name": "Sambalpuri Crimson Bridal Lehenga",
        "description": "Exquisite designer lehenga set featuring rich red Sambalpuri handloom patterns for weddings.",
        "category": "festive",
        "tags": ["ethnic", "festive", "lehenga", "sambalpuri", "silk", "ceremonial", "crimson"],
        "zip_codes": ["752001"],
        "base_color": (178, 34, 34), "accent_color": (218, 165, 32)
    },
    {
        "id": 35,
        "name": "Puri Beach Breeze Linen Shirt",
        "description": "Ultra-lightweight white linen shirt, designed for maximum comfort in coastal Odisha weather.",
        "category": "casual",
        "tags": ["casual", "summer", "linen", "breathable", "shirt", "white"],
        "zip_codes": ["752001"],
        "base_color": (255, 255, 255), "accent_color": (192, 192, 192)
    },
    {
        "id": 36,
        "name": "Sambalpuri Cotton Daily Kurti",
        "description": "Vibrant blue printed cotton dailywear kurti, light and breezy for summer.",
        "category": "casual",
        "tags": ["casual", "summer", "cotton", "breathable", "kurti", "sambalpuri", "dailywear"],
        "zip_codes": ["752001"],
        "base_color": (70, 130, 180), "accent_color": (255, 255, 255)
    },
    {
        "id": 37,
        "name": "Pipli Work Applique Dupatta",
        "description": "Stunning black cotton dupatta adorned with traditional Pipli applique embroidery.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "dupatta", "cotton", "applique", "black"],
        "zip_codes": ["752001"],
        "base_color": (20, 20, 20), "accent_color": (255, 69, 0)
    },
    {
        "id": 38,
        "name": "Katki Cotton Traditional Saree",
        "description": "Breathable hand-woven cotton saree in pastel pink, perfect for casual ethnic occasions.",
        "category": "casual",
        "tags": ["casual", "summer", "cotton", "saree", "traditional", "handloom", "pastel"],
        "zip_codes": ["752001"],
        "base_color": (255, 192, 203), "accent_color": (255, 255, 255)
    },
    {
        "id": 39,
        "name": "Odisha Silk Nehru Waistcoat",
        "description": "Premium handloom silk Nehru jacket in metallic gold, smart formal attire for wedding guests.",
        "category": "festive",
        "tags": ["ethnic", "festive", "formal", "waistcoat", "silk", "handloom", "men"],
        "zip_codes": ["752001"],
        "base_color": (218, 165, 32), "accent_color": (0, 0, 0)
    },
    {
        "id": 40,
        "name": "Pipli Applique Winter Shawl",
        "description": "Warm black woolen shawl with bright Pipli applique patches, cozy for coastal winter nights.",
        "category": "winter",
        "tags": ["winter", "warm", "shawl", "woolen", "applique"],
        "zip_codes": ["752001"],
        "base_color": (30, 30, 30), "accent_color": (220, 20, 60)
    },
    {
        "id": 41,
        "name": "Sambalpuri Ikat Winter Bomber",
        "description": "Trendy hybrid bomber jacket with Sambalpuri Ikat panels and warm fleece lining.",
        "category": "streetwear",
        "tags": ["streetwear", "modern", "jacket", "fusion", "winter", "sambalpuri"],
        "zip_codes": ["752001"],
        "base_color": (80, 20, 20), "accent_color": (0, 0, 0)
    },
    {
        "id": 42,
        "name": "Puri Temple Motif Kurta Set",
        "description": "Pure cotton yellow kurta paired with white pajama, featuring local temple border patterns.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "kurta", "cotton", "yellow"],
        "zip_codes": ["752001"],
        "base_color": (255, 215, 0), "accent_color": (255, 255, 255)
    },
    {
        "id": 43,
        "name": "Ikat Patchwork Denim Jacket",
        "description": "Heavy denim jacket with traditional Ikat patchwork details, college-fest favorite.",
        "category": "streetwear",
        "tags": ["streetwear", "denim", "jacket", "fusion", "modern"],
        "zip_codes": ["752001"],
        "base_color": (70, 130, 180), "accent_color": (255, 255, 255)
    },
    {
        "id": 44,
        "name": "Konark Sun Motif Graphic Tee",
        "description": "Breathable black cotton tee featuring a stylized print of the Konark Sun Temple wheel.",
        "category": "streetwear",
        "tags": ["streetwear", "casual", "cotton", "breathable", "tee"],
        "zip_codes": ["752001"],
        "base_color": (10, 10, 10), "accent_color": (255, 255, 255)
    },
    {
        "id": 45,
        "name": "Bomkai Silk Royal Blue Sherwani",
        "description": "Luxurious groom sherwani in hand-woven royal blue Bomkai silk with gold zari work.",
        "category": "festive",
        "tags": ["ethnic", "festive", "traditional", "sherwani", "silk", "handloom", "ceremonial", "blue", "men"],
        "zip_codes": ["752001"],
        "base_color": (0, 0, 139), "accent_color": (218, 165, 32)
    },

    # === GLOBAL APPAREL (15 Items) ===
    # zip_codes: [] makes these globally available to fill search results
    {
        "id": 46,
        "name": "Dailywear Cotton Kurta",
        "description": "Mint green pure cotton kurta, designed to keep you cool and comfortable in humid weather.",
        "category": "casual",
        "tags": ["casual", "summer", "cotton", "breathable", "kurta", "dailywear"],
        "zip_codes": [],
        "base_color": (152, 251, 152), "accent_color": (255, 255, 255)
    },
    {
        "id": 47,
        "name": "Breathable Linen Casual Shirt",
        "description": "Lightweight sky blue linen button-up shirt, perfect summer wear.",
        "category": "casual",
        "tags": ["casual", "summer", "linen", "breathable", "shirt", "dailywear", "men"],
        "zip_codes": [],
        "base_color": (135, 206, 235), "accent_color": (255, 255, 255)
    },
    {
        "id": 48,
        "name": "Heavy Velvet Kurta Suit",
        "description": "Rich plum heavy velvet straight kurta set with gold embroidery, cozy and festive.",
        "category": "winter",
        "tags": ["winter", "heavy-weight", "velvet", "kurta", "festive", "warm"],
        "zip_codes": [],
        "base_color": (48, 25, 52), "accent_color": (218, 165, 32)
    },
    {
        "id": 49,
        "name": "Woolen Cashmere Shawl",
        "description": "Luxurious beige Pashmina wool shawl with classic hand-woven Kashmiri patterns.",
        "category": "winter",
        "tags": ["winter", "heavy-weight", "shawl", "traditional", "warm", "cashmere"],
        "zip_codes": [],
        "base_color": (222, 184, 135), "accent_color": (139, 69, 19)
    },
    {
        "id": 50,
        "name": "Oversized Graphic Hoodie",
        "description": "Acid-wash grey oversized hoodie with a bold retro street print across the chest.",
        "category": "streetwear",
        "tags": ["streetwear", "casual", "hoodie", "modern", "heavy-weight"],
        "zip_codes": [],
        "base_color": (112, 128, 144), "accent_color": (255, 0, 255)
    },
    {
        "id": 51,
        "name": "Cargo Utility Joggers",
        "description": "Olive green utility cargo trousers with multiple pockets and adjustable ankle straps.",
        "category": "streetwear",
        "tags": ["streetwear", "casual", "cargo", "trousers", "modern"],
        "zip_codes": [],
        "base_color": (107, 142, 35), "accent_color": (0, 0, 0)
    },
    {
        "id": 52,
        "name": "Urban Denim Jacket",
        "description": "Oversized black wash denim trucker jacket with custom distressed details on sleeves.",
        "category": "streetwear",
        "tags": ["streetwear", "casual", "jacket", "denim", "modern"],
        "zip_codes": [],
        "base_color": (40, 40, 40), "accent_color": (255, 255, 255)
    },
    {
        "id": 53,
        "name": "Loose Fit Cropped Tee",
        "description": "Off-white streetwear crop top with a small minimal embroidered chest logo.",
        "category": "streetwear",
        "tags": ["streetwear", "casual", "top", "modern"],
        "zip_codes": [],
        "base_color": (248, 248, 255), "accent_color": (255, 69, 0)
    },
    {
        "id": 54,
        "name": "Distressed Streetwear Jeans",
        "description": "Light wash relaxed fit denim jeans featuring heavily shredded knee patches.",
        "category": "streetwear",
        "tags": ["streetwear", "casual", "trousers", "denim", "modern"],
        "zip_codes": [],
        "base_color": (176, 196, 222), "accent_color": (255, 255, 255)
    },
    {
        "id": 55,
        "name": "Puffer Jacket Hooded",
        "description": "Insulated black nylon puffer jacket with a faux-fur hood, blocking extreme winter winds.",
        "category": "winter",
        "tags": ["winter", "jacket", "puffer", "warm", "heavy-weight"],
        "zip_codes": [],
        "base_color": (20, 20, 20), "accent_color": (255, 255, 255)
    },
    {
        "id": 56,
        "name": "Quilted Winter Coat",
        "description": "Olive green quilted double-breasted coat with an adjustable belt and warm lining.",
        "category": "winter",
        "tags": ["winter", "jacket", "heavy-weight", "warm"],
        "zip_codes": [],
        "base_color": (85, 107, 47), "accent_color": (0, 0, 0)
    },
    {
        "id": 57,
        "name": "Thermal Fleece Innerwear",
        "description": "Dark grey thermal top and bottom set crafted from insulating micro-fleece.",
        "category": "winter",
        "tags": ["winter", "thermal", "warm", "dailywear"],
        "zip_codes": [],
        "base_color": (60, 60, 60), "accent_color": (100, 100, 100)
    },
    {
        "id": 58,
        "name": "Fleece Hooded Sweatshirt",
        "description": "Forest green thick fleece pullover hoodie with a kangaroo pocket for casual winter wear.",
        "category": "winter",
        "tags": ["winter", "hoodie", "warm", "casual"],
        "zip_codes": [],
        "base_color": (34, 139, 34), "accent_color": (255, 255, 255)
    },
    {
        "id": 59,
        "name": "Knitted Cable Sweater",
        "description": "Cream white heavy cable-knit crewneck sweater. A timeless warm winter classic.",
        "category": "winter",
        "tags": ["winter", "warm", "heavy-weight", "sweater"],
        "zip_codes": [],
        "base_color": (253, 245, 230), "accent_color": (139, 69, 19)
    },
    {
        "id": 60,
        "name": "Heavy Velvet Shawl",
        "description": "Deep emerald green plush velvet shawl with hand-embroidered golden borders.",
        "category": "winter",
        "tags": ["winter", "heavy-weight", "velvet", "shawl", "festive", "warm"],
        "zip_codes": [],
        "base_color": (0, 70, 40), "accent_color": (218, 165, 32)
    }
]

# Style dimension mapping to compute deterministic vector vibes
def get_vibe_vector(category_or_tags, category_str="", aesthetic_str=""):
    """
    Build a 512-dim deterministic vibe vector from tags + category + aesthetic/nature.
    
    Vector layout (512 dims):
      0-99   : Ethnic / Traditional / Festive
      100-149: Casual / Summer / Breathable
      150-199: Winter / Warm / Heavy-weight
      200-249: Streetwear / Modern / Fusion / Party
      250-299: Luxury / Premium / Designer / Bridal
      300-349: Minimalist / Clean / Subtle / Neutral
      350-399: Boho / Earthy / Artisanal / Handloom
      400-449: Maximalist / Bold / Embellished / Printed
      450-474: Workwear / Formal / Office
      475-499: Athleisure / Sporty / Active
      500-511: Category + Aesthetic fingerprint noise
    """
    vec = np.zeros(512)
    tags = set(category_or_tags)

    # === STYLE ZONE 1: Ethnic / Traditional / Festive (0-99) ===
    if any(t in tags for t in ["ethnic", "festive", "saree", "lehenga", "traditional",
                                "jainsem", "jymphong", "mundu", "sherwani", "kurta",
                                "ceremonial", "zari", "banarasi", "bhagalpuri-silk"]):
        vec[0:100] = 1.0

    # === STYLE ZONE 2: Casual / Summer / Breathable (100-149) ===
    if any(t in tags for t in ["casual", "summer", "linen", "cotton", "breathable",
                                "light", "floral", "printed", "salwar"]):
        vec[100:150] = 1.0

    # === STYLE ZONE 3: Winter / Warm / Heavy-weight (150-199) ===
    if any(t in tags for t in ["winter", "heavy-weight", "velvet", "shawl", "warm",
                                "jacket", "cardigan", "woolen", "quilted", "layered"]):
        vec[150:200] = 1.0

    # === STYLE ZONE 4: Streetwear / Modern / Fusion / Party (200-249) ===
    if any(t in tags for t in ["streetwear", "hoodie", "cargo", "modern", "denim",
                                "fusion", "party", "contemporary", "indo-western"]):
        vec[200:250] = 1.0

    # === AESTHETIC ZONE 1: Luxury / Premium / Bridal (250-299) ===
    if any(t in tags for t in ["luxury", "premium", "designer", "bridal", "silk",
                                "heavy_silk", "gold", "zari", "embellished", "brocade",
                                "ceremonial"]):
        vec[250:300] = 1.0

    # === AESTHETIC ZONE 2: Minimalist / Clean / Subtle / Neutral (300-349) ===
    if any(t in tags for t in ["minimalist", "clean", "subtle", "neutral", "solid",
                                "simple", "basic", "pastel", "white", "beige"]):
        vec[300:350] = 1.0

    # === AESTHETIC ZONE 3: Boho / Earthy / Artisanal / Handloom (350-399) ===
    if any(t in tags for t in ["boho", "earthy", "artisanal", "handloom", "natural-dye",
                                "block-print", "ikat", "khadi", "woven", "tribal",
                                "bhagalpuri-silk", "traditional_embroidery"]):
        vec[350:400] = 1.0

    # === AESTHETIC ZONE 4: Maximalist / Bold / Embellished (400-449) ===
    if any(t in tags for t in ["maximalist", "bold", "embellished", "printed", "sequin",
                                "mirror-work", "heavy", "multicolor", "vibrant",
                                "crimson", "magenta", "fuchsia"]):
        vec[400:450] = 1.0

    # === AESTHETIC ZONE 5: Workwear / Formal (450-474) ===
    if any(t in tags for t in ["workwear", "formal", "office", "corporate", "blazer",
                                "structured", "tailored"]):
        vec[450:475] = 1.0

    # === AESTHETIC ZONE 6: Athleisure / Sporty / Active (475-499) ===
    if any(t in tags for t in ["athleisure", "sporty", "active", "yoga", "gym",
                                "stretch", "moisture-wicking"]):
        vec[475:500] = 1.0

    # === FINGERPRINT: Category + Aesthetic string hashing (500-511) ===
    fingerprint_str = category_str + " " + aesthetic_str + " " + " ".join(sorted(list(tags)))
    hash_seed = abs(hash(fingerprint_str)) % (2**32)
    rng = np.random.default_rng(hash_seed)
    noise = rng.normal(0, 0.05, 512)
    vec += noise

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    return vec.tolist()


def generate_catalog_images():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        logger.error("Pillow library is missing!")
        return False
        
    os.makedirs(CATALOG_DIR, exist_ok=True)
    logger.info(f"Generating 60 mockup catalog images in {CATALOG_DIR}...")
    
    for product in PRODUCTS_SOURCE:
        i = product["id"]
        image_path = os.path.join(CATALOG_DIR, f"catalog_{i}.jpg")
        
        img = Image.new("RGB", (400, 500), color=product["base_color"])
        draw = ImageDraw.Draw(img)
        
        base = product["base_color"]
        accent = product["accent_color"]
        
        for r in range(50, 250, 40):
            draw.ellipse([200-r, 180-r, 200+r, 180+r], outline=accent, width=3)
            
        draw.rectangle([40, 40, 360, 320], outline=accent, width=2)
        draw.rectangle([50, 50, 200, 80], fill=accent, outline=(0, 0, 0))
        
        try:
            draw.text((60, 58), product["category"].upper(), fill=(0, 0, 0))
            name = product["name"]
            draw.text((30, 350), name, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))
            
            desc_words = product["description"].split()
            line1 = " ".join(desc_words[:5])
            line2 = " ".join(desc_words[5:10])
            draw.text((30, 390), line1, fill=(240, 240, 240))
            draw.text((30, 410), line2, fill=(240, 240, 240))
            
            tags_str = ", ".join(product["tags"][:3])
            draw.text((30, 450), f"Tags: {tags_str}", fill=accent)
        except Exception:
            draw.text((20, 350), product["name"], fill=(255, 255, 255))
            
        img.save(image_path, "JPEG")
        
    logger.info(f"Finished generating 60 mock images in {CATALOG_DIR}.")
    return True

def run_clip_embeddings(use_real_clip=True):
    processed_products = []
    clip_model = None
    clip_processor = None
    
    if use_real_clip:
        try:
            logger.info("Attempting to load CLIP model ('openai/clip-vit-base-patch32')...")
            import torch
            from transformers import CLIPModel, CLIPProcessor
            torch.set_num_threads(2)
            clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            logger.info("CLIP Model loaded successfully!")
        except Exception as e:
            logger.warning(f"Failed to load CLIP model. Falling back to synthetic vectors. Details: {e}")
            use_real_clip = False
            
    for item in PRODUCTS_SOURCE:
        i = item["id"]
        image_name = f"catalog_{i}.jpg"
        image_url = f"/catalog/{image_name}"
        
        embedding = None
        
        if use_real_clip and clip_model and clip_processor:
            try:
                from PIL import Image
                import torch
                
                image_path = os.path.join(CATALOG_DIR, image_name)
                image = Image.open(image_path)
                inputs = clip_processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_features = clip_model.get_image_features(**inputs)
                    
                feat_np = image_features.cpu().numpy()[0]
                norm = np.linalg.norm(feat_np)
                if norm > 0:
                    feat_np = feat_np / norm
                embedding = feat_np.tolist()
            except Exception as ex:
                logger.error(f"Error computing CLIP: {ex}. Using fallback.")
                embedding = None
                
        if embedding is None:
            embedding = get_vibe_vector(
                item["tags"],
                category_str=item.get("category", ""),
                aesthetic_str=item.get("aesthetic", "")
            )
            
        processed_products.append({
            "id": i,
            "name": item["name"],
            "description": item["description"],
            "image_url": image_url,
            "tags": item["tags"],
            "zip_codes": item["zip_codes"],
            "embedding": embedding
        })
        
    return processed_products

def upload_to_supabase(products):
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase configuration missing. Skipping upload.")
        return False
        
    try:
        logger.info("Initializing Supabase Client and uploading catalog products...")
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        logger.info("Clearing old products from Supabase table...")
        supabase.table("products").delete().neq("id", 0).execute()
        
        logger.info(f"Inserting {len(products)} products into Supabase...")
        supabase.table("products").insert(products).execute()
        logger.info("Catalog uploaded to Supabase successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to upload to Supabase: {e}")
        return False

def main():
    logger.info("Starting local catalog generation & embedding pipeline...")
    images_ok = generate_catalog_images()
    if not images_ok:
        logger.error("Failed to generate catalog images.")
        
    products = run_clip_embeddings(use_real_clip=True)
    
    try:
        with open(LOCAL_CATALOG_FILE, "w") as f:
            json.dump(products, f, indent=4)
        logger.info(f"Successfully saved local catalog cache containing {len(products)} products to {LOCAL_CATALOG_FILE}")
    except Exception as e:
        logger.error(f"Failed to save local catalog file: {e}")
        
    db_ok = upload_to_supabase(products)
    if db_ok:
        logger.info("Catalog embedding pipeline complete (Local + Supabase SQL DB synchronized).")
    else:
        logger.info("Catalog embedding pipeline complete (Local Offline file created).")

if __name__ == "__main__":
    main()
