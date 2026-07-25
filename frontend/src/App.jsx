import { useState, useEffect, useRef } from 'react';
import './App.css';
import { FALLBACK_PRODUCTS } from './catalog_fallback';
import { REGIONAL_RECOMMENDATIONS } from './recommendations_db';

const ZIP_CODES = {
  "682001": { city: "Fort Kochi", state: "Kochi", name: "Kochi (682001)" },
  "752001": { city: "Puri", state: "Odisha", name: "Odisha (752001)" },
  "800008": { city: "Patna City", state: "Patna", name: "Patna (800008)" },
  "793001": { city: "Shillong", state: "Meghalaya", name: "Shillong (793001)" },
  "302001": { city: "Jaipur", state: "Rajasthan", name: "Rajasthan (302001)" }
};

// Mapped canonical ZIP codes for backend queries
const ZIP_MAPPING = {
  "800001": "800008",
  "560034": "682001",
  "752001": "752001",
  "793001": "793001",
  "302001": "302001"
};

// Regional Faded Background Images per PIN Code
const CITY_BACKGROUNDS = {
  "800008": "/images/cities/patna.png",
  "302001": "/images/cities/jaipur.jpg",
  "793001": "/images/cities/shillong.jpg",
  "752001": "/images/cities/odisha.jpg",
  "682001": "/images/cities/kochi.jpg"
};



// Regional date profile presets
const REGIONAL_DATE_PRESETS = {
  "800008": [
    { key: "jan_14", label: "Jan 14 (Makar Sankranti)", dateStr: "2026-01-14", event: "Makar Sankranti Harvest", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "casual", "cotton", "yellow", "dailywear"] },
    { key: "jan_26", label: "Jan 26 (Republic Day)", dateStr: "2026-01-26", event: "Republic Day Parade", event_type: "festival", isFestive: true, trendingTags: ["white", "saffron", "green", "ethnic", "formal"] },
    { key: "feb_2", label: "Feb 2 (Saraswati Puja)", dateStr: "2026-02-02", event: "Saraswati Puja (Vasant Panchami)", event_type: "festival", isFestive: true, trendingTags: ["saree", "kurta", "yellow", "ethnic"] },
    { key: "mar_3", label: "Mar 3 (Holi)", dateStr: "2026-03-03", event: "Holi Festival of Colors", event_type: "festival", isFestive: true, trendingTags: ["white", "cotton", "casual", "dailywear"] },
    { key: "mar_22", label: "Mar 22 (Bihar Diwas)", dateStr: "2026-03-22", event: "Bihar Diwas (Bihar Day)", event_type: "festival", isFestive: true, trendingTags: ["saree", "salwar", "bhagalpuri_silk", "kurta", "dhoti", "nehru_jacket", "white"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["formal", "ethnic", "fusion"] },
    { key: "aug_15", label: "Aug 15 (Independence Day)", dateStr: "2026-08-15", event: "Independence Day Ceremony", event_type: "festival", isFestive: true, trendingTags: ["saffron", "white", "green", "ethnic", "formal", "cotton"] },
    { key: "oct_18", label: "Oct 18 (Durga Puja)", dateStr: "2026-10-18", event: "Durga Puja Peak Pandals", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "silk", "saree", "heavy_silk", "traditional"] },
    { key: "nov_8", label: "Nov 8 (Diwali)", dateStr: "2026-11-08", event: "Diwali Lights Festival", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "traditional", "regal", "gold", "silk"] },
    { key: "nov_15", label: "Nov 15 (Chhath Puja)", dateStr: "2026-11-15", event: "Chhath Puja (Sandhya Arghya)", event_type: "festival", isFestive: true, trendingTags: ["saree", "cotton", "traditional", "dhoti", "saffron", "yellow", "white", "patna", "chhath_puja"] },
    { key: "dec_10", label: "Dec 10 (Wedding Day)", dateStr: "2026-12-10", event: "Patna Wedding Day (Pheras Ritual)", event_type: "wedding_day", isFestive: true, trendingTags: ["heavy_silk", "traditional_embroidery", "ceremonial", "silk", "saree", "sherwani", "crimson", "gold", "maroon"] }
  ],
  "682001": [
    { key: "jan_20", label: "Jan 20 (Biennale Peak)", dateStr: "2026-01-20", event: "Kochi-Muziris Biennale Peak", event_type: "festival", isFestive: true, trendingTags: ["artsy", "bohemian", "linen", "sustainable", "modern"] },
    { key: "jan_26", label: "Jan 26 (Republic Day)", dateStr: "2026-01-26", event: "Republic Day Parade", event_type: "festival", isFestive: true, trendingTags: ["white", "fusion", "formal", "lightweight"] },
    { key: "mar_3", label: "Mar 3 (Holi)", dateStr: "2026-03-03", event: "Holi Festival of Colors", event_type: "festival", isFestive: true, trendingTags: ["casual", "streetwear", "denim", "cotton"] },
    { key: "apr_14", label: "Apr 14 (Vishu)", dateStr: "2026-04-14", event: "Vishu Festival (Malayali New Year)", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "yellow", "gold", "cream", "kasavu_weave"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["formal", "elegant", "premium"] },
    { key: "aug_15", label: "Aug 15 (Independence Day)", dateStr: "2026-08-15", event: "Independence Day Ceremony", event_type: "festival", isFestive: true, trendingTags: ["saffron", "white", "green", "ethnic", "formal", "lightweight"] },
    { key: "aug_27", label: "Aug 27 (Onam Thiruvonam)", dateStr: "2026-08-27", event: "Onam Festival (Thiruvonam)", event_type: "festival", isFestive: true, trendingTags: ["saree", "mundu", "kasavu_weave", "white", "cream", "gold"] },
    { key: "oct_18", label: "Oct 18 (Durga Puja)", dateStr: "2026-10-18", event: "Durga Puja Celebrations", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "minimalist", "cotton"] },
    { key: "nov_8", label: "Nov 8 (Diwali)", dateStr: "2026-11-08", event: "Diwali Lights Festival", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "contemporary_fusion", "fusion", "earth-tones"] },
    { key: "dec_27", label: "Dec 27 (Wedding Day)", dateStr: "2026-12-27", event: "Kochi Wedding Day (Thalikettu)", event_type: "wedding_day", isFestive: true, trendingTags: ["kasavu_weave", "off-white", "cream", "gold"] }
  ],
  "752001": [
    { key: "jan_14", label: "Jan 14 (Makar Sankranti)", dateStr: "2026-01-14", event: "Makar Sankranti (Makar Mela)", event_type: "festival", isFestive: true, trendingTags: ["traditional", "tussar_silk", "yellow", "red", "odisha"] },
    { key: "jan_26", label: "Jan 26 (Republic Day)", dateStr: "2026-01-26", event: "Republic Day Parade", event_type: "festival", isFestive: true, trendingTags: ["smart_casual", "tricolor", "khadi", "white"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["smart_formal", "blazer", "premium_fusion"] },
    { key: "jun_14", label: "Jun 14 (Pahili Raja)", dateStr: "2026-06-14", event: "Pahili Raja (Raja Parba)", event_type: "festival", isFestive: true, trendingTags: ["traditional", "cotton", "pastel", "lightweight", "sambalpuri"] },
    { key: "jun_15", label: "Jun 15 (Raja Sankranti)", dateStr: "2026-06-15", event: "Raja Sankranti Festival", event_type: "festival", isFestive: true, trendingTags: ["traditional", "cotton", "pastel", "sambalpuri", "ethnic"] },
    { key: "jul_16", label: "Jul 16 (Rath Yatra)", dateStr: "2026-07-16", event: "Puri Rath Yatra Chariot Festival", event_type: "festival", isFestive: true, trendingTags: ["sambalpuri", "cotton", "traditional", "yellow", "saffron", "saree", "kurta"] },
    { key: "aug_15", label: "Aug 15 (Independence Day)", dateStr: "2026-08-15", event: "Independence Day Ceremony", event_type: "festival", isFestive: true, trendingTags: ["khadi", "tricolor", "smart_casual"] },
    { key: "sep_15", label: "Sep 15 (Nuakhai Harvest)", dateStr: "2026-09-15", event: "Nuakhai Agricultural Harvest Festival", event_type: "festival", isFestive: true, trendingTags: ["sambalpuri", "handloom", "cotton", "traditional", "ethnic", "saree", "kurta", "odisha"] },
    { key: "oct_18", label: "Oct 18 (Durga Puja)", dateStr: "2026-10-18", event: "Durga Puja (Ravana Podi)", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "traditional_silk", "red", "gold", "sambalpuri"] },
    { key: "nov_8", label: "Nov 8 (Diwali)", dateStr: "2026-11-08", event: "Diwali Lights Festival", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "regal", "gold", "silk", "heavy_embroidery"] },
    { key: "dec_20", label: "Dec 20 (Odia Wedding)", dateStr: "2026-12-20", event: "Odisha Winter Wedding (Pheras)", event_type: "wedding_day", isFestive: true, trendingTags: ["heavy_silk", "tussar_silk", "ceremonial", "sherwani", "crimson", "gold"] }
  ],
  "793001": [ // Shillong, Meghalaya
    { key: "jan_03", label: "Jan 03 (Highland Winter)", dateStr: "2026-01-03", event: "Highland Winter Music Fest", event_type: "festival", isFestive: true, trendingTags: ["woolen", "winter", "knitted", "cardigan", "shillong"] },
    { key: "jan_14", label: "Jan 14 (Highland Winter)", dateStr: "2026-01-14", event: "Highland Winter Music Fest", event_type: "festival", isFestive: true, trendingTags: ["woolen", "winter", "knitted", "cardigan", "shillong"] },
    { key: "apr_10", label: "Apr 10 (Shad Suk Mynsiem)", dateStr: "2026-04-10", event: "Shad Suk Mynsiem (Khasi Thanksgiving Dance)", event_type: "festival", isFestive: true, trendingTags: ["jainsem", "khasi", "silk", "traditional", "gold", "nongkrem"] },
    { key: "may_15", label: "May 15 (Spring Gala)", dateStr: "2026-05-15", event: "Shillong Pine Spring Gala", event_type: "festival", isFestive: true, trendingTags: ["pastel", "linen", "boho", "casual", "shillong"] },
    { key: "nov_10", label: "Nov 10 (Nongkrem Dance)", dateStr: "2026-11-10", event: "Nongkrem Dance Festival (Smit)", event_type: "festival", isFestive: true, trendingTags: ["khasi", "silk", "brocade", "traditional", "gold", "velvet"] },
    { key: "nov_15", label: "Nov 15 (Wangala Fest)", dateStr: "2026-11-15", event: "Wangala 100 Drums Garo Festival", event_type: "festival", isFestive: true, trendingTags: ["garo", "dakmanda", "wangala", "beaded", "handloom", "tribal"] },
    { key: "nov_22", label: "Nov 22 (Cherry Blossom)", dateStr: "2026-11-22", event: "Shillong Cherry Blossom Festival", event_type: "festival", isFestive: true, trendingTags: ["cherry_blossom", "pastel", "floral", "chiffon", "gown", "indie"] },
    { key: "dec_18", label: "Dec 18 (Highland Wedding)", dateStr: "2026-12-18", event: "Highland Winter Wedding (Khasi & Christian)", event_type: "wedding_day", isFestive: true, trendingTags: ["khasi", "silk", "brocade", "velvet", "gown", "traditional", "gold"] },
    { key: "dec_25", label: "Dec 25 (Highland Christmas)", dateStr: "2026-12-25", event: "Shillong Grand Christmas Solstice", event_type: "festival", isFestive: true, trendingTags: ["woolen", "velvet", "cardigan", "red", "cozy", "festive"] }
  ],
  "302001": [ // Rajasthan (Jaipur)
    { key: "jan_03", label: "Jan 03 (Kite Prep)", dateStr: "2026-01-03", event: "Jaipur International Kite Festival (Makar Sankranti)", event_type: "festival", isFestive: true, trendingTags: ["cotton", "yellow", "block_print", "anarkali", "rajasthan"] },
    { key: "jan_14", label: "Jan 14 (Kite Festival)", dateStr: "2026-01-14", event: "Jaipur International Kite Festival (Makar Sankranti)", event_type: "festival", isFestive: true, trendingTags: ["cotton", "yellow", "block_print", "anarkali", "rajasthan"] },
    { key: "feb_15", label: "Feb 15 (Desert Festival)", dateStr: "2026-02-15", event: "Jaisalmer Desert Festival", event_type: "festival", isFestive: true, trendingTags: ["bandhani", "mirror_work", "choli", "ethnic", "desert"] },
    { key: "mar_20", label: "Mar 20 (Elephant Festival)", dateStr: "2026-03-20", event: "Jaipur Elephant & Holi Festival", event_type: "festival", isFestive: true, trendingTags: ["bright", "cotton", "gota_patti", "jaipur"] },
    { key: "apr_04", label: "Apr 04 (Gangaur Procession)", dateStr: "2026-04-04", event: "Royal Gangaur Festival Procession", event_type: "festival", isFestive: true, trendingTags: ["traditional", "gota_patti", "lehenga", "gold", "rajasthan"] },
    { key: "aug_12", label: "Aug 12 (Teej Festival)", dateStr: "2026-08-12", event: "Swarn Teej Festival Jaipur", event_type: "festival", isFestive: true, trendingTags: ["lehenga", "gota_patti", "green", "silk", "teej", "ethnic"] },
    { key: "oct_20", label: "Oct 20 (Marwar Fest)", dateStr: "2026-10-20", event: "Marwar Folk Music & Dance Festival Jodhpur", event_type: "festival", isFestive: true, trendingTags: ["mirror_work", "bandhani", "angrakha", "ethnic"] },
    { key: "nov_18", label: "Nov 18 (Pushkar Fair)", dateStr: "2026-11-18", event: "Pushkar Camel Fair & Cultural Night", event_type: "festival", isFestive: true, trendingTags: ["pushkar", "angrakha", "silk", "handloom", "traditional"] },
    { key: "dec_15", label: "Dec 15 (Rajwara Wedding)", dateStr: "2026-12-15", event: "Jaipur Royal Rajwara Wedding (Dev Uthan Lagan)", event_type: "wedding_day", isFestive: true, trendingTags: ["heavy_silk", "gota_patti", "lehenga", "sherwani", "crimson", "gold", "maroon"] }
  ]
};

const LINGERIE_KEYWORDS = [
  "bra", "bras", "panty", "panties", "briefs", "boxers", "lingerie", "innerwear",
  "thong", "pantyhose", "stockings", "bustier", "shapewear", "nightwear", "nightdress",
  "babydoll", "camisole", "bikini", "underwear", "swimwear", "thermal top", "thermal bottoms",
  "night-suits", "night suits", "pajamas", "pyjamas", "lounge shorts"
];

function isLingerieItem(item) {
  if (!item) return false;
  const text = `${item.name || ''} ${item.description || ''} ${item.category || ''} ${(item.tags || []).join(' ')}`.toLowerCase();
  return LINGERIE_KEYWORDS.some(kw => text.includes(kw));
}

const VIBE_DEFINITIONS = {
  universal_traditionalist: {
    name: "The Universal Traditionalist (Classic Pan-Indian Ethnic)",
    emoji: "🥻",
    desc: "A versatile,Modest, festive, evergreen ethnic aesthetic representing standard traditional wear found on Indian e-commerce.",
    tags: ["kurta", "palazzo", "dupatta", "anarkali", "churidar", "saree", "kurti", "pyjama", "nehru-jacket", "modi-jacket", "rayon", "cotton-blend", "georgette", "chanderi", "art-silk", "chiffon", "block-print", "paisley", "yoke", "foil-print", "ikat", "mustard", "maroon", "emerald", "rani-pink", "ivory"]
  },
  dark_academia: {
    name: "Dark Academia",
    emoji: "📚",
    desc: "A nostalgic, scholarly aesthetic inspired by literature, classic European architecture, and boarding school prep.",
    tags: ["turtleneck", "plaid", "trousers", "trench", "button-down", "sweater-vest", "pleated-skirt", "blazer", "pinafore", "tweed", "heavy-wool", "corduroy", "linen", "leather", "houndstooth", "argyle", "herringbone", "forest-green", "charcoal", "chocolate-brown", "burgundy", "navy", "beige"]
  },
  cottagecore: {
    name: "Cottagecore",
    emoji: "🌾",
    desc: "A romanticized interpretation of western agricultural life, focusing on nature, simplicity, and vintage rural silhouettes.",
    tags: ["puff-sleeve", "corset", "prairie-blouse", "tiered-skirt", "maxi-skirt", "cardigan", "slip-dress", "overalls", "pinafore", "peasant-blouse", "muslin", "linen", "chiffon", "lace", "crochet", "floral", "ditsy-floral", "gingham", "botanical", "toile", "sage-green", "dusty-rose", "butter-yellow", "lavender"]
  },
  grunge_alt: {
    name: "Grunge / Alt",
    emoji: "🎸",
    desc: "Rooted in the 90s alternative rock scene, characterized by a messy, rebellious, and purposefully unkempt styling.",
    tags: ["band-tee", "distressed-jeans", "combat-boots", "slip-dress", "tights", "long-sleeve", "cargo", "biker-jacket", "ripped-shorts", "distressed-denim", "leather", "mesh", "heavy-cotton", "stripes", "tie-dye", "crimson", "charcoal", "burgundy", "neon-green", "black"]
  }
};

const CONTEXT_MATRICES = {
  "discovery": { "w_aesthetic": 0.85, "w_festivity": 0.05, "w_boutique": 0.05, "w_creator": 0.05 },
  "high_intent": { "w_aesthetic": 0.70, "w_festivity": 0.10, "w_boutique": 0.10, "w_creator": 0.10 },
  "festive_season": { "w_aesthetic": 0.15, "w_festivity": 0.75, "w_boutique": 0.05, "w_creator": 0.05 },
  "hyper_local_boutique": { "w_aesthetic": 0.25, "w_festivity": 0.05, "w_boutique": 0.65, "w_creator": 0.05 },
  "social_commerce": { "w_aesthetic": 0.25, "w_festivity": 0.05, "w_boutique": 0.05, "w_creator": 0.65 },
};

const LOCAL_VELOCITY_CACHE = {
  1:  { velocity_score: 0.92, units_last_hour: 47 },
  2:  { velocity_score: 0.88, units_last_hour: 38 },
  7:  { velocity_score: 0.75, units_last_hour: 22 },
  9:  { velocity_score: 0.65, units_last_hour: 18 },
  13: { velocity_score: 0.70, units_last_hour: 20 },
  15: { velocity_score: 0.80, units_last_hour: 30 },
  11: { velocity_score: 0.55, units_last_hour: 12 },
  48: { velocity_score: 0.60, units_last_hour: 15 },
  6:  { velocity_score: 0.72, units_last_hour: 24 },
  16: { velocity_score: 0.95, units_last_hour: 52 },
  17: { velocity_score: 0.85, units_last_hour: 35 },
  25: { velocity_score: 0.78, units_last_hour: 28 },
  28: { velocity_score: 0.70, units_last_hour: 20 },
  20: { velocity_score: 0.62, units_last_hour: 16 },
  26: { velocity_score: 0.55, units_last_hour: 11 },
  23: { velocity_score: 0.50, units_last_hour:  9 },
  24: { velocity_score: 0.58, units_last_hour: 14 },
  30: { velocity_score: 0.45, units_last_hour:  7 },
  31: { velocity_score: 0.90, units_last_hour: 42 },
  32: { velocity_score: 0.82, units_last_hour: 32 },
  33: { velocity_score: 0.78, units_last_hour: 26 },
  36: { velocity_score: 0.72, units_last_hour: 22 },
  37: { velocity_score: 0.68, units_last_hour: 19 },
  41: { velocity_score: 0.65, units_last_hour: 17 },
  44: { velocity_score: 0.60, units_last_hour: 14 },
  40: { velocity_score: 0.55, units_last_hour: 10 },
  39: { velocity_score: 0.75, units_last_hour: 25 },
};

function generateVibeVector(vibeName) {
  const vec = new Array(512).fill(0);
  const def = VIBE_DEFINITIONS[vibeName];
  if (!def) return vec;
  
  const tags = def.tags;
  
  // === STYLE ZONE 1: Ethnic / Traditional / Festive (0-99) ===
  if (tags.some(t => ["ethnic", "festive", "saree", "lehenga", "traditional", "jainsem", "jymphong", "mundu", "sherwani", "kurta", "ceremonial", "zari", "banarasi", "bhagalpuri-silk"].includes(t))) {
    vec.fill(1, 0, 100);
  }
  // === STYLE ZONE 2: Casual / Summer / Breathable (100-149) ===
  if (tags.some(t => ["casual", "summer", "linen", "cotton", "breathable", "light", "printed", "salwar"].includes(t))) {
    vec.fill(1, 100, 150);
  }
  // === STYLE ZONE 3: Winter / Warm / Heavy-weight (150-199) ===
  if (tags.some(t => ["winter", "heavy-weight", "velvet", "shawl", "warm", "jacket", "cardigan", "woolen", "quilted", "layered"].includes(t))) {
    vec.fill(1, 150, 200);
  }
  // === STYLE ZONE 4: Streetwear / Modern / Fusion / Party (200-249) ===
  if (tags.some(t => ["streetwear", "hoodie", "cargo", "modern", "denim", "fusion", "party", "contemporary", "indo-western"].includes(t))) {
    vec.fill(1, 200, 250);
  }
  // === AESTHETIC ZONE 1: Luxury / Premium / Designer / Bridal (250-299) ===
  if (tags.some(t => ["luxury", "premium", "designer", "bridal", "silk", "heavy_silk", "gold", "zari", "embellished", "brocade", "ceremonial"].includes(t))) {
    vec.fill(1, 250, 300);
  }
  // === AESTHETIC ZONE 2: Minimalist / Clean / Subtle / Neutral (300-349) ===
  if (tags.some(t => ["minimalist", "clean", "subtle", "neutral", "solid", "simple", "basic", "pastel", "white", "beige"].includes(t))) {
    vec.fill(1, 300, 350);
  }
  // === AESTHETIC ZONE 3: Boho / Earthy / Artisanal / Handloom (350-399) ===
  if (tags.some(t => ["boho", "earthy", "artisanal", "handloom", "natural-dye", "block-print", "ikat", "khadi", "woven", "tribal", "bhagalpuri-silk", "traditional_embroidery"].includes(t))) {
    vec.fill(1, 350, 400);
  }
  // === AESTHETIC ZONE 4: Maximalist / Bold / Embellished / Printed (400-449) ===
  if (tags.some(t => ["maximalist", "bold", "embellished", "printed", "sequin", "mirror-work", "heavy", "multicolor", "vibrant", "crimson", "magenta", "fuchsia"].includes(t))) {
    vec.fill(1, 400, 450);
  }
  // === AESTHETIC ZONE 5: Workwear / Formal / Office (450-474) ===
  if (tags.some(t => ["workwear", "formal", "office", "corporate", "blazer", "structured", "tailored"].includes(t))) {
    vec.fill(1, 450, 475);
  }
  // === AESTHETIC ZONE 6: Athleisure / Sporty / Active (475-499) ===
  if (tags.some(t => ["athleisure", "sporty", "active", "yoga", "gym", "stretch", "moisture-wicking"].includes(t))) {
    vec.fill(1, 475, 500);
  }
  
  let hash = 0;
  for (let i = 0; i < vibeName.length; i++) {
    hash = vibeName.charCodeAt(i) + ((hash << 5) - hash);
  }
  let seed = Math.abs(hash) || 777;
  function random() {
    let x = Math.sin(seed++) * 10000;
    return x - Math.floor(x);
  }
  function boxMuller() {
    let u = 0, v = 0;
    while(u === 0) u = random();
    while(v === 0) v = random();
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  }
  for (let i = 0; i < 512; i++) {
    vec[i] += boxMuller() * 0.05;
  }
  
  let norm = 0;
  for (let i = 0; i < 512; i++) norm += vec[i] * vec[i];
  norm = Math.sqrt(norm);
  if (norm > 0) {
    for (let i = 0; i < 512; i++) vec[i] = vec[i] / norm;
  }
  return vec;
}

function calculateCosineSimilarity(vecA, vecB) {
  if (!vecA || !vecB) return 0.0;
  let dotProduct = 0.0;
  let normA = 0.0;
  let normB = 0.0;
  for (let i = 0; i < 512; i++) {
    dotProduct += vecA[i] * vecB[i];
    normA += vecA[i] * vecA[i];
    normB += vecB[i] * vecB[i];
  }
  if (normA === 0 || normB === 0) return 0.0;
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

const BACKEND_ZIP_MAPPED = {
  "800008": "800008",
  "302001": "302001",
  "793001": "793001",
  "752001": "752001",
  "682001": "682001"
};

const BOUTIQUE_FALLBACK_DEFS = {
  "800008": [
    { store_id: "STR_800008_001", store_name: "Patna Saree Market & Silk House", locality: "Frazer Road, Patna", rating: "4.8 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Patna+Saree+Market+Frazer+Road+Patna", signature: "Banarasi Silk & Zardozi Wedding Lehengas" },
    { store_id: "STR_800008_002", store_name: "Hathwa Market Boutique Hub", locality: "Bakerganj, Patna", rating: "4.7 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Hathwa+Market+Bakerganj+Patna", signature: "Chhath Puja Red Silk Sarees & Anarkali Suits" },
    { store_id: "STR_800008_003", store_name: "Khetan Super Market Traditional Store", locality: "Birla Mandir Road, Patna", rating: "4.6 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Khetan+Super+Market+Patna", signature: "Bihari Bridal Dupattas & Ethnic Kurti Sets" },
    { store_id: "STR_800008_004", store_name: "Maurya Lok Fashion Studio", locality: "Maurya Lok Complex, Patna", rating: "4.5 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Maurya+Lok+Patna", signature: "Indo-Western Ethnic Wear & Designer Suits" }
  ],
  "302001": [
    { store_id: "STR_302001_001", store_name: "Johari Bazaar Royal Rajputi Poshak", locality: "Johari Bazaar, Jaipur", rating: "4.9 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Johari+Bazaar+Jaipur", signature: "Royal Rajputi Poshak & Heavy Gota Patti Work" },
    { store_id: "STR_302001_002", store_name: "Bapu Bazaar Bandhani Emporium", locality: "Bapu Bazaar, Jaipur", rating: "4.8 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Bapu+Bazaar+Jaipur", signature: "Jaipur Bandhani & Leheriya Pure Georgette Sarees" },
    { store_id: "STR_302001_003", store_name: "C-Scheme Designer Handloom Studio", locality: "C-Scheme, Jaipur", rating: "4.7 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=C-Scheme+Jaipur", signature: "Sanganeri Block-Print Cotton Kurtis & Skirts" },
    { store_id: "STR_302001_004", store_name: "MI Road Heritage Silk House", locality: "Mirza Ismail Road, Jaipur", rating: "4.6 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=MI+Road+Jaipur", signature: "Brocade Silk Lehengas & Festive Sharara Sets" }
  ],
  "793001": [
    { store_id: "STR_793001_001", store_name: "Police Bazar Khasi Traditional Jainsem House", locality: "Police Bazar, Shillong", rating: "4.8 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Police+Bazar+Shillong", signature: "Pure Ryndia & Silk Jainsem Drapes" },
    { store_id: "STR_793001_002", store_name: "Laitumkhrah Highland Boutique", locality: "Laitumkhrah, Shillong", rating: "4.7 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Laitumkhrah+Shillong", signature: "Highland Winter Knitwear & Korean Maxi Coats" },
    { store_id: "STR_793001_003", store_name: "Cathedral Road Western Bridal Studio", locality: "Cathedral Road, Shillong", rating: "4.9 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Cathedral+Road+Shillong", signature: "Pristine White Lace Gowns & Formal Silk Suits" },
    { store_id: "STR_793001_004", store_name: "Bara Bazar Handloom Centre", locality: "Iewduh (Bara Bazar), Shillong", rating: "4.5 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Bara+Bazar+Shillong", signature: "Traditional Meghalayan Shawls & Wrap Skirts" }
  ],
  "752001": [
    { store_id: "STR_752001_001", store_name: "Grand Road Sambalpuri Handloom House", locality: "Grand Road, Puri", rating: "4.9 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Grand+Road+Puri", signature: "Authentic Sambalpuri Pure Silk Ikat Sarees" },
    { store_id: "STR_752001_002", store_name: "Puri Beach Market Bomkai Emporium", locality: "Golden Beach Road, Puri", rating: "4.7 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Beach+Road+Puri", signature: "Traditional Bomkai Silk Sarees with Temple Borders" },
    { store_id: "STR_752001_003", store_name: "Swargadwar Handloom & Handicraft Hub", locality: "Swargadwar, Puri", rating: "4.6 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Swargadwar+Puri", signature: "Margasira Festive Handloom Kurtis & Tussar Silk" },
    { store_id: "STR_752001_004", store_name: "Temple Road Odia Craft Studio", locality: "Near Jagannath Temple, Puri", rating: "4.8 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Jagannath+Temple+Puri", signature: "Khandua Pata Sarees & Traditional Puja Wear" }
  ],
  "682001": [
    { store_id: "STR_682001_001", store_name: "MG Road Kasavu & Kanjeevaram Saree Palace", locality: "MG Road, Kochi", rating: "4.9 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=MG+Road+Kochi", signature: "Traditional Kerala Kasavu & Kanjeevaram Silk" },
    { store_id: "STR_682001_002", store_name: "Broadway Marine Drive Handloom Emporium", locality: "Marine Drive, Kochi", rating: "4.7 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Marine+Drive+Kochi", signature: "Breezy Pure Linen Kurtas & Coastal Maxi Dresses" },
    { store_id: "STR_682001_003", store_name: "Lulu Mall Designer Ethnic Studio", locality: "Edappally, Kochi", rating: "4.8 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Lulu+Mall+Kochi", signature: "Modern Indo-Western Kerala Bridal Gowns" },
    { store_id: "STR_682001_004", store_name: "Fort Kochi Boho Fashion Boutique", locality: "Fort Kochi, Kochi", rating: "4.8 ⭐", maps_url: "https://www.google.com/maps/search/?api=1&query=Fort+Kochi", signature: "Handcrafted Organic Cotton Tunics & Coastal Wear" }
  ]
};

const CREATOR_CHANNELS_MAP = {
  "800008": ["PatnaFashionDiaries", "BihariBrideStyles", "MaithiliVlogs", "PatnaBoutiqueHunter"],
  "302001": ["JaipurPinkVibes", "RajputiRoyalty", "BandhaniDiaries", "PinkCityHauls"],
  "793001": ["ShillongStyleLab", "KhasiFashionVlogs", "HighlandChic", "PoliceBazarTrends"],
  "752001": ["OdiaHandloomDiaries", "PuriFestiveVlogs", "SambalpuriChic", "UtkalFashionHouse"],
  "682001": ["KochiCoutureVlogs", "MalayaliBrideTrends", "KasavuStyleLab", "CoastalKeralaFashion"]
};

const getRegionalCreatorFallback = (zip) => {
  const zipRecs = REGIONAL_RECOMMENDATIONS[zip]?.top_recommendations || REGIONAL_RECOMMENDATIONS["800008"].top_recommendations;
  const channels = CREATOR_CHANNELS_MAP[zip] || CREATOR_CHANNELS_MAP["800008"];

  return zipRecs.slice(0, 15).map((rec, idx) => {
    const channelName = channels[idx % channels.length];
    const query = encodeURIComponent(`${channelName} ${rec.name} haul`);
    return {
      video_id: `creator_${zip}_${idx + 1}`,
      youtube_video: {
        channel: channelName,
        title: `HUGE ${ZIP_CODES[zip]?.city || 'Regional'} Haul: ${rec.name}`,
        video_url: `https://www.youtube.com/results?search_query=${query}`,
        thumbnail_url: rec.image_url,
        views: `${(15 + (idx * 12)) % 450 + 25}K views`
      },
      matched_product: {
        id: rec.product_id,
        name: rec.name,
        brand: rec.brand,
        price: rec.price,
        image_url: rec.image_url,
        product_url: rec.product_url,
        clip_match_score: `${(rec.scores.vibe_component_pct || 94).toFixed(1)}%`,
        final_score: (rec.scores.final_matching_pct || 95) / 100
      }
    };
  });
};

const getRegionalBoutiqueFallback = (zip) => {
  const zipRecs = REGIONAL_RECOMMENDATIONS[zip]?.top_recommendations || REGIONAL_RECOMMENDATIONS["800008"].top_recommendations;
  const storeDefs = BOUTIQUE_FALLBACK_DEFS[zip] || BOUTIQUE_FALLBACK_DEFS["800008"];

  return storeDefs.map((store, sIdx) => {
    const startIdx = (sIdx * 3) % zipRecs.length;
    const storeDresses = zipRecs.slice(startIdx, startIdx + 4).map((rec) => ({
      id: rec.product_id,
      name: rec.name,
      brand: rec.brand,
      price: rec.price,
      image_url: rec.image_url,
      product_url: rec.product_url,
      final_score: (rec.scores.final_matching_pct || 94) / 100,
      clip_match_score: `${(rec.scores.vibe_component_pct || 95).toFixed(1)}%`,
      category: "Boutique Collection",
      tags: ["ethnic", "festive", "traditional", "boutique"]
    }));

    return {
      store_id: store.store_id,
      store_name: store.store_name,
      locality: store.locality,
      rating: store.rating,
      extracted_visual_trend: store.signature,
      maps_url: store.maps_url,
      store_dresses: storeDresses,
      matched_product: storeDresses[0]
    };
  });
};

const getLocalCatalogImg = (idOrName) => {
  const str = String(idOrName || '1');
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  const idx = (Math.abs(hash) % 60) + 1;
  return `/catalog/catalog_${idx}.jpg`;
};

function App() {
  const [calendarPresets, setCalendarPresets] = useState(REGIONAL_DATE_PRESETS);

  const [activeTab, setActiveTab] = useState('Women'); // 'Men' | 'Women' | 'Kids'
  const [currentZipCode, setCurrentZipCode] = useState("800008");
  const [sliderVal, setSliderVal] = useState(0);
  const [timeTravelVisible, setTimeTravelVisible] = useState(true);
  const [trendsPanelOpen, setTrendsPanelOpen] = useState(false);
  const [trendsPanelTab, setTrendsPanelTab] = useState('youtube');
  const [currentVibe, setCurrentVibe] = useState("coastal_tropical");
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [coPurchaseItems, setCoPurchaseItems] = useState([]);
  const [purchasingId, setPurchasingId] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [lookCompleter, setLookCompleter] = useState({ accessory: null, footwear: null });
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [tempVibe, setTempVibe] = useState("coastal_tropical");
  const [logs, setLogs] = useState([]);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionCart, setSessionCart] = useState([]);
  
  // Dev State variables synced from backend
  const [engineState, setEngineState] = useState("discovery");
  const [timeOffsetHours, setTimeOffsetHours] = useState(0);
  const [manualFestival, setManualFestival] = useState("None");
  const [activeSurgeTab, setActiveSurgeTab] = useState(null);
  const [velocitySurgeData, setVelocitySurgeData] = useState(null);
  
  // Trends Panel State
  const [youtubeData, setYoutubeData] = useState(null);
  const [isYoutubeLoading, setIsYoutubeLoading] = useState(false);
  const [boutiqueData, setBoutiqueData] = useState(null);
  const [isBoutiqueLoading, setIsBoutiqueLoading] = useState(false);
  const [youtubeFetched, setYoutubeFetched] = useState(false);
  const [boutiqueFetched, setBoutiqueFetched] = useState(false);
  const [globalRunwayData, setGlobalRunwayData] = useState(null);
  const [isGlobalRunwayLoading, setIsGlobalRunwayLoading] = useState(false);
  const [globalRunwayFetched, setGlobalRunwayFetched] = useState(false);
  const [globalRunwayFilter, setGlobalRunwayFilter] = useState('all'); // 'all' | 'seoul' | 'paris' | 'tokyo'
  const [expandedSections, setExpandedSections] = useState({ local: false, national: false, global: false });
  const [selectedCreatorIdx, setSelectedCreatorIdx] = useState(0);
  // Seasonal Fashion Studio State
  const [activeSeasonTab, setActiveSeasonTab] = useState('summer');
  const [userOverrodeSeason, setUserOverrodeSeason] = useState(false);
  const [seasonalData, setSeasonalData] = useState(null);
  const [isSeasonalLoading, setIsSeasonalLoading] = useState(false);
  // Zip Code Intelligence (AOV + weather + upcoming events)
  const [zipInsights, setZipInsights] = useState(null);
  
  const consoleEndRef = useRef(null);
  // ── Performance: embedding cache (computed once per session per tag-string) ──
  const embeddingCacheRef = useRef({});
  // ── Performance: recommendation result cache keyed by "zip|date|vibe|state" ──
  const recCacheRef = useRef({});
  // ── Performance: debounce timer ref for slider ──────────────────────────────
  const debounceTimerRef = useRef(null);

  const dateProfiles = calendarPresets[currentZipCode] || calendarPresets["800008"] || [];
  const activeDateProfile = dateProfiles[sliderVal] || dateProfiles[0] || { key: "default", label: "N/A", dateStr: "2026-01-01", event: "N/A", trendingTags: [] };

  const handleConfirmOnboarding = () => {
    setCurrentVibe(tempVibe);
    setShowOnboarding(false);
    logMessage(`Vibe Check vector shifted to '${VIBE_DEFINITIONS[tempVibe]?.name || tempVibe}'. Computing 8-Pillar search space...`, "success");
  };

  const logMessage = (text, type = "info") => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time: timestamp, text, type }]);
  };

  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  useEffect(() => {
    if (!ZIP_CODES[currentZipCode]) {
      setCurrentZipCode("800008");
    }
  }, [currentZipCode]);

  useEffect(() => {
    logMessage("Initializing Myntra PinPulse Unified 8-Pillar Recommender...", "info");
    const activeZip = ZIP_CODES[currentZipCode] || ZIP_CODES["800008"];
    logMessage(`Geographic boundary: ${activeZip.name}.`, "info");
    logMessage("Loaded local fallback catalog database containing 60 items.", "success");
    checkBackendConnection();
    loadDynamicPresets();
    fetchGlobalRunway('all');
  }, []);

  const loadDynamicPresets = async () => {
    try {
      const resCal = await fetch("http://localhost:8000/api/calendar-presets");
      if (resCal.ok) {
        const calData = await resCal.json();
        setCalendarPresets(calData);
        logMessage("Dynamically loaded regional holiday and festival presets from database.", "success");
      }
    } catch (_) { /* Fallback used */ }

    try {
      const resWea = await fetch("http://localhost:8000/api/weather-matrix");
      if (resWea.ok) {
        const weaData = await resWea.json();
        setWeatherMatrix(weaData);
        logMessage("Dynamically loaded local monthly climate rules and materials from database.", "success");
      }
    } catch (_) { /* Fallback used */ }
  };

  const checkBackendConnection = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/system-state");
      if (res.ok) {
        setBackendStatus("connected");
        logMessage("FastAPI application server detected online at http://localhost:8000.", "success");
        syncDevState();
      } else {
        throw new Error();
      }
    } catch {
      setBackendStatus("offline");
      logMessage("FastAPI server offline. Activating client-side vector search & 8-pillar scoring simulator.", "warning");
    }
  };

  const syncDevState = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/dev/state");
      if (res.ok) {
        const data = await res.json();
        setEngineState(data.session.state);
        setSessionCart(data.session.session_cart || []);
        setTimeOffsetHours(data.session.time_offset_hours);
        setManualFestival(data.session.active_festival || "None");
      }
    } catch (e) {
      logger.error("Error syncing dev state: ", e);
    }
  };

  // Reset fetched state when zip code changes
  useEffect(() => {
    setYoutubeData(null);
    setBoutiqueData(null);
    setYoutubeFetched(false);
    setBoutiqueFetched(false);
    setActiveSurgeTab(null);
    setVelocitySurgeData(null);
  }, [currentZipCode]);

  // Re-run recommendations when key inputs change — debounced 120ms
  useEffect(() => {
    if (backendStatus === "checking") return;
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    debounceTimerRef.current = setTimeout(() => {
      updateRecommendations();
    }, 120);
    return () => clearTimeout(debounceTimerRef.current);
  }, [currentZipCode, sliderVal, currentVibe, activeTab, backendStatus]);

  // Fetch Zip Code Intelligence (AOV, weather, upcoming events)
  useEffect(() => {
    const fetchZipInsights = async () => {
      const profile = (calendarPresets[currentZipCode] || calendarPresets['800008'])[sliderVal] ||
                      (calendarPresets[currentZipCode] || calendarPresets['800008'])[0];
      try {
        const res = await fetch(`http://localhost:8000/api/zip-insights?zip_code=${currentZipCode}&date=${profile.dateStr}`);
        if (res.ok) setZipInsights(await res.json());
      } catch (_) { /* backend offline — silently skip */ }
    };
    fetchZipInsights();
  }, [currentZipCode, sliderVal]);

  // Fetch Look Completer mappings when product selection changes
  useEffect(() => {
    if (!selectedProduct) {
      setLookCompleter({ accessory: null, footwear: null });
      setCoPurchaseItems([]);
      return;
    }

    const fetchLookCompleter = async () => {
      try {
        const occasion = activeDateProfile.event_type;
        const res = await fetch(`http://localhost:8000/api/look-completer?product_id=${selectedProduct.id}&occasion_tag=${occasion}`);
        if (res.ok) {
          const data = await res.json();
          setLookCompleter(data);
          if (data.accessory || data.footwear) {
            logMessage(`Look Completer loaded styling recommendations for '${selectedProduct.name}'.`, "success");
          }
        }
      } catch (e) {
        // Local Fallback simulation
        const fallbackMapping = {
          1: { accessory: { id: 124, name: "Heavy kundan necklace set", image_url: "/catalog/catalog_124.jpg" }, footwear: { id: 149, name: "Modern ankle boots for women", image_url: "/catalog/catalog_149.jpg" } },
          2: { accessory: { id: 124, name: "Heavy kundan necklace set", image_url: "/catalog/catalog_124.jpg" }, footwear: { id: 149, name: "Modern ankle boots for women", image_url: "/catalog/catalog_149.jpg" } },
          9: { accessory: { id: 127, name: "Traditional silver anklets", image_url: "/catalog/catalog_127.jpg" }, footwear: { id: 149, name: "Modern ankle boots for women", image_url: "/catalog/catalog_149.jpg" } },
          7: { accessory: { id: 127, name: "Traditional silver anklets", image_url: "/catalog/catalog_127.jpg" }, footwear: null },
          16: { accessory: { id: 127, name: "Traditional silver anklets", image_url: "/catalog/catalog_127.jpg" }, footwear: null },
          97: { accessory: { id: 124, name: "Heavy kundan necklace set", image_url: "/catalog/catalog_124.jpg" }, footwear: { id: 149, name: "Modern ankle boots for women", image_url: "/catalog/catalog_149.jpg" } },
          110: { accessory: { id: 38, name: "Wangala Tribal Beaded Vest", image_url: "/catalog/catalog_38.jpg" }, footwear: { id: 149, name: "Modern ankle boots for women", image_url: "/catalog/catalog_149.jpg" } },
          112: { accessory: { id: 135, name: "Minimalist gold earring set", image_url: "/catalog/catalog_135.jpg" }, footwear: { id: 149, name: "Modern ankle boots for women", image_url: "/catalog/catalog_149.jpg" } }
        };
        const local = fallbackMapping[selectedProduct.id] || { accessory: null, footwear: null };
        setLookCompleter(local);
      }
    };

    const fetchCoPurchases = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/product/${selectedProduct.id}`);
        if (res.ok) {
          const data = await res.json();
          setCoPurchaseItems(data.also_bought || []);
        }
      } catch (e) {
        setCoPurchaseItems([]);
      }
    };

    fetchLookCompleter();
    fetchCoPurchases();
  }, [selectedProduct, activeDateProfile]);

  const handleZipCodeChange = async (e) => {
    const zip = e.target.value;
    setCurrentZipCode(zip);
    setSliderVal(0);
    setExpandedSections({ local: true, national: false, global: false });
    logMessage(`Geographic boundary shifted. Active region: ${ZIP_CODES[zip]?.name || zip}.`, "success");
    if (backendStatus === "connected") {
      try {
        await fetch("http://localhost:8000/api/dev/set-zip", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ zip_code: zip })
        });
        syncDevState();
      } catch (err) {
        logMessage("Failed to sync ZIP with backend dev panel.", "error");
      }
    }
  };

  const handleSliderChange = (e) => {
    const val = parseInt(e.target.value);
    setSliderVal(val);
    const profile = (calendarPresets[currentZipCode] || calendarPresets["800008"])[val] || (calendarPresets[currentZipCode] || calendarPresets["800008"])[0];
    logMessage(`Time slider shifted. Active regional scenario: ${profile.label}.`, "info");
  };

  const updateRecommendations = async () => {
    setIsLoading(true);
    const profile = (calendarPresets[currentZipCode] || calendarPresets["800008"])[sliderVal] || (calendarPresets[currentZipCode] || calendarPresets["800008"])[0];
    const userVibeVector = generateVibeVector(currentVibe);
    const cacheKey = `${currentZipCode}_${profile.dateStr}_${currentVibe}_${engineState}`;

    logMessage(`Scoring recommendations: ${ZIP_CODES[currentZipCode].city} • ${profile.dateStr} • ${currentVibe}`, "info");
    if (backendStatus === "connected") {
      try {
        logMessage("Executing 8-Pillar Scoring Pipeline on FastAPI backend...", "sql");
        const genderParam = activeTab === 'Men' ? 'men' : activeTab === 'Kids' ? 'kids' : 'women';
        const url = `http://localhost:8000/api/products?zip_code=${currentZipCode}&date=${profile.dateStr}&vibe=${currentVibe}&state=${engineState}&gender=${genderParam}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error("API responded with error code");
        
        const data = await response.json();
        if (data.length > 0) {
          recCacheRef.current[cacheKey] = data;
          setProducts(data);
          logMessage(`Scoring Engine: ${data.length} ${genderParam} products ranked for ${ZIP_CODES[currentZipCode].city}.`, "success");
          const stillExists = data.find(p => selectedProduct && p.id === selectedProduct.id);
          setSelectedProduct(stillExists || data[0]);
        } else {
          logMessage(`Backend returned 0 results for ${genderParam}. Using local calculator.`, "warning");
          runLocalRecommendationCalculator(profile, userVibeVector);
        }
      } catch (err) {
        logMessage(`API call failed: ${err.message}. Falling back to local calculator.`, "warning");
        runLocalRecommendationCalculator(profile, userVibeVector);
      } finally {
        setIsLoading(false);
      }
    } else {
      runLocalRecommendationCalculator(profile, userVibeVector);
      setIsLoading(false);
    }
  };

  const fetchYoutubeTrends = async (zip) => {
    setIsYoutubeLoading(true);
    const targetZip = zip || currentZipCode;
    logMessage("Loading YouTube creator trends...", "info");
    try {
      const res = await fetch(`http://localhost:8000/api/trends/youtube?zip_code=${targetZip}`);
      if (res.ok) {
        const data = await res.json();
        const items = Array.isArray(data) ? data : (data.trends || []);
        if (items.length > 0) {
          setYoutubeData(items.slice(0, 15));
          setYoutubeFetched(true);
          setIsYoutubeLoading(false);
          logMessage(`Creator Feed: Loaded top 15 creator videos for ${ZIP_CODES[targetZip]?.city || targetZip}.`, "success");
          return;
        }
      }
    } catch (_) { /* Use fallback */ }

    const fallbackList = getRegionalCreatorFallback(targetZip);
    setYoutubeData(fallbackList.slice(0, 15));
    setYoutubeFetched(true);
    setIsYoutubeLoading(false);
    logMessage(`Creator Feed: Loaded top 15 creator videos for ${ZIP_CODES[targetZip]?.city || targetZip}.`, "success");
  };

  const fetchBoutiques = async (zip) => {
    setIsBoutiqueLoading(true);
    const targetZip = zip || currentZipCode;
    logMessage(`Loading local boutiques for ${ZIP_CODES[targetZip]?.city || 'Local Region'}...`, "info");
    try {
      const res = await fetch(`http://localhost:8000/api/trends/boutiques?zip_code=${targetZip}`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.boutiques && data.boutiques.length > 0) {
          setBoutiqueData(data);
          setBoutiqueFetched(true);
          setIsBoutiqueLoading(false);
          logMessage(`Local Stores: Loaded ${data.boutiques.length} boutiques with mapped dresses.`, "success");
          return;
        }
      }
    } catch (_) { /* Use fallback */ }

    const fallbackBoutiques = getRegionalBoutiqueFallback(targetZip);
    setBoutiqueData({ boutiques: fallbackBoutiques });
    setBoutiqueFetched(true);
    setIsBoutiqueLoading(false);
    logMessage(`Local Stores: Loaded ${fallbackBoutiques.length} physical boutiques with mapped catalog dresses.`, "success");
  };

  const fetchGlobalRunway = async (cityFilter) => {
    setIsGlobalRunwayLoading(true);
    setGlobalRunwayData(null);
    logMessage('Loading Global Runway trends (Tokyo / Paris / Seoul)...', 'info');
    try {
      const url = cityFilter && cityFilter !== 'all'
        ? `http://localhost:8000/api/trends/global?city=${cityFilter}`
        : 'http://localhost:8000/api/trends/global';
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch global trends');
      const data = await res.json();
      setGlobalRunwayData(data);
      setGlobalRunwayFetched(true);
      const totalTrends = Object.values(data.cities || {}).reduce((s, c) => s + (c.trends?.length || 0), 0);
      logMessage(`Global Runway: Loaded ${totalTrends} aspirational style signals.`, 'success');
    } catch (e) {
      logMessage(`Global Runway error: ${e.message}`, 'warning');
      setGlobalRunwayData({ cities: {} });
    } finally {
      setIsGlobalRunwayLoading(false);
    }
  };




  const fetchSeasonalTrends = async (seasonKey) => {
    setIsSeasonalLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/trends/seasonal?season=${seasonKey}`);
      if (!res.ok) throw new Error("Failed to fetch seasonal trends");
      const data = await res.json();
      setSeasonalData(data);
    } catch (e) {
      logMessage(`Seasonal trends error: ${e.message}`, "warning");
    } finally {
      setIsSeasonalLoading(false);
    }
  };

  const handleSeasonTabClick = (seasonKey) => {
    setUserOverrodeSeason(true);
    setActiveSeasonTab(seasonKey);
    fetchSeasonalTrends(seasonKey);
  };



  const handleTabClick = (tab) => {
    setActiveTab(tab);
    if (tab === 'youtube' && !youtubeFetched) {
      fetchYoutubeTrends(currentZipCode);
    }
    if (tab === 'boutiques' && !boutiqueFetched) {
      fetchBoutiques(currentZipCode);
    }
    if (tab === 'global' && !globalRunwayFetched) {
      fetchGlobalRunway(globalRunwayFilter);
    }
  };

  const openTrendsPanel = (tab) => {
    setTrendsPanelTab(tab);
    setTrendsPanelOpen(true);
    handleTabClick(tab);
  };

  const closeTrendsPanel = () => {
    setTrendsPanelOpen(false);
  };

  const runLocalRecommendationCalculator = (profile, userVibeVector) => {
    logMessage("Running recommendation pipeline for active region...", "sql");
    const zipData = REGIONAL_RECOMMENDATIONS[currentZipCode] || REGIONAL_RECOMMENDATIONS["800008"];
    let finalFeed = [];

    if (zipData && zipData.top_recommendations && zipData.top_recommendations.length > 0) {
      finalFeed = zipData.top_recommendations.map(rec => ({
        id: rec.product_id,
        name: rec.name,
        brand: rec.brand,
        price: rec.price,
        image_url: rec.image_url,
        product_url: rec.product_url,
        final_score: rec.scores.final_matching_pct / 100,
        vibe_score: rec.scores.vibe_component_pct / 100,
        creator_score: rec.scores.creator_component_pct / 100,
        boutique_score: rec.scores.boutique_component_pct / 100,
        tags: ["ethnic", "festive", "traditional", "silk"],
        description: rec.name,
        reason_labels: [
          "✨ Regional Cultural Match",
          "🔥 Loved by local creators",
          "🏬 Popular in local boutiques"
        ]
      }));
    } else {
      finalFeed = FALLBACK_PRODUCTS.map(product => ({
        ...product,
        final_score: 0.92,
        reason_labels: ["✨ Recommended For You"]
      }));
    }

    setProducts(finalFeed);
    logMessage(`Loaded ${finalFeed.length} recommendations for ${ZIP_CODES[currentZipCode]?.city || currentZipCode}.`, "success");
    if (finalFeed.length > 0) {
      setSelectedProduct(finalFeed[0]);
    }
  };

  const triggerVibeChange = (vibe) => {
    setCurrentVibe(vibe);
    logMessage(`Shopper style vibe profile changed: '${vibe.toUpperCase()}'.`, "success");
  };

  // Dev Panel Operations

  const handleSetState = async (stateName) => {
    setEngineState(stateName);
    logMessage(`[DEV] Switching State Machine weight context to: ${stateName.toUpperCase()}`, "info");
    if (backendStatus === "connected") {
      try {
        await fetch("http://localhost:8000/api/dev/set-state", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ state: stateName })
        });
        syncDevState();
        updateRecommendations();
      } catch (err) {
        logMessage("Failed to sync state with backend.", "error");
      }
    } else {
      updateRecommendations();
    }
  };

  const handleTimeWarp = async (hours) => {
    setTimeOffsetHours(prev => prev + hours);
    logMessage(`[DEV] Time Warping +${hours} hours forward. Decrementing intent decay...`, "warning");
    if (backendStatus === "connected") {
      try {
        const res = await fetch("http://localhost:8000/api/dev/time-warp", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ hours })
        });
        const data = await res.json();
        logMessage(`[DEV] Backend warp done. Interactions decay adjusted.`, "success");
        syncDevState();
        updateRecommendations();
      } catch (err) {
        logMessage("Failed to execute backend time-warp.", "error");
      }
    } else {
      logMessage("[DEV] Offline. Time warp simulated on client logs.", "success");
    }
  };

  const handleSetFestival = async (festName) => {
    setManualFestival(festName || "None");
    logMessage(`[DEV] Triggering manual festival override: ${festName || 'None'}`, "info");
    if (backendStatus === "connected") {
      try {
        await fetch("http://localhost:8000/api/dev/set-festival", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ festival: festName })
        });
        syncDevState();
        updateRecommendations();
      } catch (err) {
        logMessage("Failed to set festival override on backend.", "error");
      }
    } else {
      updateRecommendations();
    }
  };

  const handleVelocitySurge = async () => {
    logMessage("[DEV] Simulating real-time local velocity checkout surge...", "warning");
    if (backendStatus === "connected") {
      try {
        const res = await fetch("http://localhost:8000/api/dev/velocity-surge", { method: "POST" });
        if (res.ok) {
          const data = await res.json();
          setVelocitySurgeData(data);
          setActiveSurgeTab("surge");
          logMessage(`[DEV] Spiked checkout velocity for local catalog cluster! Theme: ${data.theme}`, "success");
        }
      } catch (err) {
        logMessage("Failed to simulate velocity surge.", "error");
      }
    } else {
      // Local fallback surge
      const data = {
        theme: "Midnight Blue Festive Bodycons & Modern Lehengas",
        products: FALLBACK_PRODUCTS.slice(0, 5),
        log: "[SYSTEM] Local velocity surge simulated on offline fallback list."
      };
      setVelocitySurgeData(data);
      setActiveSurgeTab("surge");
      logMessage(`[DEV] Offline: Simulated surge theme: ${data.theme}`, "success");
    }
  };

  const handleResetSession = async () => {
    logMessage("[DEV] Resetting user session parameters...", "warning");
    if (backendStatus === "connected") {
      try {
        await fetch("http://localhost:8000/api/dev/reset", { method: "POST" });
        syncDevState();
        updateRecommendations();
      } catch (err) {
        logMessage("Failed to reset session on backend.", "error");
      }
    } else {
      setSessionCart([]);
      setEngineState("discovery");
      setTimeOffsetHours(0);
      setManualFestival("None");
      updateRecommendations();
    }
  };

  // Cart operations
  const handleAddToCart = async (pid) => {
    logMessage(`🛒 Adding Product ID ${pid} to session cart...`, "info");
    if (backendStatus === "connected") {
      try {
        const res = await fetch("http://localhost:8000/api/cart/add", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item_id: pid })
        });
        if (res.ok) {
          const data = await res.json();
          setSessionCart(data.cart);
          setEngineState(data.state);
          logMessage(`🛒 Cart updated. Collaborative filtering boosts applied. State shifted to HIGH_INTENT.`, "success");
          updateRecommendations();
        }
      } catch (e) {
        logMessage("Failed to add to backend cart.", "error");
      }
    } else {
      if (!sessionCart.includes(pid)) {
        setSessionCart(prev => [...prev, pid]);
        setEngineState("high_intent");
        logMessage(`🛒 Offline: Added to cart. Collaborative filtering boost simulated on next rank cycle. State shifted to HIGH_INTENT.`, "success");
      }
    }
  };

  const handleRemoveFromCart = async (pid) => {
    logMessage(`🛒 Removing Product ID ${pid} from session cart...`, "info");
    if (backendStatus === "connected") {
      try {
        const res = await fetch("http://localhost:8000/api/cart/remove", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item_id: pid })
        });
        if (res.ok) {
          const data = await res.json();
          setSessionCart(data.cart);
          setEngineState(data.state);
          logMessage(`🛒 Cart updated. Product removed. State reverted to ${data.state.toUpperCase()}.`, "success");
          updateRecommendations();
        }
      } catch (e) {
        logMessage("Failed to remove from backend cart.", "error");
      }
    } else {
      setSessionCart(prev => prev.filter(id => id !== pid));
      if (sessionCart.length <= 1) {
        setEngineState("discovery");
      }
      logMessage(`🛒 Offline: Removed from cart. State reverted.`, "success");
    }
  };

  const handleAddToWishlist = async (pid) => {
    logMessage(`❤️ Adding Product ID ${pid} to wishlist...`, "info");
    if (backendStatus === "connected") {
      try {
        await fetch("http://localhost:8000/api/wishlist/add", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item_id: pid })
        });
        logMessage(`❤️ Wishlist interaction recorded. Exponential decay timer started.`, "success");
        updateRecommendations();
      } catch (e) {
        logMessage("Failed to record wishlist in backend.", "error");
      }
    } else {
      logMessage(`❤️ Wishlist interaction mock recorded on client.`, "success");
    }
  };

  const handleBuyProduct = async (pid) => {
    logMessage(`🛍️ Processing purchase for Product ID ${pid}...`, "info");
    setPurchasingId(pid);

    // Small delay so CSS slide-out animation plays before state clears
    setTimeout(async () => {
      if (backendStatus === "connected") {
        try {
          const res = await fetch("http://localhost:8000/api/buy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_id: pid })
          });
          if (res.ok) {
            logMessage(`✅ Product ID ${pid} purchased! Suppression decay applied — feed reranking...`, "success");
            setShowModal(false);
            setSelectedProduct(null);
            setPurchasingId(null);
            updateRecommendations();
          }
        } catch (e) {
          logMessage("Failed to execute purchase on backend.", "error");
          setPurchasingId(null);
        }
      } else {
        // Offline client-side suppression
        setProducts(prev => prev.filter(p => p.id !== pid));
        logMessage(`✅ Offline: Product ${pid} purchased and suppressed from feed.`, "success");
        setShowModal(false);
        setSelectedProduct(null);
        setPurchasingId(null);
      }
    }, 450);
  };

  const getFestivalBanner = (eventName) => {
    if (!eventName) return '/images/generic_festival_banner.png';
    const evLower = eventName.toLowerCase();
    if (evLower.includes('diwali')) return '/images/diwali_banner.png';
    if (evLower.includes('durga puja') || evLower.includes('dussehra')) return '/images/durga_puja_banner.png';
    if (evLower.includes('wedding') || evLower.includes('marriage') || evLower.includes('convocation') || evLower.includes('pheras') || evLower.includes('gala') || evLower.includes('graduation') || evLower.includes('farewell')) return '/images/wedding_day_banner.png';
    if (evLower.includes('independence day')) return '/images/independence_day_banner.png';
    if (evLower.includes('republic day')) return '/images/republic_day_banner.png';
    if (evLower.includes('holi')) return '/images/holi_banner.png';
    if (evLower.includes('saraswati puja') || evLower.includes('prakash parv') || evLower.includes('panchami')) return '/images/saraswati_puja_banner.png';
    if (evLower.includes('chhath puja')) return '/images/chhath_puja_banner.png';
    if (evLower.includes('onam') || evLower.includes('vishu') || evLower.includes('biennale')) return '/images/onam_vishu_banner.png';
    if (evLower.includes('rath yatra')) return '/images/rath_yatra_banner.png';
    if (evLower.includes('makar sankranti')) return '/images/makar_sankranti_banner.png';
    if (evLower.includes('nuakhai')) return '/images/nuakhai_banner.png';
    return '/images/generic_festival_banner.png';
  };

  // Meticulous classification of National vs Local events per date & zip code
  const getEventBannersForDate = (dateStr, zipCode) => {
    const banners = { national: null, local: null };
    if (!dateStr) return banners;

    // Normalize date string format YYYY-MM-DD
    const dateKey = dateStr.trim();

    // ── 1. NATIONAL FESTIVALS (Pan-India Celebrations) ──────────────────────
    if (dateKey === "2026-10-18" || dateKey.endsWith("-10-18")) {
      banners.national = {
        title: "Durga Puja & Navratri Celebrations 🥻",
        badge: "🇮🇳 NATIONAL FESTIVAL · PAN-INDIA",
        desc: "Nationwide festive surge across India! Pandals, Dandiya nights, and grand ethnic celebrations.",
        tags: ["Festive Silk", "Heavy Embroidered Saree", "Lehenga Choli", "Kurta Sets", "Red & Gold"],
        type: "national",
        bannerImg: "/images/durga_puja_banner.png"
      };
    } else if (dateKey === "2026-11-08" || dateKey.endsWith("-11-08")) {
      banners.national = {
        title: "Diwali Festival of Lights 🪔",
        badge: "🇮🇳 NATIONAL FESTIVAL · PAN-INDIA",
        desc: "Gleaming Deepavali celebrations across India! Premium festive silks, gold zari brocades, and regal sherwanis.",
        tags: ["Gleaming Gold", "Brocade Silk", "Regal Sherwani", "Anarkali", "Maroon Silk"],
        type: "national",
        bannerImg: "/images/diwali_banner.png"
      };
    } else if (dateKey === "2026-03-03" || dateKey.endsWith("-03-03")) {
      banners.national = {
        title: "Holi Festival of Colors 🎨",
        badge: "🇮🇳 NATIONAL FESTIVAL · PAN-INDIA",
        desc: "Joyous spring color festival celebrated across all states! Crisp white cottons, relaxed kurtas, and easy dailywear.",
        tags: ["Pure White Cotton", "Casual Kurti", "Chikan Handloom", "Breathable Linen"],
        type: "national",
        bannerImg: "/images/holi_banner.png"
      };
    } else if (dateKey === "2026-08-15" || dateKey.endsWith("-08-15")) {
      banners.national = {
        title: "79th Independence Day Celebration 🇮🇳",
        badge: "🇮🇳 NATIONAL DAY · PAN-INDIA",
        desc: "Tricolor pride nationwide! Khadi, handloom ethnic wear, saffron & white formal kurtas.",
        tags: ["Tricolor Accent", "Khadi Handloom", "Formal Nehru Jacket", "Saffron White Green"],
        type: "national",
        bannerImg: "/images/independence_day_banner.png"
      };
    } else if (dateKey === "2026-01-26" || dateKey.endsWith("-01-26")) {
      banners.national = {
        title: "Republic Day Parade & Celebrations 🇮🇳",
        badge: "🇮🇳 NATIONAL DAY · PAN-INDIA",
        desc: "National pride parade and ceremonial gatherings across India.",
        tags: ["Formal Ethnic", "Tricolor Wear", "Structure Blazer", "Nehru Jacket"],
        type: "national",
        bannerImg: "/images/republic_day_banner.png"
      };
    }

    // ── 2. LOCAL REGIONAL FESTIVALS (Region-Specific Heritage) ──────────────
    if (zipCode === "800008") { // Patna / Bihar
      if (dateKey === "2026-11-15" || dateKey.endsWith("-11-15")) {
        banners.local = {
          title: "Chhath Puja — Sandhya Arghya 🛕",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Authentic Bihari Mahaparv on the banks of the Ganges! Sacred saffron & yellow sarees, Bhagalpuri silk, and unstitched dhoti sets.",
          tags: ["Saffron Yellow Saree", "Bhagalpuri Tussar", "Madhubani Hand-Painted", "Cotton Dhoti"],
          type: "local",
          bannerImg: "/images/chhath_puja_banner.png"
        };
      } else if (dateKey === "2026-03-22" || dateKey.endsWith("-03-22")) {
        banners.local = {
          title: "Bihar Diwas (Statehood Day) 🏛️",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Celebrating Bihar's rich heritage with artisanal Bhagalpuri tussar silk and traditional weaves.",
          tags: ["Bhagalpuri Silk", "Tussar Kurta", "Nehru Jacket", "Traditional Weave"],
          type: "local",
          bannerImg: "/images/saraswati_puja_banner.png"
        };
      } else if (dateKey === "2026-02-02" || dateKey.endsWith("-02-02")) {
        banners.local = {
          title: "Saraswati Puja / Vasant Panchami 🌾",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Spring festival of learning in Bihar! Bright basanti yellow sarees, georgettes, and yellow kurtis.",
          tags: ["Basanti Yellow Saree", "Georgette Kurti", "Yellow Anklet Set", "Ethnic Kurta"],
          type: "local",
          bannerImg: "/images/saraswati_puja_banner.png"
        };
      } else if (dateKey === "2026-12-10" || dateKey.endsWith("-12-10")) {
        banners.local = {
          title: "Patna Wedding Day — Pheras Rituals 💍",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Peak Bihari wedding season surge! Heavy Banarasi silk sarees, zardozi lehengas, and royal wedding sherwanis.",
          tags: ["Banarasi Crimson Silk", "Heavy Zardozi", "Royal Sherwani", "Gold Brocade"],
          type: "local",
          bannerImg: "/images/wedding_day_banner.png"
        };
      } else if (dateKey === "2026-01-14" || dateKey.endsWith("-01-14")) {
        banners.local = {
          title: "Makar Sankranti Harvest Mela 🌾",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Harvest festival traditions in Bihar with comfortable cotton kurtas and vibrant dailywear.",
          tags: ["Cotton Ethnic", "Casual Kurti", "Yellow Accent"],
          type: "local",
          bannerImg: "/images/makar_sankranti_banner.png"
        };
      }
    } else if (zipCode === "682001") { // Kochi / Kerala
      if (dateKey === "2026-08-27" || dateKey.endsWith("-08-27")) {
        banners.local = {
          title: "Onam Festival — Thiruvonam 🌾",
          badge: "📍 LOCAL REGIONAL SURGE · Fort Kochi (682001)",
          desc: "Grand harvest festival of Kerala! Authentic Kasavu sarees with woven gold tissue borders, Kara mundus, and traditional pookalam attire.",
          tags: ["Kerala Kasavu Saree", "Gold Zari Border", "Men's Kara Mundu", "Off-White & Gold"],
          type: "local",
          bannerImg: "/images/onam_vishu_banner.png"
        };
      } else if (dateKey === "2026-04-14" || dateKey.endsWith("-04-14")) {
        banners.local = {
          title: "Vishu Festival (Malayali New Year) 🌼",
          badge: "📍 LOCAL REGIONAL SURGE · Fort Kochi (682001)",
          desc: "Malayali New Year celebrations! Golden Kani yellow silks, traditional Kasavu weaves, and fresh festival cottons.",
          tags: ["Kasavu Weave", "Vishu Yellow Silk", "Gold Border Mundu", "Traditional Kerala"],
          type: "local",
          bannerImg: "/images/onam_vishu_banner.png"
        };
      } else if (dateKey === "2026-01-20" || dateKey.endsWith("-01-20")) {
        banners.local = {
          title: "Kochi-Muziris Biennale Art Peak 🎨",
          badge: "📍 LOCAL REGIONAL SURGE · Fort Kochi (682001)",
          desc: "Fort Kochi arts & design surge! Sustainable organic linens, artsy boho silhouettes, and coastal summer layers.",
          tags: ["Breezy Linen", "Boho Indigo", "Artsy Midi Dress", "Sustainable Cotton"],
          type: "local",
          bannerImg: "/images/onam_vishu_banner.png"
        };
      } else if (dateKey === "2026-12-27" || dateKey.endsWith("-12-27")) {
        banners.local = {
          title: "Kochi Wedding Day — Thalikettu 💍",
          badge: "📍 LOCAL REGIONAL SURGE · Fort Kochi (682001)",
          desc: "Traditional Kerala wedding ceremony surge! Pure tissue Kasavu sarees and Kanjeevaram silk.",
          tags: ["Tissue Kasavu Silk", "Kanjeevaram Gold", "Kasavu Mundu", "Bridal Cream"],
          type: "local",
          bannerImg: "/images/wedding_day_banner.png"
        };
      }
    } else if (zipCode === "752001") { // Puri / Odisha
      if (dateKey === "2026-07-16" || dateKey === "2026-07-15" || dateKey.endsWith("-07-16") || dateKey.endsWith("-07-15")) {
        banners.local = {
          title: "Puri Rath Yatra Chariot Festival 🚩",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "World-famous Lord Jagannath Grand Chariot Festival! Handwoven Sambalpuri Ikat cotton, saffron yellow temple wear, and Odia weaves.",
          tags: ["Sambalpuri Ikat", "Temple Yellow Cotton", "Odia Handloom", "Pasapalli Weave"],
          type: "local",
          bannerImg: "/images/rath_yatra_banner.png"
        };
      } else if (dateKey === "2026-06-14" || dateKey === "2026-06-15" || dateKey.endsWith("-06-14") || dateKey.endsWith("-06-15")) {
        banners.local = {
          title: "Raja Parba / Raja Sankranti 🌿",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "Unique Odia festival celebrating womanhood and nature! New pastel cotton sarees, Alata-patterned borders, and lightweight handlooms.",
          tags: ["Lightweight Handloom", "Pastel Cotton Saree", "Sambalpuri Kurti", "Fresh Weave"],
          type: "local",
          bannerImg: "/images/nuakhai_banner.png"
        };
      } else if (dateKey === "2026-09-15" || dateKey.endsWith("-09-15")) {
        banners.local = {
          title: "Nuakhai Agricultural Harvest Festival 🌾",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "Western Odisha new crop harvest celebration! Traditional Tussar silk sarees and Sambalpuri Kurta sets.",
          tags: ["Tussar Silk", "Sambalpuri Handloom", "Harvest Earth Tones", "Traditional Odia"],
          type: "local",
          bannerImg: "/images/nuakhai_banner.png"
        };
      } else if (dateKey === "2026-12-20" || dateKey.endsWith("-12-20")) {
        banners.local = {
          title: "Odisha Winter Wedding — Pheras 💍",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "Peak Odia winter wedding season! Heavy Bomkai silk sarees, Tussar brocades, and ceremonial Nehru jacket sets.",
          tags: ["Bomkai Silk Saree", "Tussar Brocade", "Ceremonial Sherwani", "Crimson Red"],
          type: "local",
          bannerImg: "/images/wedding_day_banner.png"
        };
      } else if (dateKey === "2026-01-14" || dateKey.endsWith("-01-14")) {
        banners.local = {
          title: "Makar Sankranti (Makar Mela) 🌾",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "Traditional Odia harvest fair with Tussar silks and yellow cottons.",
          tags: ["Tussar Silk", "Sambalpuri Ikat", "Yellow Cotton"],
          type: "local",
          bannerImg: "/images/makar_sankranti_banner.png"
        };
      }
    } else if (zipCode === "793001") { // Shillong / Meghalaya
      if (dateKey === "2026-01-14" || dateKey.endsWith("-01-14")) {
        banners.local = {
          title: "Shillong Highland Winter Music Fest 🎸",
          badge: "📍 LOCAL REGIONAL SURGE · Shillong (793001)",
          desc: "Highland rock & indie music festival in the misty hills! Heavy woolen knitted cardigans, plaid trench coats, and cozy winter streetwear.",
          tags: ["Highland Woolen", "Knitted Cardigan", "Plaid Trench", "Winter Streetwear"],
          type: "local",
          bannerImg: "/images/winter_banner.png"
        };
      } else if (dateKey === "2026-04-10" || dateKey.endsWith("-04-10")) {
        banners.local = {
          title: "Shad Suk Mynsiem Thanksgiving Festival 🌸",
          badge: "📍 LOCAL REGIONAL SURGE · Shillong (793001)",
          desc: "Khasi Spring Thanksgiving Festival of peaceful hearts! Authentic silk Jainsems, coral gold beaded jewelry, and traditional woven crowns.",
          tags: ["Khasi Silk Jainsem", "Gold Beaded Jewelry", "Traditional Crown", "Spring Silk"],
          type: "local",
          bannerImg: "/images/saraswati_puja_banner.png"
        };
      } else if (dateKey === "2026-05-15" || dateKey.endsWith("-05-15")) {
        banners.local = {
          title: "Shillong Pine Spring Gala 🌲",
          badge: "📍 LOCAL REGIONAL SURGE · Shillong (793001)",
          desc: "Spring gala in the pine hills! Pastel linen maxi dresses, indie boho skirts, and lightweight chic layers.",
          tags: ["Pastel Linen Maxi", "Indie Boho Skirt", "Pine Green Layer", "Spring Chic"],
          type: "local",
          bannerImg: "/images/summer_banner.png"
        };
      } else if (dateKey === "2026-11-10" || dateKey.endsWith("-11-10")) {
        banners.local = {
          title: "Nongkrem Royal Dance Festival (Smit) 🥻",
          badge: "📍 LOCAL REGIONAL SURGE · Shillong (793001)",
          desc: "Royal Khasi harvest dance festival at Smit! Heavy silk brocade Jainsems, gold ornaments, and rich velvet festive tops.",
          tags: ["Brocade Silk Jainsem", "Velvet Festive Top", "Khasi Gold Ornament", "Royal Meghalaya"],
          type: "local",
          bannerImg: "/images/durga_puja_banner.png"
        };
      } else if (dateKey === "2026-11-15" || dateKey.endsWith("-11-15")) {
        banners.local = {
          title: "Wangala 100 Drums Garo Harvest Festival 🥁",
          badge: "📍 LOCAL REGIONAL SURGE · Shillong (793001)",
          desc: "Garo tribe post-harvest 100 Drums festival! Handspun Garo Dakmanda skirts, tribal beaded vests, and traditional headgear.",
          tags: ["Garo Dakmanda Skirt", "Tribal Beaded Vest", "Handwoven Garo", "Harvest Red & Gold"],
          type: "local",
          bannerImg: "/images/nuakhai_banner.png"
        };
      } else if (dateKey === "2026-11-22" || dateKey.endsWith("-11-22")) {
        banners.local = {
          title: "Shillong International Cherry Blossom Festival 🌸",
          badge: "📍 LOCAL REGIONAL SURGE · Shillong (793001)",
          desc: "Pink cherry blossom bloom across Shillong! Floral chiffon gowns, pastel pink knitwear, and indie fashion.",
          tags: ["Cherry Blossom Pink", "Floral Chiffon Gown", "Pastel Knitwear", "Shillong Indie"],
          type: "local",
          bannerImg: "/images/autumn_banner.png"
        };
      } else if (dateKey === "2026-12-25" || dateKey.endsWith("-12-25")) {
        banners.local = {
          title: "Shillong Grand Christmas Solstice 🎄",
          badge: "📍 LOCAL REGIONAL SURGE · Shillong (793001)",
          desc: "Highland Christmas celebrations across Shillong! Cozy red woolen sweaters, velvet evening suits, chic trench coats, and holiday glam.",
          tags: ["Cozy Red Sweater", "Velvet Evening Suit", "Chic Trench Coat", "Highland Christmas"],
          type: "local",
          bannerImg: "/images/winter_banner.png"
        };
      }
    } else if (zipCode === "302001") { // Rajasthan / Jaipur
      if (dateKey === "2026-01-14" || dateKey.endsWith("-01-14")) {
        banners.local = {
          title: "Jaipur International Kite Festival (Makar Sankranti) 🪁",
          badge: "📍 LOCAL REGIONAL SURGE · Jaipur (302001)",
          desc: "Royal Rajasthan Makar Sankranti kite flying mela! Bright yellow Jaipur block print kurtis, cotton Gota Patti suits, and Bandhani dupattas.",
          tags: ["Jaipur Block Print", "Gota Patti Suit", "Bandhani Dupatta", "Bright Yellow Cotton"],
          type: "local",
          bannerImg: "/images/makar_sankranti_banner.png"
        };
      } else if (dateKey === "2026-02-15" || dateKey.endsWith("-02-15")) {
        banners.local = {
          title: "Jaisalmer Desert Festival 🐫",
          badge: "📍 LOCAL REGIONAL SURGE · Rajasthan (302001)",
          desc: "Vibrant Thar desert folk festival! Traditional Bandhani silk lehengas, mirror-work cholis, and silver oxidised jewellery.",
          tags: ["Bandhani Silk Lehenga", "Mirror Work Choli", "Rajasthani Ethnic", "Oxidised Silver"],
          type: "local",
          bannerImg: "/images/diwali_banner.png"
        };
      } else if (dateKey === "2026-03-20" || dateKey.endsWith("-03-20")) {
        banners.local = {
          title: "Jaipur Royal Elephant & Holi Festival 🎨",
          badge: "📍 LOCAL REGIONAL SURGE · Jaipur (302001)",
          desc: "Royal pink city Holi & elephant cultural procession! Bright white Gota Patti kurtas and organic cottons.",
          tags: ["White Gota Patti Kurta", "Rajasthani Bandhani", "Cotton Anarkali", "Festive Colors"],
          type: "local",
          bannerImg: "/images/holi_banner.png"
        };
      } else if (dateKey === "2026-04-04" || dateKey.endsWith("-04-04")) {
        banners.local = {
          title: "Royal Gangaur Festival Procession 🌸",
          badge: "📍 LOCAL REGIONAL SURGE · Jaipur (302001)",
          desc: "Sacred Rajasthani festival honoring Goddess Gauri! Heavy Gota Patti lehenga cholis, royal crimson silks, and gold jewellery.",
          tags: ["Gota Patti Lehenga", "Royal Red Silk", "Rajasthani Bandhani", "Gold Jewellery"],
          type: "local",
          bannerImg: "/images/wedding_day_banner.png"
        };
      } else if (dateKey === "2026-08-12" || dateKey.endsWith("-08-12")) {
        banners.local = {
          title: "Swarn Teej Festival Jaipur 🌿",
          badge: "📍 LOCAL REGIONAL SURGE · Jaipur (302001)",
          desc: "Sawan monsoon Teej celebrations across Jaipur! Traditional green Leheriya sarees, Gota Patti work, and ethnic silk dupattas.",
          tags: ["Green Leheriya Saree", "Gota Patti Work", "Silk Dupatta", "Festive Teej"],
          type: "local",
          bannerImg: "/images/monsoon_banner.png"
        };
      } else if (dateKey === "2026-10-20" || dateKey.endsWith("-10-20")) {
        banners.local = {
          title: "Marwar Folk Music & Dance Festival Jodhpur 🎶",
          badge: "📍 LOCAL REGIONAL SURGE · Rajasthan (302001)",
          desc: "Heritage music and folk dance festival of Jodhpur! Traditional Angrakha kurta sets, mirror-work jackets, and Bandhani silk.",
          tags: ["Angrakha Kurta Set", "Mirror Work Jacket", "Marwar Bandhani", "Heritage Silk"],
          type: "local",
          bannerImg: "/images/durga_puja_banner.png"
        };
      } else if (dateKey === "2026-11-18" || dateKey.endsWith("-11-18")) {
        banners.local = {
          title: "Pushkar Camel Fair & Cultural Night 🐫",
          badge: "📍 LOCAL REGIONAL SURGE · Rajasthan (302001)",
          desc: "World-renowned Pushkar cultural mela! Handwoven Rajasthani cottons, traditional Angrakha suits, and silver craft.",
          tags: ["Rajasthani Handloom", "Angrakha Suit", "Silver Craft", "Pushkar Traditional"],
          type: "local",
          bannerImg: "/images/generic_festival_banner.png"
        };
      }
    }

    // Helper to resolve exact background image for any event
    const getBannerImgForEvent = (eventTitle = "", eventType = "") => {
      const t = eventTitle.toLowerCase();
      if (t.includes("durga") || t.includes("navratri")) return "/images/durga_puja_banner.png";
      if (t.includes("diwali") || t.includes("deepavali")) return "/images/diwali_banner.png";
      if (t.includes("chhath")) return "/images/chhath_puja_banner.png";
      if (t.includes("holi")) return "/images/holi_banner.png";
      if (t.includes("onam") || t.includes("vishu") || t.includes("biennale")) return "/images/onam_vishu_banner.png";
      if (t.includes("rath") || t.includes("chariot")) return "/images/rath_yatra_banner.png";
      if (t.includes("raja") || t.includes("nuakhai")) return "/images/nuakhai_banner.png";
      if (t.includes("sankranti") || t.includes("harvest") || t.includes("makar")) return "/images/makar_sankranti_banner.png";
      if (t.includes("saraswati") || t.includes("vasant") || t.includes("bihar")) return "/images/saraswati_puja_banner.png";
      if (t.includes("independence")) return "/images/independence_day_banner.png";
      if (t.includes("republic")) return "/images/republic_day_banner.png";
      if (t.includes("wedding") || eventType === "wedding_day") return "/images/wedding_day_banner.png";
      if (t.includes("winter") || t.includes("christmas")) return "/images/winter_banner.png";
      if (t.includes("teej") || t.includes("monsoon")) return "/images/monsoon_banner.png";
      if (t.includes("autumn") || t.includes("cherry")) return "/images/autumn_banner.png";
      return "/images/generic_festival_banner.png";
    };

    // Dynamic Guarantee: Ensure active regional banner matches the exact selected ZIP code
    if (!banners.national && !banners.local && activeDateProfile && activeDateProfile.event) {
      let eventTitle = activeDateProfile.event;
      // Sanity Guard: Prevent Patna events (Prakash Parv / Chhath Puja) from bleeding into Rajasthan or Shillong
      if (zipCode === "302001" && (eventTitle.includes("Prakash Parv") || eventTitle.includes("Chhath Puja") || eventTitle.includes("Bihar"))) {
        eventTitle = "Jaipur International Kite Festival (Makar Sankranti)";
      } else if (zipCode === "793001" && (eventTitle.includes("Prakash Parv") || eventTitle.includes("Chhath Puja") || eventTitle.includes("Bihar"))) {
        eventTitle = "Shillong Highland Winter Music Fest";
      }

      banners.local = {
        title: `${eventTitle} 🥻`,
        badge: `📍 LOCAL REGIONAL SURGE · ${ZIP_CODES[zipCode]?.city || 'Regional Dispatch'}`,
        desc: `Active regional demand surge for ${eventTitle}! Local creator and boutique signals engaged.`,
        tags: activeDateProfile.trendingTags || ["Ethnic Wear", "Regional Handloom", "Festive Collection"],
        type: "local",
        bannerImg: getBannerImgForEvent(eventTitle, activeDateProfile.event_type)
      };
    }

    return banners;
  };

  const renderFestivalBanners = () => {
    const banners = getEventBannersForDate(activeDateProfile.dateStr, currentZipCode);

    if (!banners.national && !banners.local) {
      return null;
    }

    return (
      <div className="festival-banners-container" style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
        {/* National Festival Banner */}
        {banners.national && (
          <div>
            <div 
              className={`festival-banner-card national-banner ${expandedSections.national ? 'expanded' : ''}`}
              style={{ 
                cursor: 'pointer',
                backgroundImage: `linear-gradient(135deg, rgba(30, 20, 15, 0.82) 0%, rgba(20, 12, 25, 0.85) 100%), url(${banners.national.bannerImg})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
              onClick={() => setExpandedSections(prev => ({ ...prev, national: !prev.national }))}
            >
              <div className="banner-badge-row">
                <span className="banner-pill national-pill">{banners.national.badge}</span>
                <span className="banner-weight-tag">⚡ 1.5x Festivity Score Weight</span>
              </div>
              <div className="banner-content">
                <div className="banner-text-col">
                  <h2 className="banner-title">{banners.national.title}</h2>
                  <p className="banner-desc">{banners.national.desc}</p>
                  <div className="banner-tags" style={{ justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#fdfdc9' }}>Trending Attire:</span>
                      {banners.national.tags.map((tag, ti) => (
                        <span key={ti} className="banner-tag-pill">{tag}</span>
                      ))}
                    </div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#fdfdc9', background: 'rgba(255,255,255,0.2)', padding: '4px 12px', borderRadius: '12px', whiteSpace: 'nowrap' }}>
                      {expandedSections.national ? '🙈 CLICK TO COLLAPSE ↑' : '✨ CLICK TO EXPLORE DRESSES ↓'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* National Expanded Shelf */}
            {expandedSections.national && (() => {
              const nationalProducts = products.filter(p => 
                !p.is_global_trend && 
                (
                  (p.tags && p.tags.some(t => ["ethnic", "festive", "silk", "traditional", "saree", "lehenga", "kurta", "ceremonial", "gold", "red"].includes(t.toLowerCase()))) ||
                  (p.category && ["Heritage Traditionalist", "Festive Glam"].includes(p.category))
                )
              );
              return (
                <div style={{ marginTop: '14px', background: 'var(--daisy-panel)', padding: '16px', borderRadius: '16px', border: '1px solid rgba(215, 206, 147, 0.4)' }}>
                  <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: 'var(--peach-dark)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    🥻 {banners.national.title} — Festive Collection ({nationalProducts.length} items)
                  </h3>
                  {nationalProducts.length > 0 ? (
                    <div className="horizontal-shelf">
                      {nationalProducts.slice(0, 15).map((product, idx) => renderProductCard(product, idx))}
                    </div>
                  ) : (
                    <p style={{ fontStyle: 'italic', fontSize: '0.85rem', color: 'var(--text-muted)' }}>No products matching {banners.national.title} search space.</p>
                  )}
                </div>
              );
            })()}
          </div>
        )}

        {/* Local Regional Festival Banner */}
        {banners.local && (
          <div>
            <div 
              className={`festival-banner-card local-banner ${expandedSections.local ? 'expanded' : ''}`}
              style={{ 
                cursor: 'pointer',
                backgroundImage: `linear-gradient(135deg, rgba(40, 20, 15, 0.84) 0%, rgba(20, 15, 25, 0.88) 100%), url(${banners.local.bannerImg})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
              onClick={() => setExpandedSections(prev => ({ ...prev, local: !prev.local }))}
            >
              <div className="banner-badge-row">
                <span className="banner-pill local-pill">{banners.local.badge}</span>
                <span className="banner-weight-tag">🌾 Hyperlocal Creator & Boutique Active</span>
              </div>
              <div className="banner-content">
                <div className="banner-text-col">
                  <h2 className="banner-title">{banners.local.title}</h2>
                  <p className="banner-desc">{banners.local.desc}</p>
                  <div className="banner-tags" style={{ justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#fdfdc9' }}>Regional Tags:</span>
                      {banners.local.tags.map((tag, ti) => (
                        <span key={ti} className="banner-tag-pill local-tag">{tag}</span>
                      ))}
                    </div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#fdfdc9', background: 'rgba(255,255,255,0.2)', padding: '4px 12px', borderRadius: '12px', whiteSpace: 'nowrap' }}>
                      {expandedSections.local ? '🙈 CLICK TO COLLAPSE ↑' : '✨ CLICK TO EXPLORE DRESSES ↓'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Local Expanded Shelf */}
            {expandedSections.local && (() => {
              const eventTitleLower = (activeDateProfile.event || "").toLowerCase();
              const isModernEvent = eventTitleLower.includes("christmas") || 
                                   eventTitleLower.includes("music fest") || 
                                   eventTitleLower.includes("biennale") || 
                                   eventTitleLower.includes("gala") || 
                                   eventTitleLower.includes("convocation") || 
                                   eventTitleLower.includes("cherry blossom");
              
              const isTraditionalFestival = (activeDateProfile.isFestive || activeDateProfile.event_type === "festival") && !isModernEvent;
              
              const localProducts = products.filter(p => {
                if (p.is_global_trend) return false;
                
                // STRICT REGIONAL GEOGRAPHIC ISOLATION:
                // Exclude products explicitly assigned to a different region's ZIP code
                const pZips = p.zip_codes || [];
                if (pZips.length > 0 && !pZips.includes(currentZipCode)) return false;
                
                const tagsLower = (p.tags || []).map(t => t.toLowerCase());
                const catLower = (p.category || "").toLowerCase();
                
                // FOR TRADITIONAL ETHNIC FESTIVALS (Chhath Puja, Bihar Diwas, Prakash Parv, Makar Sankranti, Durga Puja, Diwali):
                // Strictly exclude casual hoodies, sweatshirts, denim shirt dresses, tracksuits & shorts!
                if (isTraditionalFestival) {
                  const isNonEthnicCasual = tagsLower.some(t => ["hoodie", "sweatshirt", "athleisure", "tracksuit", "denim", "streetwear", "sporty", "activewear", "rebel", "y2k", "crop", "jogger"].includes(t)) ||
                                            ["urban athleisure", "high-street rebel", "y2k nostalgia", "western"].includes(catLower);
                  
                  const isFestiveOrEthnic = tagsLower.some(t => ["ethnic", "festive", "silk", "traditional", "saree", "lehenga", "kurta", "sherwani", "handloom", "ceremonial", "gold", "red", "yellow", "saffron", "patna", "chhath", "prakash", "local", "regional", "anarkali", "dupatta", "gota_patti", "bandhani", "khasi", "sambalpuri", "bhagalpuri_silk", "kasavu_weave"].includes(t)) ||
                                           ["festive glam", "heritage traditionalist", "earthy handloom", "ethnic", "festive"].includes(catLower);
                  
                  if (isNonEthnicCasual && !isFestiveOrEthnic) return false;
                  return isFestiveOrEthnic;
                }
                
                // FOR MODERN EVENTS (Christmas, Music Fests, Galas, Convocation):
                // Allow modern dresses, suits, blazers, evening gowns, winter cardigans & chic contemporary outfits
                if (isModernEvent) {
                  return (
                    (p.zip_codes && p.zip_codes.includes(currentZipCode)) ||
                    (p.tags && p.tags.some(t => activeDateProfile.trendingTags.includes(t))) ||
                    tagsLower.some(t => ["dress", "gown", "suit", "blazer", "woolen", "cardigan", "velvet", "formal", "chic", "party", "festive"].includes(t))
                  );
                }
                
                return (
                  (p.zip_codes && p.zip_codes.includes(currentZipCode)) ||
                  (p.tags && p.tags.some(t => activeDateProfile.trendingTags.includes(t))) ||
                  (p.tags && (p.tags.includes("local") || p.tags.includes("ethnic") || p.tags.includes("handloom") || p.tags.includes("saree") || p.tags.includes("kurta")))
                );
              });
              return (
                <div style={{ marginTop: '14px', background: 'var(--daisy-panel)', padding: '16px', borderRadius: '16px', border: '1px solid rgba(216, 164, 143, 0.4)' }}>
                  <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: 'var(--peach-dark)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    📍 {banners.local.title} — Regional Dispatch Collection ({localProducts.length} items)
                  </h3>
                  {localProducts.length > 0 ? (
                    <div className="horizontal-shelf">
                      {localProducts.slice(0, 15).map((product, idx) => renderProductCard(product, idx))}
                    </div>
                  ) : (
                    <p style={{ fontStyle: 'italic', fontSize: '0.85rem', color: 'var(--text-muted)' }}>No regional products matching {banners.local.title}.</p>
                  )}
                </div>
              );
            })()}
          </div>
        )}
      </div>
    );
  };

  const renderProductCard = (product, idx) => {
    const tags = product.tags || [];
    const hasWeddingSurge = (activeDateProfile.event_type === "wedding_day") && tags.includes("ceremonial");
    const hasFestiveSurge = activeDateProfile.isFestive && tags.includes("festive") && !hasWeddingSurge;
    const isMicroCreator = tags.includes("micro_creator");
    const isInCart = sessionCart.includes(product.id);
    
    return (
      <div 
        key={product.id} 
        className={`product-card ${selectedProduct && selectedProduct.id === product.id ? 'selected' : ''} ${purchasingId === product.id ? 'card-purchasing' : ''}`}
        onClick={() => {
          setSelectedProduct(product);
          setShowModal(true);
          logMessage(`Opened detail modal for '${product.name}'. Fetching co-purchases & styling shelf...`, "info");
        }}
      >
        <div className="product-card-header" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '8px 12px',
          background: 'var(--daisy-card)',
          borderBottom: '1px solid var(--olive-border)',
          borderTopLeftRadius: '12px',
          borderTopRightRadius: '12px'
        }}>
          <span style={{ fontSize: '0.72rem', fontWeight: '700', color: 'var(--text-muted)' }}>
            Rank {idx + 1}
          </span>
          {product.is_trending && (
            <span style={{
              fontSize: '0.68rem',
              fontWeight: '800',
              color: '#96636a',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '3px',
              textTransform: 'uppercase',
              letterSpacing: '0.04em'
            }}>
              🔥 Trending
            </span>
          )}
        </div>
        
        <div className="product-image-container">
          <img 
            src={product.image_url} 
            alt={product.name} 
            className="product-image"
            onError={(e) => {
              e.target.src = getLocalCatalogImg(product.id || product.name);
            }}
          />
          <div className="score-badge">
            {product.badgeText ? product.badgeText :
             product.clip_match_score ? `✨ ${product.clip_match_score} CLIP Match` :
             product.final_score != null ? `${(product.final_score * 100).toFixed(1)}%` :
             '✨ 92.4% CLIP Match'}
          </div>
          
          {isMicroCreator && (
            <div className="surge-pill" style={{ background: '#A3A380', color: '#faf9f0', top: '8px', left: '8px', bottom: 'auto' }}>
              Micro-Creator 🌾
            </div>
          )}
          
          {hasWeddingSurge && (
            <div className="surge-pill" style={{ background: '#BB8588', color: '#faf9f0', top: '8px', left: '8px', bottom: 'auto' }}>Wedding Surge 💍</div>
          )}
          {hasFestiveSurge && (
            <div className="surge-pill festive" style={{ top: '8px', left: '8px', bottom: 'auto' }}>Festive Surge 🥻</div>
          )}
        </div>
        
        <div className="product-info">
          <p className="product-category" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{product.category}</span>
            {product.zip_codes && product.zip_codes.length > 0 && (
              <span style={{ color: '#96636a', fontWeight: 'bold' }}>LOCAL</span>
            )}
          </p>
          <p style={{ margin: '4px 0', fontSize: '0.95rem', color: '#96636a', fontWeight: 'bold' }}>₹{(product.price || product.estimated_price_inr || ((product.id * 37) % 2500 + 799)).toLocaleString('en-IN')}</p>

          <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
            <button 
              className="onboarding-btn" 
              style={{ flex: 1, padding: '4px 8px', fontSize: '0.75rem', background: isInCart ? '#96636a' : '#BB8588', border: '1px solid rgba(187,133,136,0.30)', color: '#faf9f0' }}
              onClick={(e) => {
                e.stopPropagation();
                if (isInCart) handleRemoveFromCart(product.id);
                else handleAddToCart(product.id);
              }}
            >
              {isInCart ? "🛒 Remove" : "🛒 Add"}
            </button>
            <button 
              className="onboarding-btn"
              style={{ padding: '4px 8px', fontSize: '0.75rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-muted)' }}
              onClick={(e) => {
                e.stopPropagation();
                handleAddToWishlist(product.id);
              }}
            >
              ❤️ Wishlist
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderGlobalTrendCard = (product) => {
    const getGlobalTrendImage = (p) => {
      if (p.image_url) return p.image_url;
      const name = (p.name || p.global_style_archetype || "").toLowerCase();
      if (name.includes("dopamine")) return "/images/global/dopamine_streetwear_1.jpg";
      if (name.includes("french") || name.includes("romantic")) return "/images/global/french_romantic_revival_1.jpg";
      if (name.includes("harajuku") || name.includes("pastel")) return "/images/global/harajuku_pastel_layers_1.jpg";
      if (name.includes("k-drama") || name.includes("kdrama") || name.includes("soft")) return "/images/global/k_drama_soft_aesthetic_1.jpg";
      if (name.includes("parisian") || name.includes("quiet luxury")) return "/images/global/parisian_quiet_luxury_1.jpg";
      if (name.includes("power") || name.includes("tailoring") || name.includes("suit")) return "/images/global/power_femme_tailoring_1.jpg";
      if (name.includes("wabi")) return "/images/global/wabi_sabi_minimalism_1.png";
      if (name.includes("streetwear") || name.includes("seoul")) return "/images/global/genz_seoul_streetwear_1.jpg";
      if (name.includes("clean girl") || name.includes("haenyeo") || name.includes("haneyo")) return "/images/global/haneyo_clean_girl_1.jpg";
      return "/images/global/parisian_quiet_luxury_1.jpg";
    };

    const imgUrl = getGlobalTrendImage(product);
    
    return (
      <div
        key={product.id}
        className="global-trend-card"
        style={{ 
          '--city-color': product.global_primary_color || '#9b6cb5',
          flex: '0 0 260px',
          maxWidth: '260px',
          cursor: 'pointer'
        }}
        onClick={() => {
          setSelectedProduct({
            id: product.id,
            name: product.name,
            price: product.price || 2499,
            category: product.category || "Global Runway",
            image_url: imgUrl,
            description: product.description,
            material: "Silk / Cotton Blend",
            color: product.global_trending_colors?.[0] || "Pastel",
            nature: "Global Trend",
            age_group: "Gen-Z & Millennials",
            tags: product.tags || ["global", "runway", "high_fashion"],
            final_score: product.global_heat_score || 0.92,
            scoring_breakdown: {
              raw_values: {
                personal_vibe_similarity: 0.88,
                creator_trend_match: 0.95,
                local_boutique_match: 0.70,
                festivity_match: 0.60,
                weather_match: 0.80,
                checkout_velocity_score: 0.92,
                intent_score: 0.85,
                cf_score: 0.90
              }
            }
          });
          setShowModal(true);
        }}
      >
        <div className="global-trend-badge">
          <span>{product.global_flag} {product.global_city}</span>
          <span className="global-season-tag">{product.global_season}</span>
        </div>

        {/* Fashion Dress Image */}
        <div className="product-image-container" style={{ margin: '10px 0', height: '340px', width: '100%', borderRadius: '12px', overflow: 'hidden', position: 'relative', background: '#1a1a1a' }}>
          <img 
            src={imgUrl} 
            alt={product.name} 
            className="product-image"
            style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top center' }}
            onError={(e) => {
              e.target.src = getLocalCatalogImg(product.id || product.name);
            }}
          />
        </div>

        <div className="global-trend-archetype">{product.global_style_archetype}</div>
        <h4 className="global-trend-name">{product.name}</h4>
        <p className="global-trend-desc" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{product.description}</p>
        <div className="global-trend-pieces">
          {(product.global_key_pieces || []).slice(0, 2).map((piece, pi) => (
            <span key={pi} className="global-piece-pill">{piece}</span>
          ))}
        </div>
        <div className="global-trend-colors">
          {(product.global_trending_colors || []).slice(0, 4).map((col, ci) => (
            <span key={ci} className="global-color-swatch" title={col}
              style={{ background: col.includes(' ') ? col.split(' ').pop() : col }}>
            </span>
          ))}
          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginLeft: '4px' }}>
            {(product.global_trending_colors || []).slice(0, 2).join(' · ')}
          </span>
        </div>
        <div className="global-trend-footer">
          <span className="global-heat-bar">
            🔥 {((product.global_heat_score || 0) * 100).toFixed(0)}% heat
          </span>
          <span className="global-searches">
            📈 {((product.global_searches_weekly || 0) / 1000000).toFixed(1)}M/wk
          </span>
          <span className="global-runway-cta">View Item →</span>
        </div>
      </div>
    );
  };

  return (
    <div id="root">
      {/* 🌆 Faded Regional City Background Image Layer (Swaps per PIN Code) */}
      <div
        className="city-faded-background"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          pointerEvents: 'none',
          zIndex: 0,
          backgroundImage: `linear-gradient(135deg, rgba(239, 235, 206, 0.84) 0%, rgba(250, 249, 240, 0.88) 100%), url(${CITY_BACKGROUNDS[currentZipCode] || CITY_BACKGROUNDS["800008"]})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          transition: 'background-image 0.8s ease-in-out',
          opacity: 0.90
        }}
      />

      {/* Onboarding Modal */}
      {showOnboarding && (
        <div className="onboarding-modal-overlay">
          <div className="onboarding-modal">
            <div className="onboarding-header">
              <h2>Myntra Onboarding: Visual Vibe Check</h2>
              <p>Choose your style aesthetic to compute your search vector space parameters.</p>
            </div>
            
            <div className="collage-grid">
              {Object.entries(VIBE_DEFINITIONS).map(([key, def]) => (
                <div 
                  key={key} 
                  className={`vibe-card ${tempVibe === key ? 'selected' : ''}`}
                  onClick={() => setTempVibe(key)}
                >
                  <div className="vibe-icon">{def.emoji}</div>
                  <h3 className="vibe-title">{def.name}</h3>
                  <p className="vibe-desc">{def.desc}</p>
                  <div className="vibe-card-select-dot"></div>
                </div>
              ))}
            </div>
            
            <div className="onboarding-footer">
              <button className="confirm-modal-btn" onClick={handleConfirmOnboarding}>
                Enter Vibe Vector Space
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Dashboard Header */}
      <header className="app-header">
        <div className="logo-container">
          <div className="logo-badge">MYNTRA</div>
          <div className="logo-text">
            <h1>PinPulse Tri-Layer Engine</h1>
            <p><span className="live-indicator"></span> Hyperlocal Regional Dispatch Simulator</p>
          </div>
        </div>
        
        {/* Women, Men Navigation Bar */}
        <nav className="tab-navigation-bar" style={{ display: 'flex', gap: '8px', margin: '0 16px' }}>
          {['Women', 'Men'].map(tab => (
            <button
              key={tab}
              id={`tab-btn-${tab.toLowerCase()}`}
              className={`nav-tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '8px 20px',
                borderRadius: '20px',
                fontWeight: '700',
                fontSize: '0.85rem',
                cursor: 'pointer',
                background: activeTab === tab ? 'linear-gradient(135deg, #c69fd5, #824265)' : 'rgba(250,249,240,0.1)',
                color: activeTab === tab ? '#ffffff' : 'rgba(250,249,240,0.85)',
                border: activeTab === tab ? '1px solid #c69fd5' : '1px solid rgba(250,249,240,0.2)',
                transition: 'all 0.2s ease',
                boxShadow: activeTab === tab ? '0 0 10px rgba(198,159,213,0.3)' : 'none'
              }}
            >
              {tab === 'Women' ? '🥻 Women' : '👔 Men'}
            </button>
          ))}
        </nav>

        {/* Selector Panel */}
        <div className="header-meta">
          <div className="meta-pill" style={{ padding: '0px 4px 0px 12px', background: 'rgba(250,249,240,0.15)', border: '1px solid rgba(250,249,240,0.30)' }}>
            <span style={{ fontSize: '0.75rem', color: 'rgba(250, 249, 240, 0.85)' }}>📍 REGION:</span>
            <select 
              value={currentZipCode} 
              onChange={handleZipCodeChange}
              style={{
                background: 'transparent',
                color: 'white',
                border: 'none',
                padding: '4px 8px',
                fontSize: '0.8rem',
                cursor: 'pointer',
                fontWeight: '600',
                outline: 'none'
              }}
            >
              {Object.entries(ZIP_CODES).map(([zip, details]) => (
                <option key={zip} value={zip} style={{ background: 'var(--bg-deep)', color: 'white' }}>
                  {details.name}
                </option>
              ))}
            </select>
          </div>
          

          <div className="meta-pill">
            🛒 Cart: {sessionCart.length}
          </div>
          <div className="meta-pill">
            📅 {activeDateProfile.dateStr}
          </div>

        </div>
      </header>

      {/* Dashboard Content Grid */}
      <div className="dashboard-grid" style={{ display: 'flex', gap: '16px', alignItems: 'flex-start', padding: '16px 20px', width: '100%', maxWidth: '100%', margin: '0 auto', position: 'relative', zIndex: 1 }}>
        
        {/* Left Side: Controller + Grid Feed */}
        <div className="main-feed-panel" style={{ flex: 1, minWidth: 0 }}>
          
          {/* Time-Travel Control Console */}
          <div className="control-card">
            <div className="control-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '15px' }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <h3 className="control-title" style={{ margin: 0 }}>
                  🕒 Time-Traveler Control Panel ({ZIP_CODES[currentZipCode].city})
                </h3>
                <button
                  onClick={() => {
                    const nextVal = !timeTravelVisible;
                    setTimeTravelVisible(nextVal);
                    if (!nextVal) {
                      setTrendsPanelOpen(false);
                    }
                  }}
                  style={{
                    background: 'rgba(163,163,128,0.15)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    borderRadius: '20px',
                    padding: '4px 12px',
                    fontSize: '0.75rem',
                    fontWeight: '700',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    transition: 'all 0.2s'
                  }}
                >
                  {timeTravelVisible ? "👁️ Hide Panel" : "👁️ Show Panel"}
                </button>
              </div>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>

                {/* Local Creator & Boutique Engine: Render ONLY on 'Women' tab */}
                {timeTravelVisible && activeTab === 'Women' && (
                  <>
                    <button
                      id="btn-creator-feed"
                      onClick={() => openTrendsPanel('youtube')}
                      style={{
                        padding: '7px 16px',
                        background: trendsPanelOpen && trendsPanelTab === 'youtube'
                          ? 'linear-gradient(135deg, #c69fd5, #9b6cb5)'
                          : 'rgba(130, 66, 101, 0.08)',
                        color: trendsPanelOpen && trendsPanelTab === 'youtube' ? '#fdfdc9' : '#824265',
                        border: '1px solid rgba(130, 66, 101, 0.3)',
                        borderRadius: '8px',
                        fontSize: '0.8rem',
                        fontWeight: '700',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        whiteSpace: 'nowrap',
                        boxShadow: trendsPanelOpen && trendsPanelTab === 'youtube' ? '0 0 12px rgba(253,253,201,0.25)' : 'none'
                      }}
                    >
                      🎬 Creator Feed
                      {Array.isArray(youtubeData) && (
                        <span style={{
                          background: trendsPanelOpen && trendsPanelTab === 'youtube' ? 'rgba(253,253,201,0.3)' : 'rgba(130, 66, 101, 0.15)',
                          borderRadius: '10px',
                          padding: '1px 7px',
                          fontSize: '0.65rem',
                          fontWeight: 'bold'
                        }}>{youtubeData.length}</span>
                      )}
                    </button>

                    <button
                      id="btn-local-boutiques"
                      onClick={() => openTrendsPanel('boutiques')}
                      style={{
                        padding: '7px 16px',
                        background: trendsPanelOpen && trendsPanelTab === 'boutiques'
                          ? 'linear-gradient(135deg, #c69fd5, #9b6cb5)'
                          : 'rgba(130, 66, 101, 0.08)',
                        color: trendsPanelOpen && trendsPanelTab === 'boutiques' ? '#fdfdc9' : '#824265',
                        border: '1px solid rgba(130, 66, 101, 0.3)',
                        borderRadius: '8px',
                        fontSize: '0.8rem',
                        fontWeight: '700',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        whiteSpace: 'nowrap',
                        boxShadow: trendsPanelOpen && trendsPanelTab === 'boutiques' ? '0 0 12px rgba(253,253,201,0.25)' : 'none'
                      }}
                    >
                      🏪 Local Boutiques
                      {boutiqueData?.boutiques && (
                        <span style={{
                          background: trendsPanelOpen && trendsPanelTab === 'boutiques' ? 'rgba(253,253,201,0.3)' : 'rgba(130, 66, 101, 0.15)',
                          borderRadius: '10px',
                          padding: '1px 7px',
                          fontSize: '0.65rem',
                          fontWeight: 'bold'
                        }}>{boutiqueData.boutiques.length}</span>
                      )}
                    </button>
                  </>
                )}
              </div>
            </div>
            
            {timeTravelVisible && (
              <>
                <div className="slider-container">
                  <input 
                    type="range" 
                    min="0" 
                    max={dateProfiles.length - 1} 
                    value={sliderVal} 
                    onChange={handleSliderChange}
                    className="slider-input"
                  />
                  <div className="slider-labels" style={{ gridTemplateColumns: `repeat(${dateProfiles.length}, 1fr)` }}>
                    {dateProfiles.map((profile, index) => {
                      const shortLabel = profile.label.split('(')[0].trim();
                      return (
                        <span 
                          key={profile.key} 
                          className={`slider-label ${sliderVal === index ? 'active' : ''}`} 
                          onClick={() => handleSliderChange({target:{value:index}})}
                          style={{ fontSize: '0.72rem', fontWeight: sliderVal === index ? 'bold' : '500', whiteSpace: 'nowrap' }}
                          title={profile.label}
                        >
                          {shortLabel}
                        </span>
                      );
                    })}
                  </div>
                </div>
                
                {/* Live Environmental Factors */}
                <div className="env-factors-row">
                  <div className="factor-box">
                    <div className="factor-title">Local Calendar Event</div>
                    <div className="factor-value" style={{fontSize: '0.75rem', color: 'var(--peach-dark)', lineHeight: '1.2'}}>
                      {activeDateProfile.event}
                    </div>
                  </div>
                  <div className="factor-box">
                    <div className="factor-title">Active Surge</div>
                    <div className="factor-value" style={{fontSize: '0.8rem', color: 'var(--peach-dark)'}}>
                      {activeDateProfile.event_type === 'wedding_day' ? 'Wedding Surge 💍' : activeDateProfile.isFestive ? 'Festive Surge 🥻' : 'None'}
                    </div>
                  </div>
                  <div className="factor-box">
                    <div className="factor-title">Avg Order Value</div>
                    <div className="factor-value" style={{ color: 'var(--text-main)', fontWeight: 'bold' }}>
                      {zipInsights ? `₹${zipInsights.average_order_value.toLocaleString('en-IN')}` : '₹...'}
                    </div>
                  </div>
                  <div className="factor-box">
                    <div className="factor-title">Upcoming (7 Days)</div>
                    <div className="factor-value" style={{ fontSize: '0.7rem', color: 'var(--peach-dark)', lineHeight: '1.4' }}>
                      {zipInsights && zipInsights.upcoming_events && zipInsights.upcoming_events.length > 0
                        ? zipInsights.upcoming_events.slice(0, 2).map((ev, i) => (
                            <div key={i} style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--text-main)' }}>
                              📅 {ev.event_name.split('(')[0].trim()}
                            </div>
                          ))
                        : 'No events soon'
                      }
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
          
          {/* Dynamic National & Regional Festival Banners */}
          {renderFestivalBanners()}

          {/* Feed Header - only show surge tab toggle when active */}
          {velocitySurgeData && (
            <div className="feed-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <h2
                  style={{ cursor: 'pointer', opacity: activeSurgeTab === null ? 1 : 0.5 }}
                  onClick={() => setActiveSurgeTab(null)}
                >
                  🛒 Recommendations
                </h2>
                <h2
                  style={{ cursor: 'pointer', opacity: activeSurgeTab === "surge" ? 1 : 0.5, color: '#fdfdc9' }}
                  onClick={() => setActiveSurgeTab("surge")}
                >
                  🔥 Local Surge
                </h2>
              </div>
            </div>
          )}
          
          {/* Product Feed Grid */}
          {isLoading ? (
            <div className="spinner"></div>
          ) : activeSurgeTab === "surge" && velocitySurgeData ? (
            <div>
              <p style={{ margin: '0 0 15px 0', color: '#c69fd5', fontStyle: 'italic' }}>
                🚀 Showing real-time trending products matching the local demand cluster: <strong>{velocitySurgeData.theme}</strong>
              </p>
              <div className="catalog-grid">
                {velocitySurgeData.products.map((product) => (
                  <div key={product.id} className="product-card" style={{ border: '1px solid rgba(198,159,213,0.4)' }}>
                    <div className="surge-pill" style={{ background: '#c69fd5', color: '#120917', top: '10px', left: '10px' }}>Trending 📈</div>
                    <div className="product-image-container">
                      <img 
                        src={product.image_url} 
                        alt={product.name} 
                        className="product-image"
                        onError={(e) => { e.target.src = getLocalCatalogImg(product.id || product.name); }}
                      />
                    </div>
                    <div className="product-info">
                      <p className="product-category">{product.category}</p>
                      <h4 className="product-name">{product.name}</h4>
                      <p style={{ fontSize: '0.85rem', color: '#CD9FBC', fontWeight: 'bold' }}>₹{(product.id * 17) % 3000 + 499}</p>
                      <button className="onboarding-btn" style={{ width: '100%', marginTop: '10px', border: 'none' }} onClick={() => handleAddToCart(product.id)}>
                        🛒 Add to Cart
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div>
              {/* 1. Recommended For You */}
              <div className="section-container">
                {(() => {
                  const recommendedProducts = products.filter(p => {
                    if (p.is_global_trend) return false;
                    return true;
                  });

                  return (
                    <>
                      <h2 className="section-title">
                        ✨ Recommended For You ({VIBE_DEFINITIONS[currentVibe]?.name || 'Personal Vibe'})
                      </h2>
                      {recommendedProducts.length > 0 ? (
                        <div className="horizontal-shelf">
                          {recommendedProducts
                            .slice(0, 15)
                            .map((product, idx) => renderProductCard(product, idx))}
                        </div>
                      ) : (
                        <p style={{ fontStyle: 'italic', fontSize: '0.85rem', color: 'var(--text-muted)' }}>No recommendations matching your active search space.</p>
                      )}
                    </>
                  );
                })()}
              </div>
            </div>
          )}
        </div>

        {/* ───────── RIGHT SIDE: VIBE SPACE PANEL ───────── */}
        <aside style={{
          width: '280px',
          minWidth: '260px',
          flexShrink: 0,
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          paddingTop: '0px'
        }}>

          {/* Vibe Space Header */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(187,133,136,0.18) 0%, rgba(215,206,147,0.18) 100%)',
            border: '1px solid var(--peach-border)',
            borderRadius: '16px',
            padding: '18px 20px 14px 20px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '1.1rem' }}>✨</span>
              <h3 style={{
                margin: 0,
                fontSize: '1rem',
                fontWeight: '800',
                fontFamily: 'var(--font-title)',
                color: 'var(--peach-dark)',
                letterSpacing: '0.3px'
              }}>Your Vibe Space</h3>
            </div>
            <p style={{
              margin: '0 0 0 0',
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              lineHeight: '1.4'
            }}>
              Select your aesthetic to personalise your style vector.
            </p>
          </div>

          {/* 4 Aesthetic Cards */}
          {Object.entries(VIBE_DEFINITIONS).map(([key, def]) => {
            const isActive = currentVibe === key;
            const vibeGradients = {
              universal_traditionalist: 'linear-gradient(145deg, rgba(187,133,136,0.22), rgba(215,206,147,0.22))',
              dark_academia:            'linear-gradient(145deg, rgba(59,53,41,0.22), rgba(90,80,55,0.22))',
              cottagecore:              'linear-gradient(145deg, rgba(163,163,128,0.22), rgba(200,210,160,0.22))',
              grunge_alt:               'linear-gradient(145deg, rgba(120,80,80,0.22), rgba(80,60,80,0.22))',
            };
            const vibeBorders = {
              universal_traditionalist: 'rgba(187,133,136,0.55)',
              dark_academia:            'rgba(90,80,55,0.55)',
              cottagecore:              'rgba(163,163,128,0.55)',
              grunge_alt:               'rgba(120,80,80,0.55)',
            };
            const vibeActiveGlow = {
              universal_traditionalist: '0 0 18px rgba(187,133,136,0.40)',
              dark_academia:            '0 0 18px rgba(90,80,55,0.40)',
              cottagecore:              '0 0 18px rgba(163,163,128,0.40)',
              grunge_alt:               '0 0 18px rgba(120,80,80,0.40)',
            };

            return (
              <div
                key={key}
                onClick={() => triggerVibeChange(key)}
                style={{
                  background: isActive ? vibeGradients[key] : 'var(--daisy-card)',
                  border: `1.5px solid ${isActive ? vibeBorders[key] : 'var(--olive-border)'}`,
                  borderRadius: '16px',
                  padding: '16px 18px',
                  cursor: 'pointer',
                  transition: 'all 0.25s ease',
                  boxShadow: isActive ? vibeActiveGlow[key] : '0 2px 8px rgba(0,0,0,0.06)',
                  position: 'relative',
                  overflow: 'hidden',
                }}
                onMouseEnter={e => {
                  if (!isActive) {
                    e.currentTarget.style.background = vibeGradients[key];
                    e.currentTarget.style.borderColor = vibeBorders[key];
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }
                }}
                onMouseLeave={e => {
                  if (!isActive) {
                    e.currentTarget.style.background = 'var(--daisy-card)';
                    e.currentTarget.style.borderColor = 'var(--olive-border)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                {/* Active indicator dot */}
                {isActive && (
                  <div style={{
                    position: 'absolute',
                    top: '12px',
                    right: '12px',
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: 'var(--peach-dark)',
                    boxShadow: '0 0 6px rgba(150,99,106,0.7)',
                    animation: 'pulse 2s infinite'
                  }} />
                )}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '1.5rem', lineHeight: 1 }}>{def.emoji}</span>
                  <div>
                    <p style={{
                      margin: 0,
                      fontSize: '0.82rem',
                      fontWeight: '800',
                      color: isActive ? 'var(--peach-dark)' : 'var(--text-main)',
                      fontFamily: 'var(--font-ui)',
                      lineHeight: 1.2
                    }}>{def.name}</p>
                    {isActive && (
                      <span style={{
                        fontSize: '0.62rem',
                        fontWeight: '700',
                        color: 'var(--peach-dark)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.8px'
                      }}>● ACTIVE</span>
                    )}
                  </div>
                </div>
                <p style={{
                  margin: '0 0 10px 0',
                  fontSize: '0.72rem',
                  color: 'var(--text-muted)',
                  lineHeight: '1.5',
                }}>
                  {def.desc}
                </p>
                {/* Tag chips – show first 4 */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {def.tags.slice(0, 4).map(tag => (
                    <span key={tag} style={{
                      fontSize: '0.62rem',
                      fontWeight: '600',
                      padding: '2px 7px',
                      borderRadius: '8px',
                      background: isActive ? 'rgba(187,133,136,0.2)' : 'var(--olive-faint)',
                      color: isActive ? 'var(--peach-dark)' : 'var(--text-muted)',
                      border: '1px solid var(--olive-border)',
                    }}>#{tag}</span>
                  ))}
                </div>
              </div>
            );
          })}

          {/* Current active vibe summary box */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(215,206,147,0.25) 0%, rgba(187,133,136,0.20) 100%)',
            border: '1px solid var(--clover-border)',
            borderRadius: '16px',
            padding: '14px 18px',
          }}>
            <p style={{ margin: '0 0 6px 0', fontSize: '0.7rem', fontWeight: '800', color: 'var(--olive-dark)', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
              🎯 Active Vector
            </p>
            <p style={{ margin: '0 0 4px 0', fontSize: '0.85rem', fontWeight: '700', color: 'var(--peach-dark)' }}>
              {VIBE_DEFINITIONS[currentVibe]?.emoji} {VIBE_DEFINITIONS[currentVibe]?.name}
            </p>
            <p style={{ margin: 0, fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
              Scoring: 60% Vibe · 20% Creator · 20% Boutique
            </p>
          </div>

        </aside>

      </div>



      {/* ===== PRODUCT DETAIL MODAL ===== */}
      {showModal && selectedProduct && (() => {
        const p = selectedProduct;
        const aov = zipInsights?.average_order_value || 1800;
        const price = p.price || 0;
        const isInCart = sessionCart.includes(p.id);
        const withinBudget = price <= aov * 1.2;
        const scoreBreakdown = p.scoring_breakdown || {};
        const rawVals = scoreBreakdown.raw_values || {};

        return (
          <div
            className="pdp-modal-overlay"
            onClick={() => { setShowModal(false); setSelectedProduct(null); }}
          >
            <div className="pdp-modal" onClick={e => e.stopPropagation()}>

              {/* ── Close Button ── */}
              <button
                className="pdp-modal-close"
                onClick={() => { setShowModal(false); setSelectedProduct(null); }}
              >✕</button>

              {/* ── Top Section: Image + Details ── */}
              <div className="pdp-modal-top">

                {/* Left: Product Image */}
                <div className="pdp-modal-img-wrap">
                  <img
                    src={p.image_url}
                    alt={p.name}
                    className="pdp-modal-img"
                    onError={e => { e.target.src = getLocalCatalogImg(p.id || p.name); }}
                  />
                  <div className="pdp-modal-rank">Rank #{products.findIndex(x => x.id === p.id) + 1}</div>
                  <div className="pdp-modal-score">{(p.final_score * 100).toFixed(1)}% Match</div>
                </div>

                {/* Right: Details Panel */}
                <div className="pdp-modal-details">

                  {/* Category + Budget Badge */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginBottom: '6px' }}>
                    <span className="pdp-category-pill">{p.category}</span>
                    <span className={`pdp-aov-badge ${withinBudget ? 'within-budget' : 'premium-item'}`}>
                      {withinBudget ? `✅ Within ZIP AOV (₹${aov.toLocaleString('en-IN')})` : `💎 Premium Item`}
                    </span>
                  </div>

                  <h2 className="pdp-modal-title">{p.name}</h2>
                  <p className="pdp-modal-price">₹{price.toLocaleString('en-IN')}</p>

                  {/* Tags row */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', margin: '10px 0' }}>
                    {p.material && <span className="pdp-tag-pill">🧵 {p.material}</span>}
                    {p.color && <span className="pdp-tag-pill">🎨 {p.color}</span>}
                    {p.nature && <span className="pdp-tag-pill">✨ {p.nature}</span>}
                    {p.age_group && <span className="pdp-tag-pill">👤 {p.age_group}</span>}
                    {(p.tags || []).slice(0, 4).map(t => (
                      <span key={t} className={`pdp-tag-pill ${activeDateProfile.trendingTags.includes(t) ? 'trending-tag' : ''}`}>#{t}</span>
                    ))}
                  </div>

                  {/* 8-Pillar Score Breakdown */}
                  <div className="pdp-score-grid">
                    <p className="pdp-score-title">📊 8-Pillar Scoring Breakdown</p>
                    {[
                      { label: 'Personal Vibe', val: rawVals.personal_vibe_similarity },
                      { label: 'Creator Trend', val: rawVals.creator_trend_match },
                      { label: 'Local Boutique', val: rawVals.local_boutique_match },
                      { label: 'Festivity', val: rawVals.festivity_match },
                      { label: 'Weather Match', val: rawVals.weather_match },
                      { label: 'Velocity', val: rawVals.checkout_velocity_score },
                      { label: 'Session Intent', val: rawVals.intent_score },
                      { label: 'Co-Purchase CF', val: rawVals.cf_score },
                    ].map(({ label, val }) => (
                      <div key={label} className="pdp-score-row">
                        <span className="pdp-score-label">{label}</span>
                        <div className="pdp-score-bar-bg">
                          <div
                            className="pdp-score-bar-fill"
                            style={{ width: `${Math.min(100, Math.max(0, (val || 0) * 100)).toFixed(1)}%` }}
                          />
                        </div>
                        <span className="pdp-score-pct">{((val || 0) * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>

                  {/* Action Buttons */}
                  <div className="pdp-actions">
                    <button
                      className="pdp-btn-buy"
                      onClick={() => handleBuyProduct(p.id)}
                    >
                      🛍️ Buy Now
                    </button>
                    <button
                      className="pdp-btn-cart"
                      onClick={() => isInCart ? handleRemoveFromCart(p.id) : handleAddToCart(p.id)}
                    >
                      {isInCart ? '🛒 Remove' : '🛒 Add to Cart'}
                    </button>
                    <button
                      className="pdp-btn-wish"
                      onClick={() => handleAddToWishlist(p.id)}
                    >
                      ❤️ Wishlist
                    </button>
                  </div>

                  {/* Complete the Look */}
                  {(lookCompleter.accessory || lookCompleter.footwear) && (
                    <div className="pdp-look-section">
                      <p className="pdp-section-label">👗 Complete the Look</p>
                      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                        {[lookCompleter.accessory, lookCompleter.footwear].filter(Boolean).map(item => (
                          <div key={item.id} className="pdp-look-item">
                            <img
                              src={item.image_url}
                              alt={item.name}
                              className="pdp-look-img"
                              onError={e => { e.target.src = `https://placehold.co/70x90/1a1a2e/c69fd5?text=Look`; }}
                            />
                            <p className="pdp-look-name">{item.name}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* ── Bottom: People Also Bought ── */}
              <div className="pdp-copurchase-section">
                <p className="pdp-section-label">
                  👥 People Also Bought
                  {coPurchaseItems.length > 0 && <span className="pdp-copurchase-count">{coPurchaseItems.length} items</span>}
                </p>
                {coPurchaseItems.length === 0 ? (
                  <p style={{ color: '#64748b', fontSize: '0.82rem' }}>Loading co-purchase recommendations…</p>
                ) : (
                  <div className="pdp-copurchase-shelf">
                    {coPurchaseItems.slice(0, 10).map(item => (
                      <div
                        key={item.id}
                        className="pdp-copurchase-card"
                        onClick={() => {
                          setSelectedProduct({ ...item, scoring_breakdown: {}, final_score: 0, tags: item.tags || [], price: item.price || 0 });
                          logMessage(`Switching modal to co-purchase item: ${item.name}`, 'info');
                        }}
                      >
                        <img
                          src={item.image_url}
                          alt={item.name}
                          className="pdp-copurchase-img"
                          onError={e => { e.target.src = `https://placehold.co/120x160/120917/c69fd5?text=${encodeURIComponent(item.name?.slice(0,6) || 'Item')}`; }}
                        />
                        <p className="pdp-copurchase-name">{item.name}</p>
                        <p className="pdp-copurchase-price">₹{(item.price || 0).toLocaleString('en-IN')}</p>
                        <button
                          className="pdp-copurchase-btn"
                          onClick={e => { e.stopPropagation(); handleAddToCart(item.id); }}
                        >+ Cart</button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

            </div>
          </div>
        );
      })()}

      {/* ===== SLIDE-IN TRENDS PANEL ===== */}
      {trendsPanelOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: 'min(480px, 90vw)',
          background: 'var(--bg-card)',
          borderLeft: '1px solid var(--border-color)',
          zIndex: 999,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '-8px 0 40px rgba(0,0,0,0.5)',
          animation: 'slideInRight 0.25s ease'
        }}>
          {/* Slide-in Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px 18px',
            borderBottom: '1px solid var(--border-color)',
            background: 'var(--bg-app)'
          }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button
                onClick={() => { setTrendsPanelTab('youtube'); handleTabClick('youtube'); }}
                style={{
                  padding: '6px 14px',
                  borderRadius: '20px',
                  border: 'none',
                  background: trendsPanelTab === 'youtube' ? '#824265' : 'rgba(130, 66, 101, 0.08)',
                  color: trendsPanelTab === 'youtube' ? 'white' : '#824265',
                  fontSize: '0.78rem',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                🎬 Creator Feed
              </button>
              <button
                onClick={() => { setTrendsPanelTab('boutiques'); handleTabClick('boutiques'); }}
                style={{
                  padding: '6px 14px',
                  borderRadius: '20px',
                  border: 'none',
                  background: trendsPanelTab === 'boutiques' ? '#5C283C' : 'rgba(92, 40, 60, 0.08)',
                  color: trendsPanelTab === 'boutiques' ? 'white' : '#5C283C',
                  fontSize: '0.78rem',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                🏪 Local Boutiques
              </button>
            </div>
            <button
              onClick={closeTrendsPanel}
              style={{
                padding: '6px 14px',
                background: 'var(--daisy-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-main)',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: '800',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}
            >
              ✕ Close
            </button>
          </div>

          {/* Sub-header: city + refresh */}
          <div style={{ padding: '10px 18px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--daisy-panel)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: '600' }}>
              📍 {ZIP_CODES[currentZipCode].city} · Trends Intelligence
            </span>
            <button
              onClick={() => {
                if (trendsPanelTab === 'youtube') { setYoutubeFetched(false); fetchYoutubeTrends(currentZipCode); }
                if (trendsPanelTab === 'boutiques') { setBoutiqueFetched(false); fetchBoutiques(currentZipCode); }
              }}
              style={{
                padding: '5px 12px',
                background: 'var(--daisy-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-main)',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: '700',
                cursor: 'pointer',
                boxShadow: '0 1px 3px rgba(0,0,0,0.08)'
              }}
            >
              🔄 Refresh
            </button>
          </div>

          {/* Scrollable Content */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px 18px' }}>

            {/* ---- YOUTUBE / CREATOR FEED ---- */}
            {trendsPanelTab === 'youtube' && (
              <>
                {isYoutubeLoading ? (
                  <div className="trends-loading">
                    <div className="spinner" style={{ width: '28px', height: '28px', margin: '0 auto 10px' }}></div>
                    <p style={{ color: '#CD9FBC', fontSize: '0.8rem', margin: 0 }}>Loading creator fashion feeds...</p>
                  </div>
                ) : Array.isArray(youtubeData) && youtubeData.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    
                    {/* Circular Avatar Selector Bar (Grouped by Channel) */}
                    {(() => {
                      const creatorGroups = [];
                      const channelMap = new Map();

                      youtubeData.forEach(item => {
                        const channelName = item.youtube_video?.channel || "Creator";
                        if (!channelMap.has(channelName)) {
                          const groupObj = {
                            channel: channelName,
                            video: item.youtube_video,
                            products: []
                          };
                          channelMap.set(channelName, groupObj);
                          creatorGroups.push(groupObj);
                        }
                        if (item.matched_product) {
                          channelMap.get(channelName).products.push(item.matched_product);
                        }
                      });

                      const safeSelectedIdx = selectedCreatorIdx < creatorGroups.length ? selectedCreatorIdx : 0;
                      const currentGroup = creatorGroups[safeSelectedIdx] || creatorGroups[0];
                      const channel = currentGroup?.channel || "Creator";
                      const channelUrl = currentGroup?.video?.video_url || 
                                         `https://www.youtube.com/results?search_query=${encodeURIComponent(channel + ' fashion')}`;
                      const displayProducts = currentGroup?.products || [];

                      return (
                        <>
                          <div>
                            <p style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--peach-dark)', margin: '0 0 10px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                              🎬 Regional Creators ({creatorGroups.length}) — Click to view reel:
                            </p>
                            <div className="horizontal-shelf" style={{ gap: '14px', paddingBottom: '8px' }}>
                              {creatorGroups.map((group, idx) => {
                                const channelName = group.channel;
                                const initials = channelName
                                  .split(' ')
                                  .filter(Boolean)
                                  .map(n => n[0])
                                  .join('')
                                  .toUpperCase()
                                  .slice(0, 2) || "CR";
                                const isSelected = safeSelectedIdx === idx;
                                
                                return (
                                  <div
                                    key={idx}
                                    onClick={() => setSelectedCreatorIdx(idx)}
                                    style={{
                                      display: 'flex',
                                      flexDirection: 'column',
                                      alignItems: 'center',
                                      gap: '6px',
                                      cursor: 'pointer',
                                      flex: '0 0 auto'
                                    }}
                                  >
                                    <div
                                      style={{
                                        width: '56px',
                                        height: '56px',
                                        borderRadius: '50%',
                                        background: isSelected ? 'linear-gradient(135deg, #BB8588, #D8A48F)' : 'var(--daisy-card)',
                                        border: isSelected ? '3px solid #D7CE93' : '2px solid var(--border-color)',
                                        boxShadow: isSelected ? '0 0 12px rgba(215,206,147,0.6)' : 'none',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        color: isSelected ? '#faf9f0' : 'var(--text-main)',
                                        fontWeight: '800',
                                        fontSize: '1rem',
                                        fontFamily: 'var(--font-title)',
                                        transition: 'all 0.2s ease'
                                      }}
                                    >
                                      {initials}
                                    </div>
                                    <span style={{
                                      fontSize: '0.7rem',
                                      fontWeight: isSelected ? 'bold' : '500',
                                      color: isSelected ? 'var(--peach-dark)' : 'var(--text-muted)',
                                      maxWidth: '78px',
                                      textAlign: 'center',
                                      whiteSpace: 'nowrap',
                                      overflow: 'hidden',
                                      textOverflow: 'ellipsis'
                                    }}>
                                      {channelName}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>

                          {/* Selected Creator Reel */}
                          <div style={{ background: 'var(--daisy-panel)', borderRadius: '16px', padding: '16px', border: '1px solid var(--border-color)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '12px' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                                  🎬 {channel}'s Showcase ({displayProducts.length} CLIP-Matched Outfits)
                                </h4>
                                <a
                                  href={channelUrl}
                                  target="_blank"
                                  rel="noreferrer"
                                  style={{
                                    background: 'rgba(187, 133, 136, 0.15)',
                                    border: '1px solid var(--border-accent)',
                                    color: 'var(--peach-dark)',
                                    padding: '4px 12px',
                                    borderRadius: '20px',
                                    fontSize: '0.75rem',
                                    fontWeight: '700',
                                    textDecoration: 'none',
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    whiteSpace: 'nowrap',
                                    transition: 'all 0.2s ease'
                                  }}
                                >
                                  <svg width="14" height="10" viewBox="0 0 24 17" fill="currentColor" style={{ color: 'var(--peach-dark)' }}>
                                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                                  </svg>
                                  Visit Channel
                                </a>
                              </div>
                              <span style={{ fontSize: '0.72rem', color: 'var(--peach-dark)', fontWeight: 'bold' }}>
                                Scroll Horizontally ➔
                              </span>
                            </div>

                            <div className="horizontal-shelf" style={{ gap: '14px' }}>
                              {displayProducts.map((product, pIdx) => renderProductCard({
                                ...product,
                                badgeText: product.clip_match_score ? `✨ ${product.clip_match_score} CLIP Match` : null
                              }, pIdx))}
                            </div>
                          </div>
                        </>
                      );
                    })()}

                  </div>
                ) : (
                  <div className="trends-empty">
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🎬</div>
                    <p style={{ fontWeight: '600', color: 'var(--text-main)', marginBottom: '4px' }}>Creator Feed loading...</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Fetching regional fashion creator videos</p>
                  </div>
                )}
              </>
            )}

            {/* ---- BOUTIQUES TAB ---- */}
            {trendsPanelTab === 'boutiques' && (
              <>
                {isBoutiqueLoading ? (
                  <div className="trends-loading">
                    <div className="spinner" style={{ width: '28px', height: '28px', margin: '0 auto 10px' }}></div>
                    <p style={{ color: '#BA9476', fontSize: '0.8rem', margin: 0 }}>Loading local boutique trends...</p>
                  </div>
                ) : boutiqueData?.boutiques?.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {boutiqueData.boutiques.map((store, idx) => {
                      const shopDresses = store.store_dresses && store.store_dresses.length > 0 
                        ? store.store_dresses 
                        : (store.matched_product ? [store.matched_product] : []);
                      const mapsUrl = store.maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(store.store_name + ' ' + ZIP_CODES[currentZipCode]?.city)}`;

                      return (
                        <div key={store.store_id || idx} style={{ background: 'var(--daisy-panel)', borderRadius: '16px', padding: '16px', border: '1px solid var(--border-color)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '12px' }}>
                            <div>
                              <h3 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-main)' }}>
                                🏪 #{idx + 1} {store.store_name}
                              </h3>
                              <p style={{ margin: '2px 0 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                📍 {store.locality || ZIP_CODES[currentZipCode]?.city} · ⭐ {store.rating || store.simulated_engagement} · #{store.extracted_visual_trend}
                              </p>
                            </div>
                            <a
                              href={mapsUrl}
                              target="_blank"
                              rel="noreferrer"
                              style={{
                                background: 'var(--peach)',
                                color: '#faf9f0',
                                padding: '6px 14px',
                                borderRadius: '20px',
                                fontSize: '0.75rem',
                                fontWeight: 'bold',
                                textDecoration: 'none',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '4px',
                                boxShadow: '0 2px 6px rgba(187,133,136,0.3)',
                                transition: 'all 0.2s ease'
                              }}
                            >
                              🗺️ Google Maps Directions ↗
                            </a>
                          </div>

                          <div className="horizontal-shelf" style={{ gap: '14px' }}>
                            {shopDresses.map((product, pIdx) => renderProductCard(product, pIdx))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="trends-empty">
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🏪</div>
                    <p style={{ fontWeight: '600', color: 'var(--text-main)', marginBottom: '4px' }}>Local Boutiques loading...</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Fetching geo-tagged boutiques near {ZIP_CODES[currentZipCode]?.city}</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
