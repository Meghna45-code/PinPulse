import { useState, useEffect, useRef } from 'react';
import './App.css';
import { FALLBACK_PRODUCTS } from './catalog_fallback';

const getFashionFallbackImage = (title = "Fashion Item", category = "Apparel") => {
  const cleanTitle = String(title || "Fashion Outfit").replace(/["'<>&]/g, '');
  const cleanCat = String(category || "PinPulse Selection").replace(/["'<>&]/g, '');
  const displayTitle = cleanTitle.length > 28 ? cleanTitle.substring(0, 26) + '...' : cleanTitle;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="500" viewBox="0 0 400 500"><defs><linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#2D1226"/><stop offset="50%" stop-color="#4A203E"/><stop offset="100%" stop-color="#1F0B1A"/></linearGradient><linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#D7CE93"/><stop offset="100%" stop-color="#EFEBCE"/></linearGradient></defs><rect width="400" height="500" fill="url(#bg)"/><circle cx="200" cy="180" r="110" fill="none" stroke="rgba(215,206,147,0.25)" stroke-width="2"/><path d="M 170 120 Q 200 150 230 120 L 270 160 L 240 200 L 240 320 L 160 320 L 160 200 L 130 160 Z" fill="none" stroke="url(#gold)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/><text x="200" y="375" font-family="Georgia, serif" font-size="17" font-weight="bold" fill="#EFEBCE" text-anchor="middle">${displayTitle}</text><text x="200" y="405" font-family="sans-serif" font-size="12" font-weight="600" fill="#BB8588" text-anchor="middle" letter-spacing="2">${cleanCat.toUpperCase()}</text><rect x="140" y="425" width="120" height="2" fill="url(#gold)"/></svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
};

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
    { key: "apr_10", label: "Apr 10 (Farewell)", dateStr: "2026-04-10", event: "College Farewell Gala", event_type: "festival", isFestive: true, trendingTags: ["formal", "saree", "suit", "ethnic"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["formal", "ethnic", "fusion"] },
    { key: "jul_15", label: "Jul 15 (Admissions)", dateStr: "2026-07-15", event: "College Admissions Season", event_type: "festival", isFestive: false, trendingTags: ["smart_casual", "breathable_cotton", "modest_fusion", "summer_wear"] },
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
    { key: "apr_10", label: "Apr 10 (Farewell)", dateStr: "2026-04-10", event: "College Farewell Gala", event_type: "festival", isFestive: true, trendingTags: ["pastel", "fusion", "cotton", "lightweight"] },
    { key: "apr_14", label: "Apr 14 (Vishu)", dateStr: "2026-04-14", event: "Vishu Festival (Malayali New Year)", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "yellow", "gold", "cream", "kasavu_weave"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["formal", "elegant", "premium"] },
    { key: "jul_15", label: "Jul 15 (Admissions)", dateStr: "2026-07-15", event: "College Admissions Season", event_type: "festival", isFestive: false, trendingTags: ["monsoon_ready", "contemporary_casual", "dark_tones", "minimalist"] },
    { key: "aug_15", label: "Aug 15 (Independence Day)", dateStr: "2026-08-15", event: "Independence Day Ceremony", event_type: "festival", isFestive: true, trendingTags: ["saffron", "white", "green", "ethnic", "formal", "lightweight"] },
    { key: "aug_27", label: "Aug 27 (Onam Thiruvonam)", dateStr: "2026-08-27", event: "Onam Festival (Thiruvonam)", event_type: "festival", isFestive: true, trendingTags: ["saree", "mundu", "kasavu_weave", "white", "cream", "gold"] },
    { key: "oct_18", label: "Oct 18 (Durga Puja)", dateStr: "2026-10-18", event: "Durga Puja Celebrations", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "minimalist", "cotton"] },
    { key: "nov_8", label: "Nov 8 (Diwali)", dateStr: "2026-11-08", event: "Diwali Lights Festival", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "contemporary_fusion", "fusion", "earth-tones"] },
    { key: "dec_27", label: "Dec 27 (Wedding Day)", dateStr: "2026-12-27", event: "Kochi Wedding Day (Thalikettu)", event_type: "wedding_day", isFestive: true, trendingTags: ["kasavu_weave", "off-white", "cream", "gold"] }
  ],
  "752001": [
    { key: "jan_14", label: "Jan 14 (Makar Sankranti)", dateStr: "2026-01-14", event: "Makar Sankranti (Makar Mela)", event_type: "festival", isFestive: true, trendingTags: ["traditional", "tussar_silk", "yellow", "red", "odisha"] },
    { key: "jan_26", label: "Jan 26 (Republic Day)", dateStr: "2026-01-26", event: "Republic Day Parade", event_type: "festival", isFestive: true, trendingTags: ["smart_casual", "tricolor", "khadi", "white"] },
    { key: "apr_10", label: "Apr 10 (Farewell)", dateStr: "2026-04-10", event: "College Farewell Gala", event_type: "festival", isFestive: true, trendingTags: ["formal", "saree", "pastel", "cotton_silk", "fusion"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["smart_formal", "blazer", "premium_fusion"] },
    { key: "jun_14", label: "Jun 14 (Pahili Raja)", dateStr: "2026-06-14", event: "Pahili Raja (Raja Parba)", event_type: "festival", isFestive: true, trendingTags: ["traditional", "cotton", "pastel", "lightweight", "sambalpuri"] },
    { key: "jun_15", label: "Jun 15 (Raja Sankranti)", dateStr: "2026-06-15", event: "Raja Sankranti Festival", event_type: "festival", isFestive: true, trendingTags: ["traditional", "cotton", "pastel", "sambalpuri", "ethnic"] },
    { key: "jul_15", label: "Jul 15 (Admissions)", dateStr: "2026-07-15", event: "College Admissions Season", event_type: "festival", isFestive: false, trendingTags: ["casual", "denim", "graphic_tee", "breathable_cotton"] },
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
    name: "Universal Traditionalist",
    emoji: "🥻",
    desc: "A versatile, modest, festive, evergreen ethnic aesthetic representing standard traditional wear.",
    tags: ["kurta", "palazzo", "dupatta", "anarkali", "churidar", "saree", "kurti", "pyjama", "nehru-jacket", "rayon", "cotton-blend", "georgette", "chanderi", "art-silk", "chiffon", "block-print", "paisley", "yoke", "foil-print", "ikat", "mustard", "maroon", "emerald", "rani-pink", "ivory"]
  },
  old_money: {
    name: "Old Money",
    emoji: "🍷",
    desc: "Sophisticated, timeless elegance with high-quality fabrics, muted tones, and clean tailoring.",
    tags: ["blazer", "trousers", "tweed", "cashmere", "linen", "structured", "turtleneck", "pleated", "pearl", "neutral", "beige", "navy", "ivory", "monochrome"]
  },
  cottagecore: {
    name: "Cottage Core",
    emoji: "🌾",
    desc: "A romanticized aesthetic focusing on nature, rustic simplicity, floral prints, and vintage silhouettes.",
    tags: ["puff-sleeve", "corset", "prairie-blouse", "tiered-skirt", "maxi-skirt", "cardigan", "slip-dress", "overalls", "linen", "lace", "crochet", "floral", "gingham", "sage-green", "dusty-rose", "butter-yellow"]
  },
  grunge_alt: {
    name: "Alt",
    emoji: "🎸",
    desc: "Rebellious alternative fashion characterized by dark palettes, denim, graphic tees, and streetwear elements.",
    tags: ["band-tee", "distressed-jeans", "combat-boots", "slip-dress", "tights", "cargo", "biker-jacket", "leather", "mesh", "heavy-cotton", "stripes", "crimson", "charcoal", "black"]
  }
};

// ── Scoring weights (client-side fallback mirrors backend logic exactly) ────────
// Vibe SELECTED:     0.4 vibe · 0.3 creator · 0.2 boutique · 0.1 location
// Vibe NOT SELECTED: 0.0 vibe · 0.4 location · 0.3 boutique · 0.3 creator
const SCORING_WEIGHTS = {
  vibe_selected:     { w_vibe: 0.4,  w_creator: 0.3,  w_boutique: 0.2,  w_location: 0.1 },
  vibe_not_selected: { w_vibe: 0.0,  w_creator: 0.3,  w_boutique: 0.3,  w_location: 0.4 },
};
// Default location-based vibe per PIN code (used when no vibe is explicitly selected)
const DEFAULT_LOCATION_VIBE = {
  "800008": "universal_traditionalist",  // Patna
  "682001": "cottagecore",               // Kochi
  "752001": "universal_traditionalist",  // Odisha
  "793001": "grunge_alt",               // Shillong
  "302001": "universal_traditionalist",  // Jaipur
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

// ── Stubs for legacy weather & CF lookup ──────────────────────────────────────
const CF_LOOKUP = {};
const getPresetWeather = () => ({ desc: "Pleasant & Breezy 🍃", temp: "24°C", weather_conditions: "warm_moderate" });
const getWeatherSeason = () => "summer";
const fetchSeasonalTrends = () => {};

function App() {
  const [calendarPresets, setCalendarPresets] = useState(REGIONAL_DATE_PRESETS);
  // Track whether user has explicitly selected a vibe (vs default location-based)
  const [vibeExplicitlySelected, setVibeExplicitlySelected] = useState(false);

  const [activeTab, setActiveTab] = useState('Women'); // 'Men' | 'Women' | 'Kids'
  const [currentZipCode, setCurrentZipCode] = useState("800008");
  const [sliderVal, setSliderVal] = useState(0);
  const [timeTravelVisible, setTimeTravelVisible] = useState(true);
  const [trendsPanelOpen, setTrendsPanelOpen] = useState(false);
  const [trendsPanelTab, setTrendsPanelTab] = useState('youtube');
  const [currentVibe, setCurrentVibe] = useState("universal_traditionalist");
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [coPurchaseItems, setCoPurchaseItems] = useState([]);
  const [purchasingId, setPurchasingId] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [lookCompleter, setLookCompleter] = useState({ accessory: null, footwear: null });
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [tempVibe, setTempVibe] = useState("universal_traditionalist");
  const [logs, setLogs] = useState([]);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionCart, setSessionCart] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  
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
    setVibeExplicitlySelected(true);
    setShowOnboarding(false);
    logMessage(`Vibe selected: '${VIBE_DEFINITIONS[tempVibe]?.name || tempVibe}'. Weights → 0.4 vibe · 0.3 creator · 0.2 boutique · 0.1 location.`, "success");
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
        const url = `http://localhost:8000/api/products?zip_code=${currentZipCode}&date=${profile.dateStr}&vibe=${currentVibe}&state=${engineState}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error("API responded with error code");
        
        const data = await response.json();
        recCacheRef.current[cacheKey] = data;  // cache backend result
        setProducts(data);
        logMessage(`Scoring Engine finished. Retrieved ${data.length} products sorted by composite score.`, "success");
        
        if (data.length > 0) {
          // Keep current selected if still in list, else pick top
          const stillExists = data.find(p => selectedProduct && p.id === selectedProduct.id);
          setSelectedProduct(stillExists || data[0]);
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

  const MOCK_CREATOR_DATA = {
    "800008": [
      { youtube_video: { channel: "Pratibha Shree", title: "Fabric market in Patna | Patna market #fabricmarket #fabric #desginer #patnavlogs #patnamarket", video_url: "https://www.youtube.com/watch?v=U_nkHYPc1ww", thumbnail_url: "https://img.youtube.com/vi/U_nkHYPc1ww/hqdefault.jpg" }, matched_product: FALLBACK_PRODUCTS[0] },
      { youtube_video: { channel: "HER Wardrobe", title: "ZUDIO summer collection #summer #zudio #zudioshoppingvlog #summerfashion #shopping #shoppingvlog", video_url: "https://www.youtube.com/watch?v=FqilEHTE5BA", thumbnail_url: "https://img.youtube.com/vi/FqilEHTE5BA/hqdefault.jpg" }, matched_product: FALLBACK_PRODUCTS[1] },
      { youtube_video: { channel: "Asmita Vlogs", title: "Khetan Market patna #khetanmarket #patna #patnamarket #trending #lahenga #festivewear #ad #bihar", video_url: "https://www.youtube.com/watch?v=55apryEpLEs", thumbnail_url: "https://img.youtube.com/vi/55apryEpLEs/hqdefault.jpg" }, matched_product: FALLBACK_PRODUCTS[2] }
    ],
    "302001": [
      { youtube_video: { channel: "Jaipur Shopping Vlogs", title: "Johari Bazar Jaipur Gota Patti & Bandhani Saree Haul #jaipur", video_url: "https://www.youtube.com/watch?v=J11K9p0Q-1a", thumbnail_url: "https://img.youtube.com/vi/J11K9p0Q-1a/hqdefault.jpg" }, matched_product: FALLBACK_PRODUCTS[3] },
      { youtube_video: { channel: "Royal Rajputana Trends", title: "Royal Gangaur Festival Procession Outfit Haul Jaipur #gangaur", video_url: "https://www.youtube.com/watch?v=R22K0p1Q-2b", thumbnail_url: "https://img.youtube.com/vi/R22K0p1Q-2b/hqdefault.jpg" }, matched_product: FALLBACK_PRODUCTS[4] }
    ],
    "793001": [
      { youtube_video: { channel: "Shillong Style Diaries", title: "Police Bazar Shillong Traditional Khasi Jainsem Haul #shillongfashion", video_url: "https://www.youtube.com/watch?v=S11L8k9P-1a", thumbnail_url: "https://img.youtube.com/vi/S11L8k9P-1a/hqdefault.jpg" }, matched_product: FALLBACK_PRODUCTS[5] }
    ],
    "752001": [
      { youtube_video: { channel: "Payalvlogs", title: "Bapa Pua Renuka Dress Shop,📍CUTTACK", video_url: "https://www.youtube.com/watch?v=erCRv3qln1Q", thumbnail_url: "https://img.youtube.com/vi/erCRv3qln1Q/hqdefault.jpg" }, matched_product: FALLBACK_PRODUCTS[0] }
    ],
    "682001": [
      { youtube_video: { channel: "VIOLET STORE", title: "Pinterest store at Edappally #fashion #boutique #clothing #ytshorts", video_url: "https://www.youtube.com/watch?v=J_F2dzbUXvg", thumbnail_url: "https://img.youtube.com/vi/J_F2dzbUXvg/hqdefault.jpg" }, matched_product: FALLBACK_PRODUCTS[1] }
    ]
  };


  const MOCK_BOUTIQUE_DATA = {
    "800008": {
      boutiques: [
        { store_id: "STR_800008_001", store_name: "Patna Saree Market & Silk House", address: "Frazer Road, Patna, Bihar", rating: 4.6, maps_url: "https://www.google.com/maps/search/?api=1&query=Patna+Saree+Market+Frazer+Road+Patna", video_url: "https://www.youtube.com/watch?v=U_nkHYPc1ww", signature_style: "Traditional Banarasi Silk & Zardozi Wedding Lehengas" },
        { store_id: "STR_800008_002", store_name: "Hathwa Market Boutique Hub", address: "Bakerganj, Patna, Bihar", rating: 4.5, maps_url: "https://www.google.com/maps/search/?api=1&query=Hathwa+Market+Bakerganj+Patna", video_url: "https://www.youtube.com/watch?v=FqilEHTE5BA", signature_style: "Chhath Puja Special Red Silk Sarees & Anarkali Suits" },
        { store_id: "STR_800008_003", store_name: "Khetan Super Market Traditional Store", address: "Birla Mandir Road, Patna, Bihar", rating: 4.7, maps_url: "https://www.google.com/maps/search/?api=1&query=Khetan+Super+Market+Patna", video_url: "https://www.youtube.com/watch?v=55apryEpLEs", signature_style: "Bihari Bridal Dupattas & Ethnic Kurti Sets" }
      ]
    },
    "302001": {
      boutiques: [
        { store_id: "STR_302001_001", store_name: "Johari Bazaar Royal Rajputi Poshak", address: "Johari Bazaar, Jaipur, Rajasthan", rating: 4.8, maps_url: "https://www.google.com/maps/search/?api=1&query=Johari+Bazaar+Jaipur", video_url: "https://www.youtube.com/watch?v=J11K9p0Q-1a", signature_style: "Royal Rajputi Poshak with Heavy Gota Patti & Zari Work" },
        { store_id: "STR_302001_002", store_name: "Bapu Bazaar Bandhani Emporium", address: "Bapu Bazaar, Jaipur, Rajasthan", rating: 4.6, maps_url: "https://www.google.com/maps/search/?api=1&query=Bapu+Bazaar+Jaipur", video_url: "https://www.youtube.com/watch?v=R22K0p1Q-2b", signature_style: "Authentic Jaipur Bandhani & Leheriya Sarees" }
      ]
    },
    "793001": {
      boutiques: [
        { store_id: "STR_793001_001", store_name: "Police Bazar Khasi Traditional Jainsem House", address: "Police Bazar, Shillong, Meghalaya", rating: 4.7, maps_url: "https://www.google.com/maps/search/?api=1&query=Police+Bazar+Shillong", video_url: "https://www.youtube.com/watch?v=S11L8k9P-1a", signature_style: "Pure Ryndia & Silk Jainsem Drapes with Gold Motifs" },
        { store_id: "STR_793001_002", store_name: "Laitumkhrah Highland Boutique", address: "Laitumkhrah Main Road, Shillong, Meghalaya", rating: 4.6, maps_url: "https://www.google.com/maps/search/?api=1&query=Laitumkhrah+Shillong", video_url: "https://www.youtube.com/watch?v=C33L0k1P-3c", signature_style: "Highland Winter Knitwear & Maxi Coats" }
      ]
    },
    "752001": {
      boutiques: [
        { store_id: "STR_752001_001", store_name: "Grand Road Sambalpuri Handloom House", address: "Grand Road, Puri, Odisha", rating: 4.8, maps_url: "https://www.google.com/maps/search/?api=1&query=Grand+Road+Puri+Odisha", video_url: "https://www.youtube.com/watch?v=erCRv3qln1Q", signature_style: "Authentic Sambalpuri Pure Silk Ikat Sarees" }
      ]
    },
    "682001": {
      boutiques: [
        { store_id: "STR_682001_001", store_name: "MG Road Kasavu & Kanjeevaram Saree Palace", address: "MG Road, Kochi, Kerala", rating: 4.8, maps_url: "https://www.google.com/maps/search/?api=1&query=MG+Road+Kochi+Saree", video_url: "https://www.youtube.com/watch?v=J_F2dzbUXvg", signature_style: "Traditional Kerala Kasavu Tissue Sarees & Kanjeevaram" }
      ]
    }
  };

  const fetchYoutubeTrends = async (zip) => {
    setIsYoutubeLoading(true);
    const targetZip = zip || currentZipCode;
    logMessage("Loading YouTube creator trends...", "info");
    try {
      const res = await fetch(`http://localhost:8000/api/trends/youtube?zip_code=${targetZip}`);
      if (!res.ok) throw new Error("API Offline");
      const data = await res.json();
      const items = Array.isArray(data) ? data : (data.trends || []);
      if (items.length > 0) {
        setYoutubeData(items);
      } else {
        setYoutubeData(MOCK_CREATOR_DATA[targetZip] || MOCK_CREATOR_DATA["800008"]);
      }
    } catch (e) {
      logMessage("Using regional creator database cache.", "info");
      setYoutubeData(MOCK_CREATOR_DATA[targetZip] || MOCK_CREATOR_DATA["800008"]);
    } finally {
      setYoutubeFetched(true);
      setIsYoutubeLoading(false);
    }
  };

  const fetchBoutiques = async (zip) => {
    setIsBoutiqueLoading(true);
    const targetZip = zip || currentZipCode;
    logMessage(`Loading local stores for ${ZIP_CODES[targetZip]?.city || 'Local Region'}...`, "info");
    try {
      const res = await fetch(`http://localhost:8000/api/trends/boutiques?zip_code=${targetZip}`);
      if (!res.ok) throw new Error("API Offline");
      const data = await res.json();
      if (data?.boutiques?.length > 0) {
        setBoutiqueData(data);
      } else {
        setBoutiqueData(MOCK_BOUTIQUE_DATA[targetZip] || MOCK_BOUTIQUE_DATA["800008"]);
      }
    } catch (e) {
      logMessage("Using regional boutique database cache.", "info");
      setBoutiqueData(MOCK_BOUTIQUE_DATA[targetZip] || MOCK_BOUTIQUE_DATA["800008"]);
    } finally {
      setBoutiqueFetched(true);
      setIsBoutiqueLoading(false);
    }
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

  const getWeatherSeason = (weatherObj) => {
    if (!weatherObj) return "summer";
    const desc = (weatherObj.desc || "").toLowerCase();
    const tempStr = (weatherObj.temp || "").replace("°C", "").replace("°", "").trim();
    const temp = parseInt(tempStr, 10) || 30;
    if (desc.includes("rain") || desc.includes("monsoon") || weatherObj.rainy) return "monsoon";
    if (desc.includes("cold") || desc.includes("winter") || temp < 20 || weatherObj.cold_wave) return "winter";
    if (desc.includes("pleasant") || desc.includes("autumn") || desc.includes("moderate") || (temp >= 20 && temp <= 27)) return "autumn";
    return "summer";
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

  useEffect(() => {
    const activeWeather = getPresetWeather(currentZipCode, activeDateProfile.dateStr);
    const autoDetectedSeason = getWeatherSeason(activeWeather);
    setActiveSeasonTab(autoDetectedSeason);
    fetchSeasonalTrends(autoDetectedSeason);
  }, [currentZipCode, sliderVal]);

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
    const targetTab = (tab === 'creators' || tab === 'youtube') ? 'youtube' : tab;
    setTrendsPanelTab(targetTab);
    setTrendsPanelOpen(true);
    handleTabClick(targetTab);
  };

  const closeTrendsPanel = () => {
    setTrendsPanelOpen(false);
  };

  // Client-side scoring fallback — mirrors backend 4-pipeline weights exactly
  const runLocalRecommendationCalculator = (profile, userVibeVector) => {
    logMessage("Running client-side pipeline scoring simulation...", "sql");

    const dbZip = ZIP_MAPPING[currentZipCode] || currentZipCode;
    const isWeddingDay = (profile.event_type === "wedding_day");

    // ── Determine scoring mode based on whether user explicitly picked a vibe ──
    const weights = vibeExplicitlySelected
      ? SCORING_WEIGHTS.vibe_selected       // 0.4 vibe · 0.3 creator · 0.2 boutique · 0.1 location
      : SCORING_WEIGHTS.vibe_not_selected;  // 0.0 vibe · 0.4 location · 0.3 boutique · 0.3 creator

    // ── Resolve effective vibe vector ─────────────────────────────────────────
    // When no explicit vibe, use this PIN's default location vibe
    const effectiveVibeKey = vibeExplicitlySelected
      ? currentVibe
      : (DEFAULT_LOCATION_VIBE[currentZipCode] || "universal_traditionalist");
    const effectiveVibeVector = generateVibeVector(effectiveVibeKey);

    // ── Festival context vector (used for festive-tagged items) ───────────────
    const isFestivalActive = profile.isFestive || manualFestival !== "None";
    const festiveContextVector = profile.isFestive
      ? generateVibeVector(profile.trendingTags.join("|") || "ethnic")
      : effectiveVibeVector;

    // ── CF boosts from cart (populated by backend in production) ─────────────
    const activeCFBoosts = {};
    sessionCart.forEach(cid => {
      const recs = CF_LOOKUP[cid]?.recommendations || [];
      recs.forEach(rec => {
        if (!activeCFBoosts[rec.id] || rec.strength > activeCFBoosts[rec.id]) {
          activeCFBoosts[rec.id] = rec.strength;
        }
      });
    });

    const computed = FALLBACK_PRODUCTS.filter(product => {
      if (product.zip_codes && product.zip_codes.length > 0) {
        return product.zip_codes.includes(currentZipCode);
      }
      return true;
    }).map(product => {
      const id = product.id;
      const tags = product.tags;
      const descLower = (product.description || "").toLowerCase();

      // Extract product attributes
      let color = "multi";
      for (let c of ["red", "maroon", "yellow", "gold", "white", "pink", "blue", "magenta", "saffron", "fuchsia", "black", "green"]) {
        if (tags.includes(c) || descLower.includes(c)) { color = c; break; }
      }
      let nature = "casual";
      for (let n of ["ethnic", "festive", "casual", "streetwear", "traditional", "ceremonial"]) {
        if (tags.includes(n) || descLower.includes(n)) { nature = n; break; }
      }
      let category = "Ethnic";
      for (let cat of ["Ethnic", "Western", "Accessory", "Footwear"]) {
        if (tags.includes(cat.toLowerCase()) || descLower.includes(cat.toLowerCase())) { category = cat; break; }
      }
      if (category === "Ethnic" && tags.some(t => ["hoodie", "cargo", "jeans", "jacket"].includes(t))) category = "Western";
      if (tags.some(t => ["earring", "necklace", "anklet", "ring", "sunglasses", "stole"].includes(t))) category = "Accessory";
      if (tags.some(t => ["boots", "mojari", "sandals", "footwear"].includes(t))) category = "Footwear";

      const price = (id * 17) % 3000 + 499;
      const stockLevel = (id * 7) % 50 + 1;
      const isEvergreen = (id % 15 === 0);
      const baselineSales = (id * 3) % 20 + 5;
      const velocityEntry = LOCAL_VELOCITY_CACHE[id] || {};
      const vScore = velocityEntry.velocity_score || 0.0;
      const currentSales = vScore > 0 ? Math.floor(baselineSales * (1.0 + 2.0 * vScore)) : baselineSales + (id % 5);
      const ageGroup = tags.includes("streetwear") ? "gen-z" : "millennial";

      const tagKey = tags.join("|");
      const embedding = embeddingCacheRef.current[tagKey]
        || (embeddingCacheRef.current[tagKey] = generateVibeVector(tagKey));

      // ── Pipeline 2: Vibe score (0.4 when selected, 0.0 otherwise) ────────────
      let productVec = product.vector || product.embedding || embedding;
      let rawCos = calculateCosineSimilarity(effectiveVibeVector, productVec);
      let sVibe = (rawCos + 1) / 2;
      // Tag overlap bonus
      const vibeDef = VIBE_DEFINITIONS[effectiveVibeKey] || {};
      const vibeTags = vibeDef.tags || [];
      const tagOverlap = tags.filter(t => vibeTags.includes(t.toLowerCase())).length;
      if (tagOverlap > 0) sVibe = Math.min(1.0, sVibe + 0.12 * tagOverlap);

      // ── Pipeline 4: Content Creator score (0.3) ───────────────────────────────
      let sCreator = 0.5;
      if (isEvergreen) {
        sCreator = 0.85;
      } else {
        const localCreators = FALLBACK_CREATORS[dbZip] || [];
        let maxC = 0.0;
        localCreators.forEach(c => {
          const sim = (calculateCosineSimilarity(c.vector, embedding) + 1) / 2;
          const penalty = ageGroup === c.demographic ? 1.0 : 0.1;
          maxC = Math.max(maxC, sim * penalty * (c.subscriber_weight || 1.0));
        });
        sCreator = maxC || 0.5;
      }

      // ── Pipeline 3: Local Boutique score (0.2 vibe-selected / 0.3 default) ───
      let sBoutique = 0.5;
      if (isEvergreen) {
        sBoutique = 0.85;
      } else {
        const localStores = FALLBACK_STORES[dbZip] || [];
        let maxS = 0.0;
        localStores.forEach(s => {
          const sim = (calculateCosineSimilarity(s.vector, embedding) + 1) / 2;
          let wRating = Math.max(0.0, (s.rating - 3.0) / 2.0);
          if ((s.review_count || 0) < 50) wRating *= 0.5;
          const catGate = ["ethnic", "occasion", "festive", "traditional"].includes(category.toLowerCase()) ? 1.0 : 0.2;
          maxS = Math.max(maxS, sim * wRating * catGate);
        });
        sBoutique = maxS || 0.5;
      }

      // ── Location-based score (0.1 vibe-selected / 0.4 default) ──────────────
      // Approximated by cosine similarity to the PIN's default vibe vector
      const locationVibeKey = DEFAULT_LOCATION_VIBE[currentZipCode] || "universal_traditionalist";
      const locationVector = generateVibeVector(locationVibeKey);
      let sLocation = (calculateCosineSimilarity(locationVector, embedding) + 1) / 2;

      // ── Final 4-pillar weighted score ─────────────────────────────────────────
      let finalScore =
        weights.w_vibe     * sVibe     +
        weights.w_creator  * sCreator  +
        weights.w_boutique * sBoutique +
        weights.w_location * sLocation;

      // Low stock penalty
      if (stockLevel < 5) finalScore *= 0.1;

      // Wedding day regional boost
      if (isWeddingDay) {
        if (currentZipCode === "800008" && tags.includes("heavy_silk")) finalScore = Math.min(1.0, finalScore + 0.30);
        if (currentZipCode === "682001" && tags.includes("kasavu_weave")) finalScore = Math.min(1.0, finalScore + 0.30);
        if (currentZipCode === "752001" && (tags.includes("sambalpuri") || tags.includes("tussar_silk"))) finalScore = Math.min(1.0, finalScore + 0.30);
      }

      return {
        ...product,
        color,
        nature,
        category,
        price,
        stock_level: stockLevel,
        is_evergreen: isEvergreen,
        baseline_sales: baselineSales,
        current_sales: currentSales,
        units_last_hour: currentSales - baselineSales,
        is_trending: vScore >= 0.75,
        vector_score: sVibe,
        tag_score: sCreator,
        boost_score: sBoutique,
        velocity_score: vScore,
        final_score: finalScore,
        overlap_tags: tags.filter(tag => (profile.trendingTags || []).includes(tag)),
        scoring_breakdown: {
          pipeline2_vibe:     weights.w_vibe     * sVibe,
          pipeline4_creator:  weights.w_creator  * sCreator,
          pipeline3_boutique: weights.w_boutique * sBoutique,
          location_vibe:      weights.w_location * sLocation,
          raw_values: {
            vibe_similarity:    sVibe,
            creator_match:      sCreator,
            boutique_match:     sBoutique,
            location_match:     sLocation,
          }
        },
        reason_labels: [
          isFestivalActive ? `✨ Trending for ${activeDateProfile.event || 'Festival'}` : null,
          sCreator > 0.7  ? `🎬 Loved by local creators` : null,
          sBoutique > 0.7 ? `🏪 Stocked in local boutiques` : null,
          tagOverlap > 1  ? `✨ Matches your vibe` : null,
        ].filter(Boolean)
      };
    }).filter(Boolean);

    computed.sort((a, b) => b.final_score - a.final_score);
    setProducts(computed);
    logMessage(`Client-side scoring ranked ${computed.length} items. Mode: ${vibeExplicitlySelected ? 'vibe-selected' : 'location-default'}.`, "success");
    if (computed.length > 0) setSelectedProduct(computed[0]);
  };

  const triggerVibeChange = (vibe) => {
    setCurrentVibe(vibe);
    setVibeExplicitlySelected(true);  // switch to vibe-selected weight mode
    logMessage(`Vibe selected: '${vibe.toUpperCase()}'. Weights → 0.4 vibe · 0.3 creator · 0.2 boutique · 0.1 location.`, "success");
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
                    renderCarouselShelf(nationalProducts, 20, 8)
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
                const pZips = p.zip_codes || [];
                if (pZips.length > 0 && !pZips.includes(currentZipCode)) return false;
                
                const tagsLower = (p.tags || []).map(t => t.toLowerCase());
                const catLower = (p.category || "").toLowerCase();
                
                if (isTraditionalFestival) {
                  const isNonEthnicCasual = tagsLower.some(t => ["hoodie", "sweatshirt", "athleisure", "tracksuit", "denim", "streetwear", "sporty", "activewear", "rebel", "y2k", "crop", "jogger"].includes(t)) ||
                                            ["urban athleisure", "high-street rebel", "y2k nostalgia", "western"].includes(catLower);
                  
                  const isFestiveOrEthnic = tagsLower.some(t => ["ethnic", "festive", "silk", "traditional", "saree", "lehenga", "kurta", "sherwani", "handloom", "ceremonial", "gold", "red", "yellow", "saffron", "patna", "chhath", "prakash", "local", "regional", "anarkali", "dupatta", "gota_patti", "bandhani", "khasi", "sambalpuri", "bhagalpuri_silk", "kasavu_weave"].includes(t)) ||
                                           ["festive glam", "heritage traditionalist", "earthy handloom", "ethnic", "festive"].includes(catLower);
                  
                  if (isNonEthnicCasual && !isFestiveOrEthnic) return false;
                  return isFestiveOrEthnic;
                }
                
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
                    renderCarouselShelf(localProducts, 20, 8)
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

  const renderCarouselShelf = (productList, maxLimit = 20, initialLimit = 8) => {
    const displayed = productList.slice(0, maxLimit);

    return (
      <div className="carousel-shelf-wrapper">
        <button 
          className="carousel-arrow-btn left-arrow" 
          onClick={(e) => {
            const shelf = e.currentTarget.nextElementSibling;
            if (shelf) shelf.scrollBy({ left: -380, behavior: 'smooth' });
          }} 
          title="Scroll Left"
        >
          ❮
        </button>

        <div className="horizontal-shelf" style={{ scrollBehavior: 'smooth', flex: 1, overflowX: 'auto' }}>
          {displayed.map((product, idx) => renderProductCard(product, idx))}
        </div>

        <button 
          className="carousel-arrow-btn right-arrow" 
          onClick={(e) => {
            const shelf = e.currentTarget.previousElementSibling;
            if (shelf) shelf.scrollBy({ left: 380, behavior: 'smooth' });
          }} 
          title="Scroll Right / Explore Up To 20 Outfits"
        >
          ❯
        </button>
      </div>
    );
  };

  const renderProductCard = (product, idx) => {
    const hasWeddingSurge = (activeDateProfile.event_type === "wedding_day") && product.tags.includes("ceremonial");
    const hasFestiveSurge = activeDateProfile.isFestive && product.tags.includes("festive") && !hasWeddingSurge;
    const isMicroCreator = product.tags.includes("micro_creator");
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
            src={product.image_url || getFashionFallbackImage(product.name, product.category)} 
            alt={product.name} 
            className="product-image"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = getFashionFallbackImage(product.name, product.category);
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
            src={imgUrl || getFashionFallbackImage(product.name, "Global Runway")} 
            alt={product.name} 
            className="product-image"
            style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top center' }}
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = getFashionFallbackImage(product.name, "Global Runway");
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

      {/* Myntra-Style Top Header Bar */}
      <header className="myntra-top-header">
        <div className="myntra-header-left">
          <div className="myntra-logo" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <span className="myntra-logo-icon">📍</span>
            <span className="myntra-logo-title">PinPulse</span>
          </div>
          
          <nav className="myntra-nav-menu">
            {/* MEN (Dummy / Disabled for show) */}
            <div 
              className="myntra-nav-item disabled" 
              title="Men selection is disabled (Defaulting to Women)"
              onClick={() => logMessage("Men section is currently disabled. Default selection is Women.", "info")}
            >
              MEN
            </div>

            {/* WOMEN (Default Selected) */}
            <div className="myntra-nav-item active">
              WOMEN
            </div>

            {/* VIBE CHECK (Dropdown) */}
            <div className="myntra-nav-item dropdown">
              <span className="dropdown-title">VIBE CHECK ▾</span>
              <div className="dropdown-menu">
                {Object.entries(VIBE_DEFINITIONS).map(([key, def]) => (
                  <div 
                    key={key} 
                    className={`dropdown-option ${currentVibe === key ? 'active' : ''}`}
                    onClick={() => {
                      triggerVibeChange(key);
                    }}
                  >
                    <span>{def.emoji}</span>
                    <span>{def.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* LOCAL CONTENT CREATOR (Dropdown / Direct Link) */}
            <div className="myntra-nav-item dropdown">
              <span 
                className="dropdown-title" 
                onClick={() => { setTrendsPanelOpen(true); setTrendsPanelTab('creators'); }}
              >
                LOCAL CREATOR ▾
              </span>
              <div className="dropdown-menu">
                <div 
                  className="dropdown-option" 
                  onClick={() => { setTrendsPanelOpen(true); setTrendsPanelTab('creators'); }}
                >
                  🎬 Creator Insights & Reels
                </div>
              </div>
            </div>

            {/* LOCAL BOUTIQUE (Dropdown / Direct Link) */}
            <div className="myntra-nav-item dropdown">
              <span 
                className="dropdown-title" 
                onClick={() => { setTrendsPanelOpen(true); setTrendsPanelTab('boutiques'); }}
              >
                LOCAL BOUTIQUE ▾
              </span>
              <div className="dropdown-menu">
                <div 
                  className="dropdown-option" 
                  onClick={() => { setTrendsPanelOpen(true); setTrendsPanelTab('boutiques'); }}
                >
                  🏪 Boutique Directory & Tours
                </div>
              </div>
            </div>
          </nav>
        </div>

        {/* Search Bar */}
        <div className="myntra-search-bar">
          <span>🔍</span>
          <input 
            type="text" 
            placeholder="Search for products, brands and more" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Header Right Actions */}
        <div className="myntra-header-right">
          <div className="myntra-region-selector">
            <span>📍 REGION:</span>
            <select 
              value={currentZipCode} 
              onChange={handleZipCodeChange}
            >
              {Object.entries(ZIP_CODES).map(([zip, details]) => (
                <option key={zip} value={zip}>
                  {details.name}
                </option>
              ))}
            </select>
          </div>

          <div className="myntra-action-item">
            <span className="action-icon">👤</span>
            <span className="action-label">Profile</span>
          </div>
          <div className="myntra-action-item" onClick={() => logMessage("Wishlist clicked", "info")}>
            <span className="action-icon">❤️</span>
            <span className="action-label">Wishlist</span>
          </div>
          <div className="myntra-action-item" onClick={() => logMessage("Bag clicked", "info")}>
            <span className="action-icon">🛍️</span>
            <span className="action-label">Bag</span>
            {sessionCart.length > 0 && <span className="cart-badge">{sessionCart.length}</span>}
          </div>
        </div>
      </header>

      {/* Dashboard Content Grid */}
      <div className="dashboard-grid" style={{ display: 'flex', gap: '24px', alignItems: 'flex-start', padding: '24px', maxWidth: '1600px', margin: '0 auto', position: 'relative', zIndex: 1 }}>
        
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

                    <div style={{ width: '1px', height: '28px', background: 'var(--border-color)', margin: '0 4px' }} />
                  </>
                )}

                <button className="onboarding-btn" onClick={() => setShowOnboarding(true)}>
                  ✨ Vibe Check
                </button>
              </div>
            </div>
            
            {timeTravelVisible && (
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
            )}
          </div>
          
          {/* Dynamic National & Regional Festival Banners */}
          {renderFestivalBanners()}

          {/* Product Feed Grid */}
          {isLoading ? (
            <div className="spinner"></div>
          ) : (
            <div>
              {/* 1. Recommended For You */}
              <div className="section-container">
                {(() => {
                  const recommendedProducts = products.filter(p => !p.is_global_trend);
                  const vibeLabel = vibeExplicitlySelected
                    ? (VIBE_DEFINITIONS[currentVibe]?.name || 'Your Vibe')
                    : `📍 ${ZIP_CODES[currentZipCode]?.city || 'Local'} Picks`;
                  return (
                    <>
                      <h2 className="section-title">
                        ✨ Recommended For You · {vibeLabel}
                      </h2>
                      {recommendedProducts.length > 0 ? (
                        renderCarouselShelf(recommendedProducts, 20, 8)
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
                    src={p.image_url || getFashionFallbackImage(p.name, p.category)}
                    alt={p.name}
                    className="pdp-modal-img"
                    onError={e => { e.target.onerror = null; e.target.src = getFashionFallbackImage(p.name, p.category); }}
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
                      const selectedVid = currentGroup?.video;
                      const channelUrl = selectedVid?.video_url || `https://www.youtube.com/results?search_query=${encodeURIComponent(channel + ' fashion')}`;
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

                          {/* Selected Creator Video Reel & Link */}
                          <div style={{ background: 'var(--daisy-panel)', borderRadius: '16px', padding: '20px', border: '1px solid var(--border-color)' }}>
                            <div style={{ display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap' }}>
                              {(() => {
                                const vidId = selectedVid?.video_id || "U_nkHYPc1ww";
                                const thumbPic = selectedVid?.thumbnail_url || `https://img.youtube.com/vi/${vidId}/hqdefault.jpg`;
                                const ytVideoLink = selectedVid?.video_url || `https://www.youtube.com/watch?v=${vidId}`;
                                const creatorChannelLink = selectedVid?.youtube_channel_url || `https://www.youtube.com/results?search_query=${encodeURIComponent(channel + ' fashion')}`;

                                return (
                                  <>
                                    <div style={{ width: '220px', height: '140px', borderRadius: '12px', overflow: 'hidden', flexShrink: 0, position: 'relative', background: '#2D1226' }}>
                                      <img 
                                        src={thumbPic} 
                                        alt={channel} 
                                        style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                                        onError={(e) => {
                                          e.target.onerror = null;
                                          e.target.src = `https://i.ytimg.com/vi/${vidId}/hqdefault.jpg`;
                                        }}
                                      />
                                      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <span style={{ fontSize: '2rem' }}>▶️</span>
                                      </div>
                                    </div>

                                    <div style={{ flex: 1, minWidth: '200px' }}>
                                      <h3 style={{ margin: '0 0 6px 0', fontSize: '1.1rem', color: 'var(--text-main)' }}>
                                        🎬 {channel}
                                      </h3>
                                      <p style={{ margin: '0 0 14px 0', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                                        {selectedVid?.title || `Recent GenZ fashion vlog & outfit showcase in ${ZIP_CODES[currentZipCode]?.city}`}
                                      </p>

                                      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                                        <a
                                          href={ytVideoLink}
                                          target="_blank"
                                          rel="noreferrer"
                                          style={{
                                            background: '#ff3f6c',
                                            color: '#ffffff',
                                            padding: '10px 18px',
                                            borderRadius: '24px',
                                            fontSize: '0.82rem',
                                            fontWeight: '700',
                                            textDecoration: 'none',
                                            display: 'inline-flex',
                                            alignItems: 'center',
                                            gap: '6px',
                                            boxShadow: '0 4px 12px rgba(255,63,108,0.3)'
                                          }}
                                        >
                                          📺 Watch Video on YouTube ↗
                                        </a>

                                        <a
                                          href={creatorChannelLink}
                                          target="_blank"
                                          rel="noreferrer"
                                          style={{
                                            background: 'rgba(130, 66, 101, 0.15)',
                                            color: '#824265',
                                            border: '1px solid rgba(130, 66, 101, 0.3)',
                                            padding: '10px 18px',
                                            borderRadius: '24px',
                                            fontSize: '0.82rem',
                                            fontWeight: '700',
                                            textDecoration: 'none',
                                            display: 'inline-flex',
                                            alignItems: 'center',
                                            gap: '6px'
                                          }}
                                        >
                                          👤 Creator Channel ↗
                                        </a>
                                      </div>
                                    </div>
                                  </>
                                );
                              })()}
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
                      const mapsUrl = store.maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(store.store_name + ' ' + ZIP_CODES[currentZipCode]?.city)}`;
                      const ytVideoUrl = store.video_url || `https://www.youtube.com/results?search_query=${encodeURIComponent(store.store_name + ' store tour ' + ZIP_CODES[currentZipCode]?.city)}`;

                      return (
                        <div key={store.store_id || idx} style={{ background: 'var(--daisy-panel)', borderRadius: '16px', padding: '20px', border: '1px solid var(--border-color)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
                            <div>
                              <h3 style={{ margin: '0 0 6px 0', fontSize: '1.1rem', color: 'var(--text-main)' }}>
                                🏪 #{idx + 1} {store.store_name}
                              </h3>
                              <p style={{ margin: '0 0 8px 0', fontSize: '0.88rem', color: 'var(--text-main)', fontWeight: '600' }}>
                                📍 Location: {store.address || store.locality || ZIP_CODES[currentZipCode]?.city}
                              </p>
                              {store.rating && (
                                <p style={{ margin: '0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                  ⭐ Rating: {store.rating} / 5.0
                                </p>
                              )}
                            </div>

                            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                              <a
                                href={mapsUrl}
                                target="_blank"
                                rel="noreferrer"
                                style={{
                                  background: '#34a853',
                                  color: '#ffffff',
                                  padding: '8px 16px',
                                  borderRadius: '20px',
                                  fontSize: '0.8rem',
                                  fontWeight: 'bold',
                                  textDecoration: 'none',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '6px'
                                }}
                              >
                                🗺️ Google Maps Directions ↗
                              </a>

                              <a
                                href={ytVideoUrl}
                                target="_blank"
                                rel="noreferrer"
                                style={{
                                  background: '#ff0000',
                                  color: '#ffffff',
                                  padding: '8px 16px',
                                  borderRadius: '20px',
                                  fontSize: '0.8rem',
                                  fontWeight: 'bold',
                                  textDecoration: 'none',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '6px'
                                }}
                              >
                                📺 YouTube Store Tour ↗
                              </a>
                            </div>
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
