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
    { key: "oct_18", label: "Oct 18 (Durga Puja)", dateStr: "2026-10-18", event: "Durga Puja (Ravana Podi)", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "traditional_silk", "red", "gold", "sambalpuri"] },
    { key: "nov_8", label: "Nov 8 (Diwali)", dateStr: "2026-11-08", event: "Diwali Lights Festival", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "regal", "gold", "silk", "heavy_embroidery"] },
    { key: "dec_20", label: "Dec 20 (Odia Wedding)", dateStr: "2026-12-20", event: "Odisha Winter Wedding (Pheras)", event_type: "wedding_day", isFestive: true, trendingTags: ["heavy_silk", "tussar_silk", "ceremonial", "sherwani", "crimson", "gold"] }
  ]
};

const VIBE_DEFINITIONS = {
  festive: {
    name: "Ethnic & Festive",
    emoji: "🥻",
    desc: "Traditional silks, zari brocades, kurtas, and festival sarees matching regional cultural dates.",
    tags: ["ethnic", "festive", "traditional", "silk", "saree", "jainsem", "jymphong", "mundu", "sherwani"]
  },
  casual: {
    name: "Summer Casual",
    emoji: "👕",
    desc: "Lightweight cottons, linens, breezy tunics, and everyday wear for hot humid climates.",
    tags: ["casual", "summer", "cotton", "linen", "breathable", "dailywear"]
  },
  winter: {
    name: "Cozy Winter",
    emoji: "🧥",
    desc: "Heavy velvet ensembles, wool shawls, pullovers, and fleece layers for extreme cold spells.",
    tags: ["winter", "warm", "heavy-weight", "velvet", "shawl", "jacket", "cardigan", "woolen"]
  },
  streetwear: {
    name: "Urban Streetwear",
    emoji: "👟",
    desc: "Oversized hoodies, utility cargoes, denim jackets, and modern graphic tees for modern shoppers.",
    tags: ["streetwear", "hoodie", "cargo", "modern", "denim", "fusion", "party"]
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
  if (vibeName === "festive") vec.fill(1, 0, 100);
  else if (vibeName === "casual") vec.fill(1, 100, 200);
  else if (vibeName === "winter") vec.fill(1, 200, 300);
  else if (vibeName === "streetwear") vec.fill(1, 300, 400);
  vec.fill(0.2, 400, 512);
  
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
  const [trendsPanelOpen, setTrendsPanelOpen] = useState(false);
  const [trendsPanelTab, setTrendsPanelTab] = useState('youtube');
  const [currentVibe, setCurrentVibe] = useState("casual");
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [lookCompleter, setLookCompleter] = useState({ accessory: null, footwear: null });
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [tempVibe, setTempVibe] = useState("casual");
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

    fetchLookCompleter();
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

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    if (tab === 'youtube' && !youtubeFetched) {
      fetchYoutubeTrends(currentZipCode);
    }
    if (tab === 'boutiques' && !boutiqueFetched) {
      fetchBoutiques(currentZipCode);
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

  const weights = CONTEXT_MATRICES[engineState] || CONTEXT_MATRICES["discovery"];

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
          <div className="meta-pill highlight" style={{ padding: '0px 10px', background: 'transparent' }}>
            <span style={{ fontSize: '0.75rem', marginRight: '4px', color: '#94a3b8' }}>📍 REGION:</span>
            <select 
              value={currentZipCode} 
              onChange={handleZipCodeChange}
              style={{
                background: 'var(--bg-card)',
                color: 'white',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '4px 8px',
                fontSize: '0.8rem',
                cursor: 'pointer',
                fontWeight: '600',
                outline: 'none'
              }}
            >
              {Object.entries(ZIP_CODES).map(([zip, details]) => (
                <option key={zip} value={zip}>{details.name}</option>
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
            <div className="control-card-header">
              <h3 className="control-title">
                🕒 Time-Traveler Control Panel ({ZIP_CODES[currentZipCode].city})
              </h3>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>

                {/* Trend intelligence buttons inline with the panel */}
                <button
                  id="btn-creator-feed"
                  onClick={() => openTrendsPanel('youtube')}
                  style={{
                    padding: '7px 16px',
                    background: trendsPanelOpen && trendsPanelTab === 'youtube'
                      ? 'linear-gradient(135deg, #c69fd5, #9b6cb5)'
                      : 'rgba(198,159,213,0.1)',
                    color: trendsPanelOpen && trendsPanelTab === 'youtube' ? '#fdfdc9' : '#c69fd5',
                    border: '1px solid rgba(198,159,213,0.4)',
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
                      background: trendsPanelOpen && trendsPanelTab === 'youtube' ? 'rgba(253,253,201,0.3)' : 'rgba(198,159,213,0.2)',
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
                      : 'rgba(198,159,213,0.08)',
                    color: trendsPanelOpen && trendsPanelTab === 'boutiques' ? '#fdfdc9' : '#c69fd5',
                    border: '1px solid rgba(198,159,213,0.4)',
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
                      background: trendsPanelOpen && trendsPanelTab === 'boutiques' ? 'rgba(253,253,201,0.3)' : 'rgba(198,159,213,0.2)',
                      borderRadius: '10px',
                      padding: '1px 7px',
                      fontSize: '0.65rem',
                      fontWeight: 'bold'
                    }}>{boutiqueData.boutiques.length}</span>
                  )}
                </button>

                <div style={{ width: '1px', height: '28px', background: 'var(--border-color)', margin: '0 4px' }} />


                <button className="onboarding-btn" onClick={() => setShowOnboarding(true)}>
                  ✨ Vibe Check
                </button>
              </div>
            </div>
            
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
                         getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("9°") ? '#c69fd5' : 
                         getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("39°") || 
                         getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("38°") ? '#fdfdc9' : '#f6f1f9'
                }}>
                  {getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp}
                </div>
              </div>
              <div className="factor-box">
                <div className="factor-title">Weather Status</div>
                <div className="factor-value">
                  {getPresetWeather(currentZipCode, activeDateProfile.dateStr).desc}
                </div>
              </div>
              <div className="factor-box">
                <div className="factor-title">Local Calendar Event</div>
                <div className="factor-value" style={{fontSize: '0.75rem', color: '#fdfdc9', lineHeight: '1.2'}}>
                  {activeDateProfile.event}
                </div>
              </div>
              <div className="factor-box">
                <div className="factor-title">Active Surge</div>
                <div className="factor-value" style={{fontSize: '0.8rem', color: '#c69fd5'}}>
                  {activeDateProfile.event_type === 'wedding_day' ? 'Wedding Surge 💍' : activeDateProfile.isFestive ? 'Festive Surge 🥻' : 'None'}
                </div>
              </div>
              <div className="factor-box">
                <div className="factor-title">Avg Order Value</div>
                <div className="factor-value" style={{ color: '#fdfdc9', fontWeight: 'bold' }}>
                  {zipInsights ? `₹${zipInsights.average_order_value.toLocaleString('en-IN')}` : '₹...'}
                </div>
              </div>
              <div className="factor-box">
                <div className="factor-title">Upcoming (7 Days)</div>
                <div className="factor-value" style={{ fontSize: '0.7rem', color: '#c69fd5', lineHeight: '1.4' }}>
                  {zipInsights && zipInsights.upcoming_events && zipInsights.upcoming_events.length > 0
                    ? zipInsights.upcoming_events.slice(0, 2).map((ev, i) => (
                        <div key={i} style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: '#fdfdc9' }}>
                          📅 {ev.event_name.split('(')[0].trim()}
                        </div>
                      ))
                    : 'No events soon'
                  }
                </div>
              </div>
            </div>
          </div>
          
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
            <div className="catalog-grid">
              {products.map((product, idx) => {
                const hasWeddingSurge = (activeDateProfile.event_type === "wedding_day") && product.tags.includes("ceremonial");
                const hasFestiveSurge = activeDateProfile.isFestive && product.tags.includes("festive") && !hasWeddingSurge;
                const isMicroCreator = product.tags.includes("micro_creator");
                const isInCart = sessionCart.includes(product.id);
                
                return (
                  <div 
                    key={product.id} 
                    className={`product-card ${selectedProduct && selectedProduct.id === product.id ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedProduct(product);
                      logMessage(`Selected catalog item: ${product.name} for mathematical score dissection.`, "info");
                    }}
                  >
                    <div className="rank-badge">Rank {idx + 1}</div>
                    
                    <div className="product-image-container">
                      <img 
                        src={product.image_url} 
                        alt={product.name} 
                        className="product-image"
                        onError={(e) => {
                          e.target.src = `https://placehold.co/400x500/${product.category === 'festive' ? '8b0000' : product.category === 'winter' ? '301934' : product.category === 'streetwear' ? '708090' : '135206'}/ffffff?text=${encodeURIComponent(product.name)}`;
                        }}
                      />
                      <div className="score-badge">
                        {(product.final_score * 100).toFixed(1)}%
                      </div>
                      
                      {isMicroCreator && (
                        <div className="surge-pill" style={{ background: '#7A5A45', color: '#CD9FBC', top: '40px', left: '8px', bottom: 'auto' }}>
                          Micro-Creator 🌾
                        </div>
                      )}
                      
                      {product.is_trending && (
                        <div className="surge-pill" style={{ background: 'linear-gradient(135deg, #824265, #5C283C)', color: '#CD9FBC', top: isMicroCreator ? '68px' : '40px', left: '8px', bottom: 'auto', fontWeight: '800' }}>
                          🔥 Trending
                        </div>
                      )}
                      
                      {hasWeddingSurge && (
                        <div className="surge-pill" style={{ background: '#824265', color: '#CD9FBC' }}>Wedding Surge 💍</div>
                      )}
                      {hasFestiveSurge && (
                        <div className="surge-pill festive">Festive Surge 🥻</div>
                      )}
                    </div>
                    
                    <div className="product-info">
                      <p className="product-category" style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{product.category}</span>
                        {product.zip_codes && product.zip_codes.length > 0 && (
                          <span style={{ color: '#CD9FBC', fontWeight: 'bold' }}>LOCAL</span>
                        )}
                      </p>
                      <h4 className="product-name">{product.name}</h4>
                      <p style={{ margin: '4px 0', fontSize: '0.9rem', color: '#BA9476', fontWeight: 'bold' }}>₹{product.price}</p>
                      
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

                      {/* Interactive Buttons */}
                      <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                        <button 
                          className="onboarding-btn" 
                          style={{ flex: 1, padding: '4px 8px', fontSize: '0.75rem', background: isInCart ? '#5C283C' : '#824265', border: '1px solid rgba(205,159,188,0.2)', color: '#CD9FBC' }}
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
                          style={{ padding: '4px 8px', fontSize: '0.75rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'white' }}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAddToWishlist(product.id);
                          }}
                        >
                          ❤️ Wishlist
                        </button>
                      </div>

                      {product.product_url && (
                        <div style={{ marginTop: '10px' }}>
                          <a 
                            href={product.product_url} 
                            target="_blank" 
                            rel="noreferrer"
                            style={{ 
                              display: 'block', 
                              padding: '5px 10px', 
                              background: 'rgba(255,255,255,0.05)', 
                              color: 'white', 
                              textDecoration: 'none', 
                              borderRadius: '4px', 
                              fontSize: '0.75rem',
                              fontWeight: 'bold',
                              textAlign: 'center',
                              border: '1px solid var(--border-color)'
                            }}
                            onClick={(e) => e.stopPropagation()}
                          >
                            🛍️ View on Myntra
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        


      </div>



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
                  background: trendsPanelTab === 'youtube' ? '#824265' : 'rgba(122,90,69,0.12)',
                  color: 'white',
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
                  background: trendsPanelTab === 'boutiques' ? '#5C283C' : 'rgba(122,90,69,0.08)',
                  color: 'white',
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
                    <p style={{ color: '#CD9FBC', fontSize: '0.8rem', margin: 0 }}>Loading creator videos...</p>
                  </div>
                ) : Array.isArray(youtubeData) && youtubeData.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {youtubeData.map((item, idx) => (
                      <div key={idx} className="creator-card" style={{ flexDirection: 'column' }}>
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                          <div className="creator-thumb-wrap" style={{ minWidth: '100px', width: '100px', height: '60px' }}>
                            <img
                              src={item.youtube_video.thumbnail_url}
                              alt="thumb"
                              className="creator-thumb"
                              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                              onError={(e) => { e.target.src = `https://placehold.co/160x90/1a1a2e/ec4899?text=Video+${idx+1}`; }}
                            />
                            <div className="creator-rank-badge">#{idx + 1}</div>
                            {item.youtube_video.video_url && (
                              <a href={item.youtube_video.video_url} target="_blank" rel="noreferrer" className="creator-play-btn">▶</a>
                            )}
                          </div>
                          <div className="creator-info" style={{ flex: 1 }}>
                            <p className="creator-video-title">{item.youtube_video.title}</p>
                            <p className="creator-channel">📺 {item.youtube_video.channel}</p>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                              {item.youtube_video.inferred_tags?.slice(0, 3).map(tag => (
                                <span key={tag} className="creator-tag">{tag}</span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <p className="creator-llm-desc" style={{ marginTop: '8px' }}>"{item.youtube_video.llm_extracted_description}"</p>
                        {item.matched_product && (
                          <div className="creator-match" style={{ marginTop: '8px', padding: '8px', background: 'rgba(34,197,94,0.07)', borderRadius: '8px', border: '1px solid rgba(34,197,94,0.15)', display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <img
                              src={item.matched_product.image_url}
                              alt={item.matched_product.name}
                              style={{ width: '48px', height: '60px', objectFit: 'cover', borderRadius: '4px' }}
                              onError={(e) => { e.target.src = 'https://placehold.co/70x90/1a1a2e/22c55e?text=Match'; }}
                            />
                            <div>
                              <span style={{ fontSize: '0.6rem', color: '#22c55e', fontWeight: 'bold' }}>🎯 CATALOG MATCH</span>
                              <p className="creator-match-name">{item.matched_product.name}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="trends-empty">
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🎬</div>
                    <p style={{ fontWeight: '600', color: 'white', marginBottom: '4px' }}>Creator Feed loading...</p>
                    <p style={{ fontSize: '0.75rem' }}>Fetching regional fashion creator videos</p>
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
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {boutiqueData.boutiques.map((store, idx) => (
                      <div key={store.store_id} className="boutique-card">
                        <div className="boutique-card-top">
                          <div className="boutique-rank">#{idx + 1}</div>
                          <div className="boutique-store-info">
                            <p className="boutique-store-name">{store.store_name}</p>
                            <p className="boutique-locality">📍 {store.locality || ZIP_CODES[currentZipCode]?.city}</p>
                          </div>
                          <div className="boutique-rating">⭐ {store.rating || store.simulated_engagement}</div>
                        </div>
                        <div className="boutique-trend-row">
                          <span className="boutique-trend-badge">#{store.extracted_visual_trend}</span>
                          <span className="boutique-vibe-cluster">{store.style_vibe_cluster}</span>
                        </div>
                        <div className="boutique-meta-row">
                          <span className="boutique-source">{store.social_signal_source}</span>
                          <span className="boutique-engagement">🔥 {(store.simulated_engagement / 1000).toFixed(1)}K</span>
                        </div>
                        {store.matched_product && (
                          <div className="boutique-matched-product">
                            <img
                              src={store.matched_product.image_url}
                              alt={store.matched_product.name}
                              className="boutique-match-img"
                              onError={(e) => { e.target.src = 'https://placehold.co/60x75/1a1a2e/a855f7?text=Item'; }}
                            />
                            <div className="boutique-match-details">
                              <span style={{ fontSize: '0.6rem', color: '#CD9FBC', fontWeight: 'bold' }}>TRENDING IN STORE</span>
                              <p className="boutique-match-name">{store.matched_product.name}</p>
                              {store.matched_product.product_url && (
                                <a href={store.matched_product.product_url} target="_blank" rel="noreferrer" className="creator-buy-btn" style={{ background: '#a855f7' }}>Shop ↗</a>
                              )}
                            </div>
                          </div>
                        )}
                        <a href={store.maps_url} target="_blank" rel="noreferrer" className="boutique-maps-btn">🗺️ Open in Maps</a>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="trends-empty">
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🏪</div>
                    <p style={{ fontWeight: '600', color: 'white', marginBottom: '4px' }}>Local Boutiques loading...</p>
                    <p style={{ fontSize: '0.75rem' }}>Fetching geo-tagged boutiques near {ZIP_CODES[currentZipCode].city}</p>
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
