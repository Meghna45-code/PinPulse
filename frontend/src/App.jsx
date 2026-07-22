import { useState, useEffect, useRef } from 'react';
import './App.css';
import { FALLBACK_PRODUCTS } from './catalog_fallback';

const ZIP_CODES = {
  "682001": { city: "Fort Kochi", state: "Kochi", name: "Kochi (682001)" },
  "752001": { city: "Puri", state: "Odisha", name: "Odisha (752001)" },
  "800008": { city: "Patna City", state: "Patna", name: "Patna (800008)" }
};

// Mapped canonical ZIP codes for backend queries
const BACKEND_ZIP_MAPPED = {
  "800008": "800008",
  "682001": "682001",
  "752001": "752001",
};

// Weather Matrix throughout the year
const WEATHER_MATRIX = {
  "682001": { // Fort Kochi
    1: { desc: "Pleasant & Breezy 🍃", temp: "23°C–31°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    2: { desc: "Breezy & Warm 🍃", temp: "24°C–32°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    3: { desc: "Warm & Sunny ☀️", temp: "25°C–33°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "hot_humid" },
    4: { desc: "Warm & Dry ☀️", temp: "27°C–33°C", cold_wave: false, hot_wave: true, rainy: false, weather_conditions: "hot_humid" },
    5: { desc: "Pre-Monsoon Showers 🌧️", temp: "27°C–31°C", cold_wave: false, hot_wave: true, rainy: true, weather_conditions: "hot_humid" },
    6: { desc: "Cool & Rainy 🌧️", temp: "26°C–29°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    7: { desc: "Monsoon Breezes 🌧️", temp: "25°C–29°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    8: { desc: "Cloudy & Rainy 🌧️", temp: "25°C–29°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    9: { desc: "Pleasant Showers 🌧️", temp: "25°C–29°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    10: { desc: "Cool & Pleasant 🍂", temp: "25°C–30°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "hot_humid" },
    11: { desc: "Cool & Cozy 🍃", temp: "25°C–30°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    12: { desc: "Pleasant Winter ❄️", temp: "24°C–31°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" }
  },
  "752001": { // Puri, Odisha
    1: { desc: "Cool & Pleasant 🍃", temp: "18°C–27°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    2: { desc: "Pleasant & Sunny ☀️", temp: "21°C–30°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    3: { desc: "Warm & Sunny ☀️", temp: "24°C–33°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "hot_humid" },
    4: { desc: "Hot & Humid 🔥", temp: "27°C–35°C", cold_wave: false, hot_wave: true, rainy: false, weather_conditions: "hot_humid" },
    5: { desc: "Very Hot & Humid 🔥", temp: "28°C–37°C", cold_wave: false, hot_wave: true, rainy: false, weather_conditions: "hot_humid" },
    6: { desc: "Monsoon Showers 🌧️", temp: "27°C–33°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    7: { desc: "Heavy Monsoons 🌧️", temp: "26°C–31°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    8: { desc: "Wet & Humid 🌧️", temp: "26°C–31°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    9: { desc: "Breezy Showers 🌧️", temp: "25°C–30°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    10: { desc: "Pleasant Autumn 🍂", temp: "23°C–31°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    11: { desc: "Cool & Dry 🍂", temp: "20°C–29°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    12: { desc: "Mild Winter ❄️", temp: "17°C–26°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" }
  },
  "800008": { // Patna
    1: { desc: "Cold & Foggy ❄️", temp: "10°C–22°C", cold_wave: true, hot_wave: false, rainy: false, weather_conditions: "cold" },
    2: { desc: "Cool & Sunny 🌤️", temp: "12°C–26°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "cold" },
    3: { desc: "Warming Up ☀️", temp: "17°C–33°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    4: { desc: "Hot & Dry 🔥", temp: "21°C–38°C", cold_wave: false, hot_wave: true, rainy: false, weather_conditions: "hot_dry" },
    5: { desc: "Very Hot 🔥", temp: "24°C–39°C", cold_wave: false, hot_wave: true, rainy: false, weather_conditions: "hot_dry" },
    6: { desc: "Hot & Humid 🌡️", temp: "25°C–35°C", cold_wave: false, hot_wave: true, rainy: false, weather_conditions: "hot_humid" },
    7: { desc: "Hot & Monsoon 🌧️", temp: "26°C–33°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    8: { desc: "Humid & Wet 🌧️", temp: "25°C–32°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    9: { desc: "Post-Monsoon Humidity 🌧️", temp: "24°C–32°C", cold_wave: false, hot_wave: false, rainy: true, weather_conditions: "hot_humid" },
    10: { desc: "Pleasant & Sunny 🍂", temp: "20°C–30°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    11: { desc: "Cool & Dry 🍂", temp: "15°C–27°C", cold_wave: false, hot_wave: false, rainy: false, weather_conditions: "warm_moderate" },
    12: { desc: "Cold & Dry ❄️", temp: "11°C–23°C", cold_wave: true, hot_wave: false, rainy: false, weather_conditions: "cold" }
  }
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
  ]
};

const VIBE_DEFINITIONS = {
  heritage_traditionalist: {
    name: "Heritage Traditionalist",
    emoji: "🥻",
    desc: "Traditional silks, zari brocades, and classic festival sarees.",
    tags: ["traditional", "silk", "heavy", "classic", "ethnic", "saree", "kanjeevaram", "banarasi", "zari", "gold", "temple", "mundu", "sherwani", "jainsem"]
  },
  festive_glam: {
    name: "Festive Glam",
    emoji: "✨",
    desc: "Bright, embellished, heavy ethnic wear, lehengas, and celebration outfits.",
    tags: ["festive", "bright", "red", "embellished", "celebration", "lehenga", "anarkali", "ceremonial", "heavy_silk", "maroon", "gold", "brocade", "embroidery"]
  },
  indie_fusion: {
    name: "Indie Fusion (Desi Boho)",
    emoji: "🎨",
    desc: "Desi Boho chic with block prints, indigo dyes, and contemporary fusion kurtas.",
    tags: ["fusion", "cotton", "prints", "oxidized", "casual-ethnic", "block-print", "indigo", "kurta", "denim", "boho", "handblock", "ethnic"]
  },
  high_street_rebel: {
    name: "High-Street Rebel",
    emoji: "👟",
    desc: "Oversized hoodies, utility cargoes, denim jackets, and edgy modern graphic tees.",
    tags: ["streetwear", "oversized", "edgy", "grunge", "layered", "cargo", "graphic", "hoodie", "denim", "modern", "rebel", "baggy"]
  },
  coastal_tropical: {
    name: "Coastal Tropical",
    emoji: "🏝️",
    desc: "Light, breezy cottons, linen shirts, and floral sundresses.",
    tags: ["breathable", "pastel", "floral", "linen", "coastal", "summer", "cotton", "light", "breezy", "sundress", "resort"]
  },
  winter_academia: {
    name: "Winter Academia",
    emoji: "🧥",
    desc: "Smart-casual layering, cable-knit sweaters, velvet blazers, and warm woolen shawls.",
    tags: ["winter", "layered", "preppy", "knitwear", "smart-casual", "trench", "plaid", "woolen", "jacket", "cardigan", "warm", "shawl", "velvet"]
  },
  y2k_nostalgia: {
    name: "Y2K Nostalgia",
    emoji: "📟",
    desc: "Retro pop, Gen-Z crop tops, baggy jeans, bucket hats, and bold neon aesthetics.",
    tags: ["y2k", "vibrant", "retro", "pop", "gen-z", "crop", "baggy", "bucket-hat", "synthetic", "colorful", "neon", "bold"]
  },
  minimalist_essentials: {
    name: "Minimalist Essentials",
    emoji: "🤍",
    desc: "Solid neutrals, clean structures, clean lines, and timeless capsule basics.",
    tags: ["minimal", "neutral", "solid", "clean", "basic", "white", "beige", "black", "fitted", "structured"]
  },
  earthy_handloom: {
    name: "Earthy Handloom",
    emoji: "🌾",
    desc: "Organic, sustainable handlooms, khadi weaves, natural dyes, and artisanal textures.",
    tags: ["handloom", "organic", "earthy", "comfortable", "khadi", "ochre", "olive", "sustainable", "natural", "artisanal"]
  },
  urban_athleisure: {
    name: "Urban Athleisure",
    emoji: "🏃",
    desc: "Activewear, sporty joggers, ribbed tracksuits, and premium athletic apparel.",
    tags: ["sporty", "activewear", "comfortable", "casual", "sneakers", "tracksuit", "ribbed", "athletic", "gym", "jogger"]
  }
};

const CONTEXT_MATRICES = {
  "discovery": { "w_aesthetic": 0.35, "w_fabric": 0.15, "w_festivity": 0.05, "w_boutique": 0.05, "w_creator": 0.05, "w_cf": 0.25, "w_intent": 0.05, "w_velocity": 0.05 },
  "high_intent": { "w_aesthetic": 0.15, "w_fabric": 0.10, "w_festivity": 0.0, "w_boutique": 0.0, "w_creator": 0.0, "w_cf": 0.15, "w_intent": 0.50, "w_velocity": 0.10 },
  "festive_season": { "w_aesthetic": 0.20, "w_fabric": 0.10, "w_festivity": 0.40, "w_boutique": 0.05, "w_creator": 0.05, "w_cf": 0.10, "w_intent": 0.05, "w_velocity": 0.05 },
  "hyper_local_boutique": { "w_aesthetic": 0.10, "w_fabric": 0.05, "w_festivity": 0.0, "w_boutique": 0.40, "w_creator": 0.0, "w_cf": 0.05, "w_intent": 0.10, "w_velocity": 0.30 },
  "social_commerce": { "w_aesthetic": 0.10, "w_fabric": 0.05, "w_festivity": 0.0, "w_boutique": 0.0, "w_creator": 0.40, "w_cf": 0.05, "w_intent": 0.10, "w_velocity": 0.30 },
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

function App() {
  const [calendarPresets, setCalendarPresets] = useState(REGIONAL_DATE_PRESETS);
  const [weatherMatrix, setWeatherMatrix] = useState(WEATHER_MATRIX);
  
  const getPresetWeather = (zip, dateStr) => {
    try {
      const month = parseInt(dateStr.split("-")[1], 10);
      const dbZip = BACKEND_ZIP_MAPPED[zip] || "800008";
      return weatherMatrix[dbZip]?.[month] || weatherMatrix[dbZip]?.[String(month)] || { desc: "Pleasant & Breezy 🍃", temp: "22°C", weather_conditions: "warm_moderate" };
    } catch {
      return { desc: "Pleasant & Breezy 🍃", temp: "22°C", weather_conditions: "warm_moderate" };
    }
  };

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
  const [showOnboarding, setShowOnboarding] = useState(true);
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
  const [activeTab, setActiveTab] = useState('youtube');
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
  }, [currentZipCode, sliderVal, currentVibe, backendStatus]);

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
    logMessage(`Geographic boundary shifted. Active zip code: ${ZIP_CODES[zip].name}.`, "success");
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

    // ── Result Cache: return instantly if same combo was already computed ──
    const cacheKey = `${currentZipCode}|${profile.dateStr}|${currentVibe}|${engineState}`;
    const cached = recCacheRef.current[cacheKey];
    if (cached) {
      setProducts(cached);
      setIsLoading(false);
      const stillExists = cached.find(p => selectedProduct && p.id === selectedProduct.id);
      setSelectedProduct(stillExists || cached[0]);
      return;
    }

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

  const fetchYoutubeTrends = async (zip) => {
    setIsYoutubeLoading(true);
    setYoutubeData(null);
    logMessage("Loading YouTube creator trends from database...", "info");
    try {
      const res = await fetch(`http://localhost:8000/api/trends/youtube?zip_code=${BACKEND_ZIP_MAPPED[zip || currentZipCode]}`);
      if (!res.ok) throw new Error("Failed to fetch YouTube trends");
      const data = await res.json();
      const isArr = Array.isArray(data);
      const len = isArr ? data.length : 0;
      setYoutubeData(isArr ? data : []);
      setYoutubeFetched(true);
      setIsYoutubeLoading(false);
      logMessage(`Creator Feed: Loaded ${len} regional fashion videos.`, "success");
    } catch (e) {
      logMessage(`YouTube trends error: ${e.message}`, "error");
      setIsYoutubeLoading(false);
      setYoutubeFetched(true);
    }
  };

  const fetchBoutiques = async (zip) => {
    setIsBoutiqueLoading(true);
    setBoutiqueData(null);
    logMessage(`Loading local stores for ${ZIP_CODES[zip || currentZipCode]?.city}...`, "info");
    try {
      const res = await fetch(`http://localhost:8000/api/trends/boutiques?zip_code=${BACKEND_ZIP_MAPPED[zip || currentZipCode]}`);
      if (!res.ok) throw new Error("Failed to fetch boutiques");
      const data = await res.json();
      setBoutiqueData(data);
      setBoutiqueFetched(true);
      setIsBoutiqueLoading(false);
      const count = data?.boutiques?.length || 0;
      logMessage(`Local Stores: Loaded ${count} geo-tagged boutiques with social signals.`, "success");
    } catch (e) {
      logMessage(`Boutique store error: ${e.message}`, "error");
      setIsBoutiqueLoading(false);
      setBoutiqueFetched(true);
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

  // Client-side 8-Pillar Scoring Simulation Fallback
  const runLocalRecommendationCalculator = (profile, userVibeVector) => {
    logMessage("Running client-side 8-Pillar mathematical scoring simulation...", "sql");
    
    const month = parseInt(profile.dateStr.split("-")[1], 10);
    const dbZip = BACKEND_ZIP_MAPPED[currentZipCode] || "800008";
    const weatherEntry = weatherMatrix[dbZip]?.[month] || weatherMatrix[dbZip]?.[String(month)] || {};
    const isColdWave = weatherEntry.cold_wave || false;
    const isHotWave = weatherEntry.hot_wave || false;
    const isRainy = weatherEntry.rainy || false;
    const isWeddingDay = (profile.event_type === "wedding_day");
    
    const weatherCondition = weatherEntry.weather_conditions || "hot_humid";
    const allowableMaterials = WEATHER_RULES[weatherCondition]?.allowable_materials || ["cotton", "linen"];
    const allowableMaterialsVector = generateVibeVector(weatherCondition);
    
    const isFestivalActive = profile.isFestive || manualFestival !== "None";
    const festName = manualFestival !== "None" ? manualFestival.toLowerCase() : profile.isFestive ? "chhath_puja" : "";
    const festivalRule = FESTIVAL_RULES[festName] || {};
    const targetColor = festivalRule.target_color || "";
    const targetNature = festivalRule.target_nature || "";
    const festiveContextVector = generateVibeVector(festName || "chhath_puja");

    // Local CF Lookup mock
    const activeCFBoosts = {};
    sessionCart.forEach(cid => {
      const recs = CF_LOOKUP[cid]?.recommendations || [];
      recs.forEach(rec => {
        if (!activeCFBoosts[rec.id] || rec.strength > activeCFBoosts[rec.id]) {
          activeCFBoosts[rec.id] = rec.strength;
        }
      });
    });

    const weights = CONTEXT_MATRICES[engineState] || CONTEXT_MATRICES["discovery"];

    const computed = FALLBACK_PRODUCTS.filter(product => {
      if (product.zip_codes && product.zip_codes.length > 0) {
        return product.zip_codes.includes(currentZipCode);
      }
      return true;
    }).map(product => {
      const id = product.id;
      const tags = product.tags;
      const descLower = product.description.lower || product.description.toLowerCase();

      // Extract attributes dynamically
      let material = "cotton";
      for (let m of ["silk", "linen", "rayon", "velvet", "wool", "denim", "polyester", "chanderi", "georgette", "organza"]) {
        if (tags.includes(m) || descLower.includes(m)) { material = m; break; }
      }
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

      const tagKey = product.tags.join("|");
      const embedding = embeddingCacheRef.current[tagKey]
        || (embeddingCacheRef.current[tagKey] = generateVibeVector(tagKey));

      // === Pillar 1: Aesthetic score ===
      let sAesthetic = calculateCosineSimilarity(userVibeVector, embedding);
      if (nature === currentVibe) sAesthetic = 1.0;
      else sAesthetic = (sAesthetic + 1) / 2;

      // === Pillar 2: Fabric score ===
      let sFabric = calculateCosineSimilarity(allowableMaterialsVector, embedding);
      if (allowableMaterials.includes(material)) sFabric = 1.0;
      else sFabric = (sFabric + 1) / 2;

      // WEATHER VETO
      if (sFabric < 0.2) return null;

      // === Pillar 3: Festivity score ===
      let sFestivity = 1.0;
      if (isFestivalActive) {
        sFestivity = calculateCosineSimilarity(festiveContextVector, embedding);
        if (color === targetColor && nature === targetNature) sFestivity = 1.0;
        else sFestivity = (sFestivity + 1) / 2;
      }

      // === Pillar 4: Creator score ===
      let sCreator = 0.5;
      if (isEvergreen) sCreator = 0.85;
      else {
        const localCreators = FALLBACK_CREATORS[dbZip] || [];
        let maxC = 0.0;
        localCreators.forEach(c => {
          const sim = (calculateCosineSimilarity(c.vector, embedding) + 1) / 2;
          const penalty = ageGroup === c.demographic ? 1.0 : 0.1;
          maxC = Math.max(maxC, sim * penalty * c.subscriber_weight);
        });
        sCreator = maxC;
      }

      // === Pillar 5: Boutique score ===
      let sBoutique = 0.5;
      if (isEvergreen) sBoutique = 0.85;
      else {
        const localStores = FALLBACK_STORES[dbZip] || [];
        let maxS = 0.0;
        localStores.forEach(s => {
          const sim = (calculateCosineSimilarity(s.vector, embedding) + 1) / 2;
          let wRating = Math.max(0.0, (s.rating - 3.0) / 2.0);
          if (s.review_count < 50) wRating *= 0.5;
          const catGate = ["ethnic", "occasion", "festive", "traditional"].includes(category.toLowerCase()) ? 1.0 : 0.2;
          const pricePenalty = s.estimated_cost > 2500 * 2 ? 0.3 : 1.0;
          maxS = Math.max(maxS, sim * wRating * catGate * pricePenalty);
        });
        sBoutique = maxS;
      }

      // === Pillar 6: Velocity score ===
      let sVelocity = 0.0;
      if (baselineSales > 0) {
        const delta = currentSales / baselineSales;
        if (delta > 1.0) sVelocity = Math.min(1.0, (delta - 1.0) / 2.0);
      }

      // === Pillar 7: Intent score ===
      let sIntent = 0.0; // offline simple intent decay mock

      // === Pillar 8: CF score ===
      let sCf = activeCFBoosts[id] || 0.0;

      // Final score formula
      let finalScore = (
        weights.w_aesthetic * sAesthetic +
        weights.w_fabric * sFabric +
        weights.w_festivity * sFestivity +
        weights.w_boutique * sBoutique +
        weights.w_creator * sCreator +
        weights.w_cf * sCf +
        weights.w_intent * sIntent +
        weights.w_velocity * sVelocity
      );

      // Low Stock Penalty
      if (stockLevel < 5) finalScore *= 0.1;

      // Dynamic rules overrides
      if (currentZipCode === "800001" && isWeddingDay) {
        if (tags.includes("heavy_silk")) finalScore += 0.50;
        else if (tags.includes("summer") || tags.includes("casual")) finalScore -= 0.50;
      }
      if (currentZipCode === "560034" && isWeddingDay) {
        if (tags.includes("kasavu_weave")) finalScore += 0.50;
      }
      if (currentZipCode === "752001" && isWeddingDay) {
        if (tags.includes("sambalpuri") || tags.includes("tussar_silk")) finalScore += 0.50;
      }

      return {
        ...product,
        material,
        color,
        nature,
        category,
        price,
        stock_level: stockLevel,
        is_evergreen: isEvergreen,
        baseline_sales: baselineSales,
        current_sales: currentSales,
        units_last_hour: currentSales - baselineSales,
        is_trending: sVelocity >= 0.75,
        vector_score: sAesthetic,
        tag_score: sCreator,
        boost_score: sFestivity,
        velocity_score: sVelocity,
        velocity_boost: sIntent,
        final_score: finalScore,
        overlap_tags: tags.filter(tag => profile.trendingTags.includes(tag)),
        scoring_breakdown: {
          layer1_personal_vibe: weights.w_aesthetic * sAesthetic,
          layer2_creator_trend: weights.w_creator * sCreator,
          layer3_local_boutique: weights.w_boutique * sBoutique,
          layer4_festivity: weights.w_festivity * sFestivity,
          layer5_weather: weights.w_fabric * sFabric,
          layer6_velocity: weights.w_velocity * sVelocity,
          layer7_intent: weights.w_intent * sIntent,
          layer8_cf: weights.w_cf * sCf,
          raw_values: {
            personal_vibe_similarity: sAesthetic,
            creator_trend_match: sCreator,
            local_boutique_match: sBoutique,
            festivity_match: sFestivity,
            weather_match: sFabric,
            checkout_velocity_score: sVelocity,
            intent_score: sIntent,
            cf_score: sCf
          }
        },
        reason_labels: [
          sFestivity > 0.7 && isFestivalActive ? `✨ Trending for Festival` : null,
          sCreator > 0.7 ? `🔥 Loved by local creators` : null,
          sFabric > 0.8 ? `☀️ Climate-appropriate` : null,
          sCf > 0.5 ? `👥 People also bought` : null
        ].filter(Boolean)
      };
    }).filter(Boolean);

    computed.sort((a, b) => b.final_score - a.final_score);

    // ── Score-Gated Diversity Stratification ───────────────────────────────
    // A category only earns a diversity "slot" if its best item meets the
    // minimum relevance threshold. This prevents a 3.8% hoodie from jumping
    // ahead of 57% festive kurtas just because it's a different category.
    const DIVERSITY_MIN_SCORE = 0.20; // 20% threshold to qualify for a slot
    const MAX_PER_CATEGORY   = 2;     // max diversity slots per category
    const DIVERSITY_POOL_SIZE = 20;   // consider top-N items for stratification

    const diversityPool = computed.slice(0, DIVERSITY_POOL_SIZE);
    const categoryCount  = {};
    const diversitySlots = [];   // items that earned a diversity slot
    const remainder      = [];   // everything else in the pool

    diversityPool.forEach(item => {
      const cat   = item.category || 'other';
      const count = categoryCount[cat] || 0;
      // Earns a slot only if score ≥ threshold AND category not yet saturated
      if (item.final_score >= DIVERSITY_MIN_SCORE && count < MAX_PER_CATEGORY) {
        categoryCount[cat] = count + 1;
        diversitySlots.push(item);
      } else {
        remainder.push(item);
      }
    });

    // Merge: diversity winners + remainder + anything beyond the pool
    const merged = [
      ...diversitySlots,
      ...remainder,
      ...computed.slice(DIVERSITY_POOL_SIZE)
    ];

    // De-duplicate (in case the same item ended up in two buckets)
    const seenIds  = new Set();
    const deduped  = merged.filter(p => {
      if (seenIds.has(p.id)) return false;
      seenIds.add(p.id);
      return true;
    });

    // ── Critical: re-sort by score so rank always mirrors the badge ─────────
    deduped.sort((a, b) => b.final_score - a.final_score);

    // Pad to at least 20 items
    const finalFeed = deduped.length < 20
      ? [...deduped, ...computed.filter(p => !seenIds.has(p.id))].slice(0, Math.max(20, deduped.length))
      : deduped;

    setProducts(finalFeed);
    logMessage(`Local matching algorithm ranked ${paddedFeed.length} items. 8-Pillar weights applied.`, "success");
    if (paddedFeed.length > 0) {
      setSelectedProduct(paddedFeed[0]);
    }
  };

  const triggerVibeChange = (vibe) => {
    setCurrentVibe(vibe);
    logMessage(`Shopper style vibe profile changed: '${vibe.toUpperCase()}'.`, "success");
  };

  const handleConfirmOnboarding = () => {
    setCurrentVibe(tempVibe);
    setShowOnboarding(false);
    logMessage(`Vibe check onboarding completed. Selected Vibe: '${VIBE_DEFINITIONS[tempVibe].name}'.`, "success");
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
    const dateObj = new Date(dateStr);
    const month = dateObj.getMonth() + 1;
    const day = dateObj.getDate();

    // ── 1. NATIONAL FESTIVALS (Strictly Pan-India Only) ──────────────────────
    if ((month === 10 && day >= 15 && day <= 24) || dateStr === "2026-10-18") {
      banners.national = {
        title: "Durga Puja & Navratri Celebrations 🥻",
        badge: "🇮🇳 NATIONAL FESTIVAL · PAN-INDIA",
        desc: "Nationwide festive surge across India! Pandals, Dandiya nights, and grand ethnic celebrations.",
        tags: ["Festive Silk", "Heavy Embroidered Saree", "Lehenga Choli", "Kurta Sets", "Red & Gold"],
        type: "national",
        bannerImg: "/images/durga_puja_banner.png"
      };
    } else if ((month === 11 && day >= 5 && day <= 10) || dateStr === "2026-11-08") {
      banners.national = {
        title: "Diwali Festival of Lights 🪔",
        badge: "🇮🇳 NATIONAL FESTIVAL · PAN-INDIA",
        desc: "Gleaming Deepavali celebrations across India! Premium festive silks, gold zari brocades, and regal sherwanis.",
        tags: ["Gleaming Gold", "Brocade Silk", "Regal Sherwani", "Anarkali", "Maroon Silk"],
        type: "national",
        bannerImg: "/images/diwali_banner.png"
      };
    } else if ((month === 3 && day >= 2 && day <= 5) || dateStr === "2026-03-03") {
      banners.national = {
        title: "Holi Festival of Colors 🎨",
        badge: "🇮🇳 NATIONAL FESTIVAL · PAN-INDIA",
        desc: "Joyous spring color festival celebrated across all states! Crisp white cottons, relaxed kurtas, and easy dailywear.",
        tags: ["Pure White Cotton", "Casual Kurti", "Chikan Handloom", "Breathable Linen"],
        type: "national",
        bannerImg: "/images/holi_banner.png"
      };
    } else if (month === 8 && day === 15) {
      banners.national = {
        title: "79th Independence Day Celebration 🇮🇳",
        badge: "🇮🇳 NATIONAL DAY · PAN-INDIA",
        desc: "Tricolor pride nationwide! Khadi, handloom ethnic wear, saffron & white formal kurtas.",
        tags: ["Tricolor Accent", "Khadi Handloom", "Formal Nehru Jacket", "Saffron White Green"],
        type: "national",
        bannerImg: "/images/independence_day_banner.png"
      };
    } else if (month === 1 && day === 26) {
      banners.national = {
        title: "Republic Day Parade & Celebrations 🇮🇳",
        badge: "🇮🇳 NATIONAL DAY · PAN-INDIA",
        desc: "National pride parade and ceremonial gatherings across India.",
        tags: ["Formal Ethnic", "Tricolor Wear", "Structure Blazer", "Nehru Jacket"],
        type: "national",
        bannerImg: "/images/republic_day_banner.png"
      };
    }

    // ── 2. LOCAL REGIONAL FESTIVALS (Strictly Local / State Only) ────────────
    if (zipCode === "800008") { // Patna / Bihar
      if (dateStr === "2026-11-15") {
        banners.local = {
          title: "Chhath Puja — Sandhya Arghya 🛕",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Authentic Bihari Mahaparv on the banks of the Ganges! Sacred saffron & yellow sarees, Bhagalpuri silk, and unstitched dhoti sets.",
          tags: ["Saffron Yellow Saree", "Bhagalpuri Tussar", "Madhubani Hand-Painted", "Cotton Dhoti"],
          type: "local",
          bannerImg: "/images/chhath_puja_banner.png"
        };
      } else if (dateStr === "2026-03-22") {
        banners.local = {
          title: "Bihar Diwas (Statehood Day) 🏛️",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Celebrating Bihar's rich heritage with artisanal Bhagalpuri tussar silk and traditional weaves.",
          tags: ["Bhagalpuri Silk", "Tussar Kurta", "Nehru Jacket", "Traditional Weave"],
          type: "local",
          bannerImg: "/images/saraswati_puja_banner.png"
        };
      } else if (dateStr === "2026-02-02") {
        banners.local = {
          title: "Saraswati Puja / Vasant Panchami 🌾",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Spring festival of learning in Bihar! Bright basanti yellow sarees, georgettes, and yellow kurtis.",
          tags: ["Basanti Yellow Saree", "Georgette Kurti", "Yellow Anklet Set", "Ethnic Kurta"],
          type: "local",
          bannerImg: "/images/saraswati_puja_banner.png"
        };
      } else if (dateStr === "2026-12-10") {
        banners.local = {
          title: "Patna Wedding Day — Pheras Rituals 💍",
          badge: "📍 LOCAL REGIONAL SURGE · Patna (800008)",
          desc: "Peak Bihari wedding season surge! Heavy Banarasi silk sarees, zardozi lehengas, and royal wedding sherwanis.",
          tags: ["Banarasi Crimson Silk", "Heavy Zardozi", "Royal Sherwani", "Gold Brocade"],
          type: "local",
          bannerImg: "/images/wedding_day_banner.png"
        };
      } else if (dateStr === "2026-01-14") {
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
      if (dateStr === "2026-08-27") {
        banners.local = {
          title: "Onam Festival — Thiruvonam 🌾",
          badge: "📍 LOCAL REGIONAL SURGE · Fort Kochi (682001)",
          desc: "Grand harvest festival of Kerala! Authentic Kasavu sarees with woven gold tissue borders, Kara mundus, and traditional pookalam attire.",
          tags: ["Kerala Kasavu Saree", "Gold Zari Border", "Men's Kara Mundu", "Off-White & Gold"],
          type: "local",
          bannerImg: "/images/onam_vishu_banner.png"
        };
      } else if (dateStr === "2026-04-14") {
        banners.local = {
          title: "Vishu Festival (Malayali New Year) 🌼",
          badge: "📍 LOCAL REGIONAL SURGE · Fort Kochi (682001)",
          desc: "Malayali New Year celebrations! Golden Kani yellow silks, traditional Kasavu weaves, and fresh festival cottons.",
          tags: ["Kasavu Weave", "Vishu Yellow Silk", "Gold Border Mundu", "Traditional Kerala"],
          type: "local",
          bannerImg: "/images/onam_vishu_banner.png"
        };
      } else if (dateStr === "2026-01-20") {
        banners.local = {
          title: "Kochi-Muziris Biennale Art Peak 🎨",
          badge: "📍 LOCAL REGIONAL SURGE · Fort Kochi (682001)",
          desc: "Fort Kochi arts & design surge! Sustainable organic linens, artsy boho silhouettes, and coastal summer layers.",
          tags: ["Breezy Linen", "Boho Indigo", "Artsy Midi Dress", "Sustainable Cotton"],
          type: "local",
          bannerImg: "/images/onam_vishu_banner.png"
        };
      } else if (dateStr === "2026-12-27") {
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
      if (dateStr === "2026-07-16" || dateStr === "2026-07-15") {
        banners.local = {
          title: "Puri Rath Yatra Chariot Festival 🚩",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "World-famous Lord Jagannath Grand Chariot Festival! Handwoven Sambalpuri Ikat cotton, saffron yellow temple wear, and Odia weaves.",
          tags: ["Sambalpuri Ikat", "Temple Yellow Cotton", "Odia Handloom", "Pasapalli Weave"],
          type: "local",
          bannerImg: "/images/rath_yatra_banner.png"
        };
      } else if (dateStr === "2026-06-14" || dateStr === "2026-06-15") {
        banners.local = {
          title: "Raja Parba / Raja Sankranti 🌿",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "Unique Odia festival celebrating womanhood and nature! New pastel cotton sarees, Alata-patterned borders, and lightweight handlooms.",
          tags: ["Lightweight Handloom", "Pastel Cotton Saree", "Sambalpuri Kurti", "Fresh Weave"],
          type: "local",
          bannerImg: "/images/nuakhai_banner.png"
        };
      } else if (dateStr === "2026-09-15") {
        banners.local = {
          title: "Nuakhai Agricultural Harvest Festival 🌾",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "Western Odisha new crop harvest celebration! Traditional Tussar silk sarees and Sambalpuri Kurta sets.",
          tags: ["Tussar Silk", "Sambalpuri Handloom", "Harvest Earth Tones", "Traditional Odia"],
          type: "local",
          bannerImg: "/images/nuakhai_banner.png"
        };
      } else if (dateStr === "2026-12-20") {
        banners.local = {
          title: "Odisha Winter Wedding — Pheras 💍",
          badge: "📍 LOCAL REGIONAL SURGE · Puri (752001)",
          desc: "Peak Odia winter wedding season! Heavy Bomkai silk sarees, Tussar brocades, and ceremonial Nehru jacket sets.",
          tags: ["Bomkai Silk Saree", "Tussar Brocade", "Ceremonial Sherwani", "Crimson Red"],
          type: "local",
          bannerImg: "/images/wedding_day_banner.png"
        };
      }
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
                      {nationalProducts.slice(0, 25).map((product, idx) => renderProductCard(product, idx))}
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
              const localProducts = products.filter(p => 
                !p.is_global_trend && 
                (
                  (p.zip_codes && p.zip_codes.includes(currentZipCode)) ||
                  (p.tags && p.tags.some(t => activeDateProfile.trendingTags.includes(t))) ||
                  (p.tags && (p.tags.includes("local") || p.tags.includes("ethnic") || p.tags.includes("handloom") || p.tags.includes("saree") || p.tags.includes("kurta")))
                )
              );
              return (
                <div style={{ marginTop: '14px', background: 'var(--daisy-panel)', padding: '16px', borderRadius: '16px', border: '1px solid rgba(216, 164, 143, 0.4)' }}>
                  <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: 'var(--peach-dark)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    📍 {banners.local.title} — Regional Dispatch Collection ({localProducts.length} items)
                  </h3>
                  {localProducts.length > 0 ? (
                    <div className="horizontal-shelf">
                      {localProducts.slice(0, 25).map((product, idx) => renderProductCard(product, idx))}
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
            src={product.image_url} 
            alt={product.name} 
            className="product-image"
            onError={(e) => {
              e.target.src = `https://placehold.co/400x500/EFEBCE/A3A380?text=${encodeURIComponent(product.name)}`;
            }}
          />
          <div className="score-badge">
            {(product.final_score * 100).toFixed(1)}%
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
          <h4 className="product-name">{product.name}</h4>
          <p style={{ margin: '4px 0', fontSize: '0.9rem', color: '#96636a', fontWeight: 'bold' }}>₹{product.price}</p>
          
          <div className="product-tags" style={{ margin: '8px 0' }}>
            {product.tags.slice(0, 3).map(tag => (
              <span 
                key={tag} 
                className={`product-tag ${activeDateProfile.trendingTags.includes(tag) ? 'highlight' : ''}`}
              >
                #{tag}
              </span>
            ))}
          </div>

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
    return (
      <div
        key={product.id}
        className="global-trend-card"
        style={{ '--city-color': product.global_primary_color || '#9b6cb5', flex: '0 0 260px', maxWidth: '260px' }}
        onClick={() => openTrendsPanel('global')}
      >
        <div className="global-trend-badge">
          <span>{product.global_flag} {product.global_city}</span>
          <span className="global-season-tag">{product.global_season}</span>
        </div>
        <div className="global-trend-archetype">{product.global_style_archetype}</div>
        <h4 className="global-trend-name">{product.name}</h4>
        <p className="global-trend-desc">{product.description}</p>
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
          <span className="global-runway-cta">See Runway →</span>
        </div>
      </div>
    );
  };

  return (
    <div id="root">
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
      <div className="dashboard-grid">
        
        {/* Left Side: Controller + Grid Feed */}
        <div className="main-feed-panel">
          
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

                {/* Trend intelligence buttons inline with the panel */}
                {timeTravelVisible && (
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
                    {dateProfiles.map((profile, index) => (
                      <span 
                        key={profile.key} 
                        className={`slider-label ${sliderVal === index ? 'active' : ''}`} 
                        onClick={() => handleSliderChange({target:{value:index}})}
                        style={{ fontSize: '0.7rem' }}
                      >
                        {profile.label}
                      </span>
                    ))}
                  </div>
                </div>
                
                {/* Live Environmental Factors */}
                <div className="env-factors-row">
                  <div className="factor-box">
                    <div className="factor-title">Temperature</div>
                    <div className="factor-value" style={{
                      color: getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("10°") || 
                             getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("8°") || 
                             getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("9°") ? '#1e40af' : 
                             getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("39°") || 
                             getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("38°") ? '#9a3412' : 'var(--text-main)'
                    }}>
                      {getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp}
                    </div>
                  </div>
                  <div className="factor-box">
                    <div className="factor-title">Weather Status</div>
                    <div className="factor-value" style={{ color: 'var(--text-main)' }}>
                      {getPresetWeather(currentZipCode, activeDateProfile.dateStr).desc}
                    </div>
                  </div>
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
                        onError={(e) => { e.target.src = `https://placehold.co/400x500/1a1a2e/ffffff?text=${encodeURIComponent(product.name)}`; }}
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
                <h2 className="section-title">✨ Recommended For You</h2>
                {products.filter(p => !p.is_global_trend).length > 0 ? (
                  <div className="horizontal-shelf">
                    {products
                      .filter(p => !p.is_global_trend)
                      .slice(0, 25)
                      .map((product, idx) => renderProductCard(product, idx))}
                  </div>
                ) : (
                  <p style={{ fontStyle: 'italic', fontSize: '0.85rem', color: 'var(--text-muted)' }}>No recommendations matching your search space.</p>
                )}
              </div>

              {/* 2. Global Trends */}
              <div className="section-container">
                <div 
                  className="festival-banner" 
                  style={{ backgroundImage: `url(/images/global_trends_banner.png)` }}
                  onClick={() => setExpandedSections(prev => ({ ...prev, global: !prev.global }))}
                >
                    <div className="banner-overlay">
                      <span className="banner-badge">🌍 GLOBAL STYLE PULSE</span>
                      <h2 className="banner-title">GLOBAL RUNWAY TRENDS</h2>
                      <span className="banner-cta">
                        {expandedSections.global ? '🙈 CLICK TO COLLAPSE COLLECTION' : '✨ CLICK TO EXPLORE TRENDS'}
                      </span>
                    </div>
                  </div>
                  
                  {expandedSections.global && (() => {
                    let extractedGlobalTrends = [];
                    if (globalRunwayData && globalRunwayData.cities) {
                      Object.entries(globalRunwayData.cities).forEach(([cityKey, cityData]) => {
                        if (cityData.trends) {
                          cityData.trends.forEach(trend => {
                            extractedGlobalTrends.push({
                              id: `global_${trend.id || trend.trend_name}`,
                              name: trend.trend_name,
                              description: trend.description,
                              tags: trend.vibe_tags || [],
                              category: "Global Runway",
                              is_global_trend: true,
                              global_city: cityData.city || cityKey,
                              global_country: cityData.country || "",
                              global_flag: cityData.flag || "🌍",
                              global_primary_color: cityData.primary_color || "#9b6cb5",
                              global_style_archetype: cityData.style_archetype || "",
                              global_season: cityData.season || "SS26",
                              global_heat_score: trend.heat_score || 0.9,
                              global_searches_weekly: trend.global_searches_weekly || 150000,
                              global_key_pieces: trend.key_pieces || [],
                              global_trending_colors: trend.trending_colors || []
                            });
                          });
                        }
                      });
                    }
                    const globalProducts = extractedGlobalTrends.length > 0 
                      ? extractedGlobalTrends 
                      : products.filter(p => p.is_global_trend);
                      
                    return globalProducts.length > 0 ? (
                      <div className="global-trends-vertical-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px', marginTop: '15px' }}>
                        {globalProducts
                          .slice(0, 25)
                          .map((product) => renderGlobalTrendCard(product))}
                      </div>
                    ) : (
                      <p style={{ fontStyle: 'italic', fontSize: '0.85rem', color: 'var(--text-muted)' }}>Global trends loading...</p>
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
                    src={p.image_url}
                    alt={p.name}
                    className="pdp-modal-img"
                    onError={e => { e.target.src = `https://placehold.co/400x500/1a1a2e/ffffff?text=${encodeURIComponent(p.name)}`; }}
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

                  {/* Description */}
                  {p.description && (
                    <p className="pdp-description">{p.description}</p>
                  )}

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
                padding: '6px 10px',
                background: 'rgba(255,255,255,0.08)',
                border: '1px solid var(--border-color)',
                color: 'white',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: 'bold'
              }}
            >
              ✕ Close
            </button>
          </div>

          {/* Sub-header: city + refresh */}
          <div style={{ padding: '10px 18px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              📍 {ZIP_CODES[currentZipCode].city} · Trends Intelligence
            </span>
            <button
              onClick={() => {
                if (trendsPanelTab === 'youtube') { setYoutubeFetched(false); fetchYoutubeTrends(currentZipCode); }
                if (trendsPanelTab === 'boutiques') { setBoutiqueFetched(false); fetchBoutiques(currentZipCode); }
              }}
              style={{ padding: '4px 10px', background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '4px', fontSize: '0.7rem', cursor: 'pointer' }}
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
                    
                    {/* Circular Avatar Selector Bar */}
                    <div>
                      <p style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--peach-dark)', margin: '0 0 10px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        🎬 Regional Creators ({youtubeData.length}) — Click to view reel:
                      </p>
                      <div className="horizontal-shelf" style={{ gap: '14px', paddingBottom: '8px' }}>
                        {youtubeData.map((item, idx) => {
                          const channelName = item.youtube_video?.channel || `Creator ${idx+1}`;
                          const initials = channelName
                            .split(' ')
                            .filter(Boolean)
                            .map(n => n[0])
                            .join('')
                            .toUpperCase()
                            .slice(0, 2) || "CR";
                          const isSelected = selectedCreatorIdx === idx;
                          
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
                                maxWidth: '70px',
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

                    {/* Selected Creator Reel (Horizontal Dress Cards - Max 15) */}
                    {(() => {
                      const currentCreator = youtubeData[selectedCreatorIdx] || youtubeData[0];
                      const channel = currentCreator?.youtube_video?.channel || "Creator";
                      
                      const creatorTags = currentCreator?.youtube_video?.inferred_tags || [];
                      const creatorProducts = products.filter(p => 
                        !p.is_global_trend && (
                          (currentCreator?.matched_product && p.id === currentCreator.matched_product.id) ||
                          (p.tags && p.tags.some(t => creatorTags.includes(t))) ||
                          (p.tags && p.tags.includes("micro_creator"))
                        )
                      );

                      const displayProducts = (creatorProducts.length >= 3 ? creatorProducts : products.filter(p => !p.is_global_trend)).slice(0, 15);

                      return (
                        <div style={{ background: 'var(--daisy-panel)', borderRadius: '16px', padding: '16px', border: '1px solid var(--border-color)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                            <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                              🎬 {channel}'s Showcase ({displayProducts.length} dresses)
                            </h4>
                            <span style={{ fontSize: '0.72rem', color: 'var(--peach-dark)', fontWeight: 'bold' }}>
                              Scroll Horizontally ➔
                            </span>
                          </div>
                          <div className="horizontal-shelf" style={{ gap: '14px' }}>
                            {displayProducts.map((product, pIdx) => renderProductCard(product, pIdx))}
                          </div>
                        </div>
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
                      const storeProducts = products.filter(p => 
                        !p.is_global_trend && (
                          (p.zip_codes && p.zip_codes.includes(currentZipCode)) ||
                          (store.matched_product && p.id === store.matched_product.id) ||
                          (p.tags && p.tags.some(t => [store.style_vibe_cluster?.toLowerCase(), store.extracted_visual_trend?.toLowerCase()].includes(t)))
                        )
                      );
                      const shopDresses = (storeProducts.length >= 3 ? storeProducts : products.filter(p => !p.is_global_trend)).slice(0, 7);
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
