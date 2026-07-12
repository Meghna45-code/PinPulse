import { useState, useEffect, useRef } from 'react';
import './App.css';
import { FALLBACK_PRODUCTS } from './catalog_fallback';

const ZIP_CODES = {
  "560034": { city: "Koramangala", state: "Bengaluru", name: "Bengaluru (560034) - Gen-Z Streetwear" },
  "110049": { city: "South Ext", state: "Delhi", name: "Delhi (110049) - Premium Indo-Western" },
  "800001": { city: "Frazer Road", state: "Patna", name: "Patna (800001) - Traditional Silk" }
};

// Regional date profile presets
// Weather Matrix throughout the year for the three zip codes
const WEATHER_MATRIX = {
  "560034": { // Koramangala, Bengaluru
    1: { desc: "Pleasant & Breezy 🍃", temp: "18°C–27°C", cold_wave: false, hot_wave: false, rainy: false },
    2: { desc: "Breezy & Warm 🍃", temp: "19°C–29°C", cold_wave: false, hot_wave: false, rainy: false },
    3: { desc: "Warm & Sunny ☀️", temp: "21°C–32°C", cold_wave: false, hot_wave: false, rainy: false },
    4: { desc: "Warm & Dry ☀️", temp: "22°C–34°C", cold_wave: false, hot_wave: false, rainy: false },
    5: { desc: "Pre-Monsoon Showers 🌧️", temp: "21°C–33°C", cold_wave: false, hot_wave: false, rainy: true },
    6: { desc: "Cool & Rainy 🌧️", temp: "20°C–29°C", cold_wave: false, hot_wave: false, rainy: true },
    7: { desc: "Monsoon Breezes 🌧️", temp: "19°C–28°C", cold_wave: false, hot_wave: false, rainy: true },
    8: { desc: "Cloudy & Rainy 🌧️", temp: "19°C–27°C", cold_wave: false, hot_wave: false, rainy: true },
    9: { desc: "Pleasant Showers 🌧️", temp: "19°C–28°C", cold_wave: false, hot_wave: false, rainy: true },
    10: { desc: "Cool & Pleasant 🍂", temp: "19°C–28°C", cold_wave: false, hot_wave: false, rainy: false },
    11: { desc: "Cool & Cozy 🍃", temp: "18°C–27°C", cold_wave: false, hot_wave: false, rainy: false },
    12: { desc: "Pleasant Winter ❄️", temp: "16°C–26°C", cold_wave: false, hot_wave: false, rainy: false }
  },
  "110049": { // South Ext, Delhi
    1: { desc: "Cold & Foggy ❄️", temp: "7°C–18°C", cold_wave: true, hot_wave: false, rainy: false },
    2: { desc: "Pleasant & Sunny ☀️", temp: "10°C–24°C", cold_wave: false, hot_wave: false, rainy: false },
    3: { desc: "Getting Hot ☀️", temp: "15°C–30°C", cold_wave: false, hot_wave: false, rainy: false },
    4: { desc: "Hot & Dry 🔥", temp: "20°C–36°C", cold_wave: false, hot_wave: true, rainy: false },
    5: { desc: "Extreme Heatwave 🔥", temp: "25°C–41°C", cold_wave: false, hot_wave: true, rainy: false },
    6: { desc: "Extreme Heat & Humid 🔥", temp: "27°C–39°C", cold_wave: false, hot_wave: true, rainy: false },
    7: { desc: "Hot & Monsoon 🌧️", temp: "26°C–34°C", cold_wave: false, hot_wave: false, rainy: true },
    8: { desc: "Humid & Wet 🌧️", temp: "26°C–33°C", cold_wave: false, hot_wave: false, rainy: true },
    9: { desc: "Humid & Pleasant 🍃", temp: "23°C–33°C", cold_wave: false, hot_wave: false, rainy: true },
    10: { desc: "Pleasant Autumn 🍂", temp: "18°C–31°C", cold_wave: false, hot_wave: false, rainy: false },
    11: { desc: "Cool & Dry 🍂", temp: "12°C–26°C", cold_wave: false, hot_wave: false, rainy: false },
    12: { desc: "Very Cold Winter ❄️", temp: "8°C–20°C", cold_wave: true, hot_wave: false, rainy: false }
  },
  "800001": { // Frazer Road, Patna
    1: { desc: "Cold & Foggy ❄️", temp: "9°C–21°C", cold_wave: true, hot_wave: false, rainy: false },
    2: { desc: "Warm & Dry ☀️", temp: "12°C–26°C", cold_wave: false, hot_wave: false, rainy: false },
    3: { desc: "Getting Hot ☀️", temp: "17°C–33°C", cold_wave: false, hot_wave: false, rainy: false },
    4: { desc: "Hot & Dry 🔥", temp: "21°C–38°C", cold_wave: false, hot_wave: true, rainy: false },
    5: { desc: "Very Hot 🔥", temp: "24°C–39°C", cold_wave: false, hot_wave: true, rainy: false },
    6: { desc: "Hot & Humid 🌡️", temp: "25°C–35°C", cold_wave: false, hot_wave: true, rainy: false },
    7: { desc: "Hot & Monsoon 🌧️", temp: "26°C–33°C", cold_wave: false, hot_wave: false, rainy: true },
    8: { desc: "Humid & Wet 🌧️", temp: "25°C–32°C", cold_wave: false, hot_wave: false, rainy: true },
    9: { desc: "Humid 🌧️", temp: "24°C–32°C", cold_wave: false, hot_wave: false, rainy: true },
    10: { desc: "Pleasant 🍂", temp: "20°C–30°C", cold_wave: false, hot_wave: false, rainy: false },
    11: { desc: "Cool & Dry 🍂", temp: "15°C–27°C", cold_wave: false, hot_wave: false, rainy: false },
    12: { desc: "Cold & Dry ❄️", temp: "10°C–22°C", cold_wave: true, hot_wave: false, rainy: false }
  }
};

const getPresetWeather = (zip, dateStr) => {
  try {
    const month = parseInt(dateStr.split("-")[1], 10);
    return WEATHER_MATRIX[zip]?.[month] || { desc: "Pleasant & Breezy 🍃", temp: "22°C" };
  } catch {
    return { desc: "Pleasant & Breezy 🍃", temp: "22°C" };
  }
};

// Regional date profile presets
const REGIONAL_DATE_PRESETS = {
  "800001": [
    { key: "jan_26", label: "Jan 26 (Republic Day)", dateStr: "2026-01-26", event: "Republic Day Parade", event_type: "festival", isFestive: true, trendingTags: ["white", "saffron", "green", "ethnic", "formal"] },
    { key: "feb_2", label: "Feb 2 (Saraswati Puja)", dateStr: "2026-02-02", event: "Saraswati Puja (Vasant Panchami)", event_type: "festival", isFestive: true, trendingTags: ["saree", "kurta", "yellow", "ethnic"] },
    { key: "mar_3", label: "Mar 3 (Holi)", dateStr: "2026-03-03", event: "Holi Festival of Colors", event_type: "festival", isFestive: true, trendingTags: ["white", "cotton", "casual", "dailywear"] },
    { key: "mar_20", label: "Mar 20 (Eid-ul-Fitr)", dateStr: "2026-03-20", event: "Eid-ul-Fitr Celebration", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "traditional_embroidery", "embroidered", "kurta", "sherwani"] },
    { key: "apr_10", label: "Apr 10 (Farewell)", dateStr: "2026-04-10", event: "College Farewell Gala", event_type: "festival", isFestive: true, trendingTags: ["formal", "saree", "suit", "ethnic"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["formal", "ethnic", "fusion"] },
    { key: "jul_15", label: "Jul 15 (Admissions)", dateStr: "2026-07-15", event: "College Admissions Season", event_type: "festival", isFestive: false, trendingTags: ["smart_casual", "breathable_cotton", "modest_fusion", "summer_wear"] },
    { key: "aug_15", label: "Aug 15 (Independence Day)", dateStr: "2026-08-15", event: "Independence Day Ceremony", event_type: "festival", isFestive: true, trendingTags: ["saffron", "white", "green", "ethnic", "formal", "cotton"] },
    { key: "oct_18", label: "Oct 18 (Durga Puja)", dateStr: "2026-10-18", event: "Durga Puja Peak Pandals", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "silk", "saree", "heavy_silk", "traditional"] },
    { key: "nov_8", label: "Nov 8 (Diwali)", dateStr: "2026-11-08", event: "Diwali Lights Festival", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "traditional", "regal", "gold", "silk"] },
    { key: "nov_15", label: "Nov 15 (Chhath Puja)", dateStr: "2026-11-15", event: "Chhath Puja (Sandhya Arghya)", event_type: "festival", isFestive: true, trendingTags: ["saree", "cotton", "traditional", "dhoti", "saffron", "yellow", "white", "patna", "chhath-puja"] },
    { key: "dec_10", label: "Dec 10 (Wedding Day)", dateStr: "2026-12-10", event: "Patna Wedding Day (Pheras Ritual)", event_type: "wedding_day", isFestive: true, trendingTags: ["heavy_silk", "traditional_embroidery", "ceremonial", "silk", "saree", "sherwani", "crimson", "gold", "maroon"] },
    { key: "dec_25", label: "Dec 25 (Christmas)", dateStr: "2026-12-25", event: "Christmas Day Celebrations", event_type: "festival", isFestive: true, trendingTags: ["winter", "party", "jacket", "velvet", "warm"] }
  ],
  "560034": [
    { key: "jan_20", label: "Jan 20 (Biennale Peak)", dateStr: "2026-01-20", event: "Kochi-Muziris Biennale Peak", event_type: "festival", isFestive: true, trendingTags: ["artsy", "bohemian", "linen", "sustainable", "modern"] },
    { key: "jan_26", label: "Jan 26 (Republic Day)", dateStr: "2026-01-26", event: "Republic Day Parade", event_type: "festival", isFestive: true, trendingTags: ["white", "fusion", "formal", "lightweight"] },
    { key: "mar_3", label: "Mar 3 (Holi)", dateStr: "2026-03-03", event: "Holi Festival of Colors", event_type: "festival", isFestive: true, trendingTags: ["casual", "streetwear", "denim", "cotton"] },
    { key: "mar_20", label: "Mar 20 (Eid-ul-Fitr)", dateStr: "2026-03-20", event: "Eid-ul-Fitr Celebration", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "modest", "elegant"] },
    { key: "apr_10", label: "Apr 10 (Farewell)", dateStr: "2026-04-10", event: "College Farewell Gala", event_type: "festival", isFestive: true, trendingTags: ["pastel", "fusion", "cotton", "lightweight"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["formal", "elegant", "premium"] },
    { key: "jul_15", label: "Jul 15 (Admissions)", dateStr: "2026-07-15", event: "College Admissions Season", event_type: "festival", isFestive: false, trendingTags: ["monsoon_ready", "contemporary_casual", "dark_tones", "minimalist"] },
    { key: "aug_15", label: "Aug 15 (Independence Day)", dateStr: "2026-08-15", event: "Independence Day Ceremony", event_type: "festival", isFestive: true, trendingTags: ["saffron", "white", "green", "ethnic", "formal", "lightweight"] },
    { key: "aug_27", label: "Aug 27 (Onam Thiruvonam)", dateStr: "2026-08-27", event: "Onam Festival (Thiruvonam)", event_type: "festival", isFestive: true, trendingTags: ["saree", "mundu", "kasavu_weave", "white", "cream", "gold"] },
    { key: "oct_18", label: "Oct 18 (Durga Puja)", dateStr: "2026-10-18", event: "Durga Puja Celebrations", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "minimalist", "cotton"] },
    { key: "nov_8", label: "Nov 8 (Diwali)", dateStr: "2026-11-08", event: "Diwali Lights Festival", event_type: "festival", isFestive: true, trendingTags: ["ethnic", "festive", "contemporary_fusion", "fusion", "earth-tones"] },
    { key: "dec_25", label: "Dec 25 (Christmas)", dateStr: "2026-12-25", event: "Christmas Day Celebrations", event_type: "festival", isFestive: true, trendingTags: ["vibrant", "party", "bohemian", "modern", "western"] },
    { key: "dec_27", label: "Dec 27 (Wedding Day)", dateStr: "2026-12-27", event: "Kochi Wedding Day (Thalikettu)", event_type: "wedding_day", isFestive: true, trendingTags: ["kasavu_weave", "off-white", "cream", "gold"] }
  ],
  "110049": [
    { key: "jan_26", label: "Jan 26 (Republic Day)", dateStr: "2026-01-26", event: "Republic Day Parade", event_type: "festival", isFestive: true, trendingTags: ["white", "saffron", "green", "winter", "jacket", "formal"] },
    { key: "mar_3", label: "Mar 3 (Holi)", dateStr: "2026-03-03", event: "Holi Festival of Colors", event_type: "festival", isFestive: true, trendingTags: ["hoodie", "winter", "warm", "streetwear"] },
    { key: "mar_20", label: "Mar 20 (Eid-ul-Fitr)", dateStr: "2026-03-20", event: "Eid-ul-Fitr Celebration", event_type: "festival", isFestive: true, trendingTags: ["western_formal", "modest", "fusion"] },
    { key: "apr_10", label: "Apr 10 (Farewell)", dateStr: "2026-04-10", event: "College Farewell Gala", event_type: "festival", isFestive: true, trendingTags: ["western_formal", "navy", "black", "grey", "blazer", "suit"] },
    { key: "apr_15", label: "Apr 15 (Harvest Fest)", dateStr: "2026-04-15", event: "Shad Suk Mynsiem Harvest Fest", event_type: "festival", isFestive: true, trendingTags: ["jainsem", "jymphong", "traditional", "ethnic", "silk"] },
    { key: "may_15", label: "May 15 (Graduation)", dateStr: "2026-05-15", event: "Annual Convocation Ceremony", event_type: "festival", isFestive: true, trendingTags: ["western_formal", "suit", "gown", "blazer"] },
    { key: "jul_15", label: "Jul 15 (Admissions)", dateStr: "2026-07-15", event: "College Admissions Season", event_type: "festival", isFestive: false, trendingTags: ["streetwear", "light_layers", "western_casual", "trendy_youth"] },
    { key: "aug_15", label: "Aug 15 (Independence Day)", dateStr: "2026-08-15", event: "Independence Day Ceremony", event_type: "festival", isFestive: true, trendingTags: ["saffron", "white", "green", "formal", "jacket", "layered"] },
    { key: "oct_18", label: "Oct 18 (Durga Puja)", dateStr: "2026-10-18", event: "Durga Puja Autumn Fusion", event_type: "festival", isFestive: true, trendingTags: ["streetwear", "fusion", "modern"] },
    { key: "nov_8", label: "Nov 8 (Diwali)", dateStr: "2026-11-08", event: "Diwali Festival of Lights", event_type: "festival", isFestive: true, trendingTags: ["winter", "warm", "jacket", "velvet", "festive"] },
    { key: "nov_15", label: "Nov 15 (Cherry Blossom)", dateStr: "2026-11-15", event: "Shillong Cherry Blossom Fest", event_type: "festival", isFestive: true, trendingTags: ["streetwear", "jacket", "coat", "scarf", "boots"] },
    { key: "dec_20", label: "Dec 20 (Khasi Wedding Day)", dateStr: "2026-12-20", event: "Shillong Wedding Day (Traditional)", event_type: "wedding_day", isFestive: true, trendingTags: ["handwoven_silk", "tribal_heritage", "jainsem", "jymphong", "earth-tones"] },
    { key: "dec_25", label: "Dec 25 (Christmas Day)", dateStr: "2026-12-25", event: "Christmas Day Celebration", event_type: "festival", isFestive: true, trendingTags: ["velvet", "woolen", "dress", "formal", "winter", "premium"] }
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

// Local velocity cache (mirrors backend LOCAL_VELOCITY_CACHE for offline mode)
const LOCAL_VELOCITY_CACHE = {
  // Patna
  1:  { velocity_score: 0.92, units_last_hour: 47 },
  2:  { velocity_score: 0.88, units_last_hour: 38 },
  7:  { velocity_score: 0.75, units_last_hour: 22 },
  9:  { velocity_score: 0.65, units_last_hour: 18 },
  13: { velocity_score: 0.70, units_last_hour: 20 },
  15: { velocity_score: 0.80, units_last_hour: 30 },
  11: { velocity_score: 0.55, units_last_hour: 12 },
  48: { velocity_score: 0.60, units_last_hour: 15 },
  6:  { velocity_score: 0.72, units_last_hour: 24 },
  // Kochi
  16: { velocity_score: 0.95, units_last_hour: 52 },
  17: { velocity_score: 0.85, units_last_hour: 35 },
  25: { velocity_score: 0.78, units_last_hour: 28 },
  28: { velocity_score: 0.70, units_last_hour: 20 },
  20: { velocity_score: 0.62, units_last_hour: 16 },
  26: { velocity_score: 0.55, units_last_hour: 11 },
  23: { velocity_score: 0.50, units_last_hour:  9 },
  24: { velocity_score: 0.58, units_last_hour: 14 },
  30: { velocity_score: 0.45, units_last_hour:  7 },
  // Shillong
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
  const [currentZipCode, setCurrentZipCode] = useState("800001");
  const [sliderVal, setSliderVal] = useState(0);
  const [currentVibe, setCurrentVibe] = useState("casual");
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [lookCompleter, setLookCompleter] = useState({ accessory: null, footwear: null });
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [tempVibe, setTempVibe] = useState("casual");
  const [logs, setLogs] = useState([]);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [isLoading, setIsLoading] = useState(false);
  
  // Trends Panel State — data is only fetched on first tab click, never auto-loaded
  const [activeTab, setActiveTab] = useState('youtube');
  const [youtubeData, setYoutubeData] = useState(null);      // null = not yet fetched
  const [isYoutubeLoading, setIsYoutubeLoading] = useState(false);
  const [boutiqueData, setBoutiqueData] = useState(null);     // null = not yet fetched
  const [isBoutiqueLoading, setIsBoutiqueLoading] = useState(false);
  const [youtubeFetched, setYoutubeFetched] = useState(false);
  const [boutiqueFetched, setBoutiqueFetched] = useState(false);
  
  const consoleEndRef = useRef(null);

  // Active date profile list based on zip code
  const dateProfiles = REGIONAL_DATE_PRESETS[currentZipCode] || REGIONAL_DATE_PRESETS["800001"];
  const activeDateProfile = dateProfiles[sliderVal] || dateProfiles[0];

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
      setCurrentZipCode("800001");
    }
  }, [currentZipCode]);

  useEffect(() => {
    logMessage("Initializing Myntra PinPulse Tri-Layer recommendation engine...", "info");
    const activeZip = ZIP_CODES[currentZipCode] || ZIP_CODES["800001"];
    logMessage(`Geographic boundary boundary: ${activeZip.name}.`, "info");
    logMessage("Loaded local fallback catalog database containing 60 items.", "success");
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/system-state");
      if (res.ok) {
        setBackendStatus("connected");
        logMessage("FastAPI application server detected online at http://localhost:8000.", "success");
      } else {
        throw new Error();
      }
    } catch {
      setBackendStatus("offline");
      logMessage("FastAPI server offline. Activating client-side vector search and ranking subsystem.", "warning");
    }
  };

  // Reset fetched state when zip code changes so stale data is cleared
  useEffect(() => {
    setYoutubeData(null);
    setBoutiqueData(null);
    setYoutubeFetched(false);
    setBoutiqueFetched(false);
  }, [currentZipCode]);

  // Re-run connection check when zip code or state changes
  useEffect(() => {
    if (backendStatus !== "checking") {
      updateRecommendations();
    }
  }, [currentZipCode, sliderVal, currentVibe, backendStatus]);

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
        // Local Fallback simulation - IDs verified against catalog (1-159):
        // ID=124: Heavy kundan necklace set
        // ID=127: Traditional silver anklets
        // ID=135: Minimalist gold earring set
        // ID=149: Modern ankle boots for women
        // ID=38: Wangala Tribal Beaded Vest
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

  const handleZipCodeChange = (e) => {
    const zip = e.target.value;
    setCurrentZipCode(zip);
    setSliderVal(0); // Reset slider to index 0 on zip shift
    logMessage(`Geographic boundary shifted. Active zip code: ${ZIP_CODES[zip].name}.`, "success");
  };

  const handleSliderChange = (e) => {
    const val = parseInt(e.target.value);
    setSliderVal(val);
    const profile = REGIONAL_DATE_PRESETS[currentZipCode][val];
    logMessage(`Time slider shifted. Active regional scenario: ${profile.label}.`, "info");
  };

  const updateRecommendations = async () => {
    setIsLoading(true);
    const profile = REGIONAL_DATE_PRESETS[currentZipCode][sliderVal] || REGIONAL_DATE_PRESETS[currentZipCode][0];
    const userVibeVector = generateVibeVector(currentVibe);
    
    logMessage(`Querying recommendations: zip='${currentZipCode}' date='${profile.dateStr}' vibe='${currentVibe}'`, "info");
    
    if (backendStatus === "connected") {
      try {
        logMessage("Executing Hybrid Vector matching via Supabase RPC...", "sql");
        const url = `http://localhost:8000/api/products?zip_code=${currentZipCode}&date=${profile.dateStr}&vibe=${currentVibe}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error("API responded with error code");
        
        const data = await response.json();
        setProducts(data);
        logMessage(`SQL query successful. Retreived ${data.length} products ordered by composite score.`, "success");
        
        if (data.length > 0) {
          setSelectedProduct(data[0]);
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
      const res = await fetch(`http://localhost:8000/api/trends/youtube?zip_code=${zip || currentZipCode}`);
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
      setYoutubeFetched(true); // Mark as fetched even on error so we show error state
    }
  };

  const fetchBoutiques = async (zip) => {
    setIsBoutiqueLoading(true);
    setBoutiqueData(null);
    logMessage(`Loading local stores for ${ZIP_CODES[zip || currentZipCode]?.city}...`, "info");
    try {
      const res = await fetch(`http://localhost:8000/api/trends/boutiques?zip_code=${zip || currentZipCode}`);
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

  // Called when user clicks a tab — only fetch if not already loaded for current zip
  const handleTabClick = (tab) => {
    setActiveTab(tab);
    if (tab === 'youtube' && !youtubeFetched) {
      fetchYoutubeTrends(currentZipCode);
    }
    if (tab === 'boutiques' && !boutiqueFetched) {
      fetchBoutiques(currentZipCode);
    }
  };

  const runLocalRecommendationCalculator = (profile, userVibeVector) => {
    logMessage("Running client-side vector cosine distance similarity calculations...", "sql");
    
    const month = parseInt(profile.dateStr.split("-")[1], 10);
    const weatherEntry = WEATHER_MATRIX[currentZipCode]?.[month] || {};
    const isColdWave = weatherEntry.cold_wave || false;
    const isHotWave = weatherEntry.hot_wave || false;
    const isRainy = weatherEntry.rainy || false;
    const isWeddingDay = (profile.event_type === "wedding_day");
    
    logMessage(`Active Event: '${profile.event}' | Type: '${profile.event_type}'`, "info");
    logMessage(`Active Weather: '${weatherEntry.desc}' | Temp Range: '${weatherEntry.temp}'`, "info");
    logMessage(`Trending active tags: [${profile.trendingTags.join(", ")}]`, "info");
    
    const computed = FALLBACK_PRODUCTS.filter(product => {
      // Geographic filter
      if (product.zip_codes && product.zip_codes.length > 0) {
        return product.zip_codes.includes(currentZipCode);
      }
      return true; // Global
    }).map(product => {
      // Cosine similarity
      const productVibeVector = generateVibeVector(product.tags);
      const similarity = calculateCosineSimilarity(userVibeVector, productVibeVector);
      
      // Tag overlap score against trending/event tags
      const overlapTags = product.tags.filter(tag => profile.trendingTags.includes(tag));
      const tagScore = overlapTags.length;
      
      // Determine boosts
      let climateBoost = 0.0;
      let festiveBoost = 0.0;
      let weddingBoost = 0.0;
      let eventBoost = 0.0;
      let hotBoost = 0.0;
      let rainyBoost = 0.0;
      
      if (isColdWave && product.tags.includes("winter")) {
        climateBoost = 0.15;
      }
      if (isHotWave && (product.tags.includes("summer") || product.tags.includes("breathable"))) {
        hotBoost = 0.15;
      }
      if (isRainy && (product.tags.includes("cotton") || product.tags.includes("breathable"))) {
        rainyBoost = 0.15;
      }
      if (profile.isFestive && product.tags.includes("festive")) {
        festiveBoost = 0.15;
      }
      if (isWeddingDay && product.tags.includes("ceremonial")) {
        weddingBoost = 0.30;
      }
      // Target event tag intersection boost
      if (profile.trendingTags.length > 0 && product.tags.some(t => profile.trendingTags.includes(t))) {
        eventBoost = 0.15;
      }
      
      const boostScore = climateBoost + festiveBoost + weddingBoost + eventBoost + hotBoost + rainyBoost;
      
      // Checkout Velocity Boost (mirrors backend: max +0.20 for viral items)
      const velocityEntry = LOCAL_VELOCITY_CACHE[product.id] || {};
      const vScore = velocityEntry.velocity_score || 0.0;
      const unitsLastHour = velocityEntry.units_last_hour || 0;
      const velocityBoost = vScore > 0 ? parseFloat((vScore * 0.20).toFixed(4)) : 0.0;
      const isTrending = vScore >= 0.75;
      
      const visualScoreVal = Math.max(0.0, Math.min(1.0, similarity));
      const normalizedTagScore = Math.min(1.0, tagScore / 3);
      
      // Base hybrid score + velocity boost (mirrors backend formula)
      let finalScore = (visualScoreVal * 0.4) + (normalizedTagScore * 0.3) + (boostScore * 0.3) + velocityBoost;
      
      // --- APPLY STRICT HACKATHON LOGIC RULES ---
      
      // Patna Wedding Day: Heavy silk must dominate, lightweight summerwear penalized
      if (currentZipCode === "800008" && isWeddingDay) {
        if (product.tags.includes("heavy_silk")) {
          finalScore += 0.50;
        } else if (product.tags.includes("summer") || product.tags.includes("casual")) {
          finalScore -= 0.50; // Heavy penalty
        }
      }
      
      // Kochi Wedding Day: Kasavu saree is non-negotiable
      if (currentZipCode === "682001" && isWeddingDay) {
        if (product.tags.includes("kasavu_weave")) {
          finalScore += 0.50;
        }
      }
      
      // Shillong Wedding Day: Jainsem & Jymphong boost
      if (currentZipCode === "793003" && isWeddingDay) {
        if (product.tags.includes("handwoven_silk") || product.tags.includes("tribal_heritage")) {
          finalScore += 0.50;
        }
      }
      
      return {
        ...product,
        vector_score: visualScoreVal,
        tag_score: normalizedTagScore,
        boost_score: boostScore,
        velocity_score: vScore,
        velocity_boost: velocityBoost,
        units_last_hour: unitsLastHour,
        is_trending: isTrending,
        final_score: finalScore,
        overlap_tags: overlapTags
      };
    });
    
    // Sort descending by final score
    computed.sort((a, b) => b.final_score - a.final_score);
    
    setProducts(computed);
    logMessage(`Local matching algorithm ranked ${computed.length} items. Velocity boosts applied.`, "success");
    if (computed.filter(p => p.is_trending).length > 0) {
      logMessage(`⚡ ${computed.filter(p => p.is_trending).length} trending items detected via checkout velocity.`, "success");
    }
    
    if (computed.length > 0) {
      setSelectedProduct(computed[0]);
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
          
          <div className={`meta-pill ${backendStatus === 'connected' ? 'highlight' : ''}`}>
            Status: {backendStatus === "connected" ? "FastAPI Online" : "FastAPI Offline (Local Sim)"}
          </div>
          <div className="meta-pill">
            📅 {activeDateProfile.dateStr}
          </div>
          <div className="meta-pill highlight">
            ⚡ Vibe: {VIBE_DEFINITIONS[currentVibe].name}
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
              <div style={{ display: 'flex', gap: '10px' }}>
                <button className="onboarding-btn" style={{ background: '#ec4899', border: 'none' }} onClick={() => {
                  // Reset fetched state to force re-fetch on next tab click
                  if (activeTab === 'youtube') { setYoutubeFetched(false); fetchYoutubeTrends(currentZipCode); }
                  if (activeTab === 'boutiques') { setBoutiqueFetched(false); fetchBoutiques(currentZipCode); }
                }}>
                  🎬 Refresh Trends
                </button>
                <button className="onboarding-btn" onClick={() => setShowOnboarding(true)}>
                  🔄 Vibe Check
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
                         getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("9°") ? '#06b6d4' : 
                         getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("39°") || 
                         getPresetWeather(currentZipCode, activeDateProfile.dateStr).temp.includes("38°") ? '#ef4444' : 'white'
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
                <div className="factor-value" style={{fontSize: '0.75rem', color: '#ff3f6c', lineHeight: '1.2'}}>
                  {activeDateProfile.event}
                </div>
              </div>
              <div className="factor-box">
                <div className="factor-title">Active Surge</div>
                <div className="factor-value" style={{fontSize: '0.8rem', color: '#bef264'}}>
                  {activeDateProfile.event_type === 'wedding_day' ? 'Wedding Surge 💍' : activeDateProfile.isFestive ? 'Festive Surge 🥻' : 'None'}
                </div>
              </div>
            </div>
          </div>
          
          {/* Feed Header */}
          <div className="feed-header">
            <h2>🛒 Hyper-Local Ranked Feed ({products.length} Items)</h2>
            <div className="meta-pill">
              Filtered for {ZIP_CODES[currentZipCode].city} • Cosine match + regional surges
            </div>
          </div>
          
          {/* Product Feed Grid */}
          {isLoading ? (
            <div className="spinner"></div>
          ) : (
            <div className="catalog-grid">
              {products.map((product, idx) => {
                const hasWeddingSurge = (activeDateProfile.event_type === "wedding_day") && product.tags.includes("ceremonial");
                const hasFestiveSurge = activeDateProfile.isFestive && product.tags.includes("festive") && !hasWeddingSurge;
                const isMicroCreator = product.tags.includes("micro_creator");
                
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
                        <div className="surge-pill" style={{ background: '#a855f7', color: 'white', top: '40px', left: '8px', bottom: 'auto' }}>
                          Micro-Creator 🌾
                        </div>
                      )}
                      
                      {product.is_trending && (
                        <div className="surge-pill" style={{ background: 'linear-gradient(135deg, #f97316, #ef4444)', color: 'white', top: isMicroCreator ? '68px' : '40px', left: '8px', bottom: 'auto', fontWeight: '800' }}>
                          🔥 Trending
                        </div>
                      )}
                      
                      {hasWeddingSurge && (
                        <div className="surge-pill" style={{ background: '#ec4899', color: 'white' }}>Wedding Surge 💍</div>
                      )}
                      {hasFestiveSurge && (
                        <div className="surge-pill festive">Festive Surge 🥻</div>
                      )}
                    </div>
                    
                    <div className="product-info">
                      <p className="product-category" style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{product.category}</span>
                        {product.zip_codes && product.zip_codes.length > 0 && (
                          <span style={{ color: '#ec4899', fontWeight: 'bold' }}>LOCAL</span>
                        )}
                      </p>
                      <h4 className="product-name">{product.name}</h4>
                      <div className="product-tags">
                        {product.tags.slice(0, 3).map(tag => (
                          <span 
                            key={tag} 
                            className={`product-tag ${activeDateProfile.trendingTags.includes(tag) ? 'highlight' : ''}`}
                          >
                            #{tag}
                          </span>
                        ))}
                        {product.tags.length > 3 && (
                          <span className="product-tag">+{product.tags.length - 3}</span>
                        )}
                      </div>
                      {product.product_url && (
                        <div style={{ marginTop: '10px' }}>
                          <a 
                            href={product.product_url} 
                            target="_blank" 
                            rel="noreferrer"
                            style={{ 
                              display: 'inline-block', 
                              padding: '5px 10px', 
                              background: '#ff3f6c', 
                              color: 'white', 
                              textDecoration: 'none', 
                              borderRadius: '4px', 
                              fontSize: '0.8rem',
                              fontWeight: 'bold'
                            }}
                            onClick={(e) => e.stopPropagation()}
                          >
                            🛍️ Buy on Myntra
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
        
        {/* Right Side: Logs Terminal + Decision Tracker Panel */}
        <div className="dev-console-panel">
          
          {/* Logs Terminal */}
          <div className="console-card">
            <div className="console-header">
              <span className="console-header-title">
                <span className="console-pulse"></span> SYSTEM REALTIME LOGS MONITOR
              </span>
              <span style={{fontSize: '0.65rem', color: '#6b7280', fontFamily: 'monospace'}}>
                ACTIVE PORT: 8000
              </span>
            </div>
            
            <div className="console-lines">
              {logs.map((log, index) => (
                <div key={index} className="log-line">
                  <span className="log-time">[{log.time}]</span>
                  <span className={`log-${log.type}`}>
                    {log.type === 'sql' ? '⚡ SQL: ' : log.type === 'warning' ? '⚠ WARN: ' : log.type === 'error' ? '✖ ERR: ' : 'ℹ SYSTEM: '}
                    {log.text}
                  </span>
                </div>
              ))}
              <div ref={consoleEndRef} />
            </div>
          </div>
          
          {/* Decision Math Dissection Panel */}
          <div className="decision-card">
            <h3 className="decision-title">
              🔬 Score Decision Dissect
            </h3>
            
            {selectedProduct ? (
              <div className="metrics-breakdown">
                <h4 style={{margin: '0 0 5px 0', fontSize: '0.95rem', color: 'white'}}>
                  {selectedProduct.name}
                </h4>
                <p style={{fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0 0 10px 0'}}>
                  {selectedProduct.description}
                </p>
                
                {/* Metric 1: Vector similarity */}
                <div className="metric-row">
                  <div className="metric-info">
                    <span className="metric-name">
                      🧠 Visual Vibe Similarity (CLIP)
                    </span>
                    <span className="metric-val">
                      {(selectedProduct.vector_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric-bar-bg">
                    <div 
                      className="metric-bar-fill vibe" 
                      style={{width: `${selectedProduct.vector_score * 100}%`}}
                    />
                  </div>
                </div>

                {/* Metric 2: Trending Tag Overlap */}
                <div className="metric-row">
                  <div className="metric-info">
                    <span className="metric-name">
                      📈 Youtube/Event Tag Overlap
                    </span>
                    <span className="metric-val">
                      {(selectedProduct.tag_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="metric-bar-bg">
                    <div 
                      className="metric-bar-fill tag" 
                      style={{width: `${selectedProduct.tag_score * 100}%`}}
                    />
                  </div>
                </div>

                {/* Metric 3: Climate/Festive Boost */}
                <div className="metric-row">
                  <div className="metric-info">
                    <span className="metric-name">
                      ⚡ Dynamic Surge Boost
                    </span>
                    <span className="metric-val">
                      {selectedProduct.boost_score > 0 ? `+${(selectedProduct.boost_score * 100).toFixed(0)}%` : '0%'}
                    </span>
                  </div>
                  <div className="metric-bar-bg">
                    <div 
                      className="metric-bar-fill boost" 
                      style={{width: `${selectedProduct.boost_score > 0 ? Math.min(100, (selectedProduct.boost_score / 0.6) * 100) : 0}%`}}
                    />
                  </div>
                </div>

                {/* Metric 4: Checkout Velocity */}
                <div className="metric-row">
                  <div className="metric-info">
                    <span className="metric-name" style={{ color: selectedProduct.is_trending ? '#f97316' : 'inherit' }}>
                      🔥 Checkout Velocity {selectedProduct.is_trending ? '(TRENDING)' : ''}
                    </span>
                    <span className="metric-val" style={{ color: selectedProduct.is_trending ? '#f97316' : 'inherit' }}>
                      {selectedProduct.velocity_score != null ? `${(selectedProduct.velocity_score * 100).toFixed(0)}%` : 'N/A'}
                    </span>
                  </div>
                  <div className="metric-bar-bg">
                    <div 
                      className="metric-bar-fill" 
                      style={{
                        width: `${selectedProduct.velocity_score != null ? selectedProduct.velocity_score * 100 : 0}%`,
                        background: selectedProduct.is_trending ? 'linear-gradient(90deg, #f97316, #ef4444)' : 'rgba(107,114,128,0.4)'
                      }}
                    />
                  </div>
                  {selectedProduct.units_last_hour > 0 && (
                    <div style={{ fontSize: '0.7rem', color: '#9ca3af', marginTop: '2px' }}>
                      {selectedProduct.units_last_hour} units sold in last hour · Velocity Boost: +{((selectedProduct.velocity_boost || 0) * 100).toFixed(1)}%
                    </div>
                  )}
                </div>

                {/* Mathematical Equation output */}
                <div className="vector-matches-section" style={{marginTop: '10px'}}>
                  <h4>Matched Active Surge Tags</h4>
                  {selectedProduct.overlap_tags && selectedProduct.overlap_tags.length > 0 ? (
                    <div className="tag-match-list">
                      {selectedProduct.overlap_tags.map(tag => (
                        <span key={tag} className="match-pill">{tag}</span>
                      ))}
                    </div>
                  ) : (
                    <p style={{fontSize: '0.75rem', color: '#6b7280', margin: '0'}}>No active tag matches</p>
                  )}
                </div>

                <div className="metric-formula-box">
                  <strong style={{color: '#ff3f6c', display: 'block', marginBottom: '4px'}}>
                    Composite Engine Formula:
                  </strong>
                  <code>
                    Base_Score = (0.4 * Visual) + (0.3 * Trend) + (0.3 * Boost) + Velocity<br />
                    Base_Score = (0.4 × {selectedProduct.vector_score.toFixed(3)}) + (0.3 × {selectedProduct.tag_score.toFixed(3)}) + (0.3 × {selectedProduct.boost_score.toFixed(3)}) + {(selectedProduct.velocity_boost || 0).toFixed(4)} = {((selectedProduct.vector_score * 0.4) + (selectedProduct.tag_score * 0.3) + (selectedProduct.boost_score * 0.3) + (selectedProduct.velocity_boost || 0)).toFixed(4)}<br />
                    
                    {/* Specific rules print */}
                    {currentZipCode === "800008" && activeDateProfile.event_type === "wedding_day" && (
                      <span style={{ color: '#fb7185', display: 'block', marginTop: '4px' }}>
                        * Patna Wedding Day Rule applied: {selectedProduct.tags.includes("heavy_silk") ? "+0.50 (heavy silk boost)" : (selectedProduct.tags.includes("summer") || selectedProduct.tags.includes("casual")) ? "-0.50 (lightwear penalty)" : "0.0"}
                      </span>
                    )}
                    {currentZipCode === "682001" && activeDateProfile.event_type === "wedding_day" && (
                      <span style={{ color: '#fb7185', display: 'block', marginTop: '4px' }}>
                        * Kochi Wedding Day Rule applied: {selectedProduct.tags.includes("kasavu_weave") ? "+0.50 (Kasavu weave boost)" : "0.0"}
                      </span>
                    )}
                    {currentZipCode === "793003" && activeDateProfile.event_type === "wedding_day" && (
                      <span style={{ color: '#fb7185', display: 'block', marginTop: '4px' }}>
                        * Shillong Wedding Day Rule applied: {(selectedProduct.tags.includes("handwoven_silk") || selectedProduct.tags.includes("tribal_heritage")) ? "+0.50 (handwoven Khasi heritage boost)" : "0.0"}
                      </span>
                    )}
                    {selectedProduct.velocity_score > 0 && (
                      <span style={{ color: '#f97316', display: 'block', marginTop: '4px' }}>
                        * Checkout Velocity Boost: +{((selectedProduct.velocity_boost || 0) * 100).toFixed(1)}% ({selectedProduct.units_last_hour} units/hr)
                      </span>
                    )}
                    
                    Final Ranked Score = <strong style={{color: 'white'}}>{selectedProduct.final_score.toFixed(4)} ({(selectedProduct.final_score * 100).toFixed(1)}%)</strong>
                  </code>
                </div>

                {/* --- LOOK COMPLETER CROSS-CATEGORY STYLING SECTION --- */}
                {(lookCompleter.accessory || lookCompleter.footwear) && (
                  <div className="look-completer-section" style={{
                    marginTop: '20px',
                    padding: '12px',
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px'
                  }}>
                    <h4 style={{
                      margin: '0 0 10px 0',
                      fontSize: '0.85rem',
                      color: '#ff3f6c',
                      textTransform: 'uppercase',
                      letterSpacing: '1px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}>
                      ✨ Complete The Look (Stylist Choice)
                    </h4>
                    <p style={{ fontSize: '0.7rem', color: '#94a3b8', margin: '0 0 12px 0' }}>
                      Recommended cross-category matches for {activeDateProfile.event}
                    </p>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      {lookCompleter.accessory && (
                        <div style={{
                          background: 'var(--bg-app)',
                          border: '1px solid rgba(255,255,255,0.05)',
                          borderRadius: '6px',
                          padding: '8px',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          textAlign: 'center'
                        }}>
                          <span style={{ fontSize: '0.65rem', color: '#a855f7', fontWeight: 'bold', marginBottom: '6px' }}>ACCESSORY</span>
                          <img 
                            src={lookCompleter.accessory.image_url} 
                            alt={lookCompleter.accessory.name}
                            style={{ width: '50px', height: '60px', objectFit: 'cover', borderRadius: '4px', marginBottom: '6px' }}
                            onError={(e) => {
                              e.target.src = `https://placehold.co/100x120/1a1a2e/a855f7?text=Accessory`;
                            }}
                          />
                          <span style={{ fontSize: '0.7rem', color: 'white', fontWeight: '500', height: '24px', overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                            {lookCompleter.accessory.name}
                          </span>
                          {lookCompleter.accessory.product_url && (
                            <a 
                              href={lookCompleter.accessory.product_url} 
                              target="_blank" 
                              rel="noreferrer"
                              style={{
                                marginTop: '8px',
                                display: 'block',
                                padding: '3px 8px',
                                background: '#a855f7',
                                color: 'white',
                                textDecoration: 'none',
                                borderRadius: '4px',
                                fontSize: '0.65rem',
                                fontWeight: 'bold'
                              }}
                            >
                              🛍️ Add
                            </a>
                          )}
                        </div>
                      )}
                      
                      {lookCompleter.footwear && (
                        <div style={{
                          background: 'var(--bg-app)',
                          border: '1px solid rgba(255,255,255,0.05)',
                          borderRadius: '6px',
                          padding: '8px',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          textAlign: 'center'
                        }}>
                          <span style={{ fontSize: '0.65rem', color: '#10b981', fontWeight: 'bold', marginBottom: '6px' }}>FOOTWEAR</span>
                          <img 
                            src={lookCompleter.footwear.image_url} 
                            alt={lookCompleter.footwear.name}
                            style={{ width: '50px', height: '60px', objectFit: 'cover', borderRadius: '4px', marginBottom: '6px' }}
                            onError={(e) => {
                              e.target.src = `https://placehold.co/100x120/1a1a2e/10b981?text=Footwear`;
                            }}
                          />
                          <span style={{ fontSize: '0.7rem', color: 'white', fontWeight: '500', height: '24px', overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                            {lookCompleter.footwear.name}
                          </span>
                          {lookCompleter.footwear.product_url && (
                            <a 
                              href={lookCompleter.footwear.product_url} 
                              target="_blank" 
                              rel="noreferrer"
                              style={{
                                marginTop: '8px',
                                display: 'block',
                                padding: '3px 8px',
                                background: '#10b981',
                                color: 'white',
                                textDecoration: 'none',
                                borderRadius: '4px',
                                fontSize: '0.65rem',
                                fontWeight: 'bold'
                              }}
                            >
                              🛍️ Add
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-decision-state">
                Click any product card in the feed to dissect its visual, tag-overlap, and climate/wedding surge composite ranking score.
              </div>
            )}
          </div>
        </div>

      </div>

      {/* ===== TRENDS INTELLIGENCE PANEL (Inline Tabs) ===== */}
      <div className="trends-panel">
        {/* Tab Headers */}
        <div className="trends-tab-header">
          <div className="trends-tab-title">📡 Trends Intelligence Layer</div>
          <div className="trends-tabs">
            <button
              id="tab-youtube"
              className={`trends-tab-btn ${activeTab === 'youtube' ? 'active' : ''}`}
              onClick={() => handleTabClick('youtube')}
            >
              🎬 Creator Feed
              {Array.isArray(youtubeData) && <span className="tab-count">{youtubeData.length}</span>}
            </button>
            <button
              id="tab-boutiques"
              className={`trends-tab-btn ${activeTab === 'boutiques' ? 'active' : ''}`}
              onClick={() => handleTabClick('boutiques')}
            >
              🏪 Local Stores
              {boutiqueData && <span className="tab-count">{boutiqueData.boutiques?.length}</span>}
            </button>
          </div>
          <div style={{ fontSize: '0.7rem', color: '#6b7280' }}>
            {ZIP_CODES[currentZipCode].city} · Click a tab to load
          </div>
        </div>

        {activeTab === 'youtube' && (
          <div className="trends-tab-content">
            {isYoutubeLoading ? (
              <div className="trends-loading">
                <div className="spinner" style={{ width: '28px', height: '28px', margin: '0 auto 10px' }}></div>
                <p style={{ color: '#ec4899', fontSize: '0.8rem', margin: 0 }}>Loading creator videos from database...</p>
              </div>
            ) : Array.isArray(youtubeData) && youtubeData.length > 0 ? (
              <div className="creator-feed-grid">
                {youtubeData.map((item, idx) => (
                  <div key={idx} className="creator-card">
                    {/* Thumbnail + Video Info */}
                    <div className="creator-thumb-wrap">
                      <img
                        src={item.youtube_video.thumbnail_url}
                        alt="thumb"
                        className="creator-thumb"
                        onError={(e) => { e.target.src = `https://placehold.co/160x90/1a1a2e/ec4899?text=Video+${idx+1}`; }}
                      />
                      <div className="creator-rank-badge">#{idx + 1}</div>
                      {item.youtube_video.video_url && (
                        <a href={item.youtube_video.video_url} target="_blank" rel="noreferrer" className="creator-play-btn">▶</a>
                      )}
                    </div>
                    <div className="creator-info">
                      <p className="creator-video-title">{item.youtube_video.title}</p>
                      <p className="creator-channel">📺 {item.youtube_video.channel}</p>
                      <p className="creator-llm-desc">"{item.youtube_video.llm_extracted_description}"</p>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                        {item.youtube_video.inferred_tags?.slice(0, 4).map(tag => (
                          <span key={tag} className="creator-tag">{tag}</span>
                        ))}
                      </div>
                    </div>
                    {/* Matched Product */}
                    {item.matched_product && (
                      <div className="creator-match">
                        <div className="creator-match-label">🎯 Catalog Match</div>
                        <img
                          src={item.matched_product.image_url}
                          alt={item.matched_product.name}
                          className="creator-match-img"
                          onError={(e) => { e.target.src = 'https://placehold.co/70x90/1a1a2e/22c55e?text=Match'; }}
                        />
                        <p className="creator-match-name">{item.matched_product.name}</p>
                        <div className="creator-match-score">
                          {item.matched_product.overlap_tags?.slice(0, 2).map(t => (
                            <span key={t} className="match-pill" style={{ fontSize: '0.6rem', padding: '1px 5px' }}>#{t}</span>
                          ))}
                        </div>
                        {item.matched_product.product_url && (
                          <a href={item.matched_product.product_url} target="_blank" rel="noreferrer" className="creator-buy-btn">Shop ↗</a>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : youtubeData === null ? (
              <div className="trends-empty">
                <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🎬</div>
                <p style={{ fontWeight: '600', color: 'white', marginBottom: '4px' }}>Creator Feed not loaded</p>
                <p style={{ fontSize: '0.75rem' }}>Click the <strong>🎬 Creator Feed</strong> tab above to load regional fashion creator videos</p>
              </div>
            ) : (
              <div className="trends-empty">No creator videos found for this region.</div>
            )}
          </div>
        )}

        {/* ---- BOUTIQUES TAB ---- */}
        {activeTab === 'boutiques' && (
          <div className="trends-tab-content">
            {isBoutiqueLoading ? (
              <div className="trends-loading">
                <div className="spinner" style={{ width: '28px', height: '28px', margin: '0 auto 10px' }}></div>
                <p style={{ color: '#a855f7', fontSize: '0.8rem', margin: 0 }}>Loading local boutique stores from database...</p>
              </div>
            ) : boutiqueData?.boutiques?.length > 0 ? (
              <div className="boutique-feed-grid">
                {boutiqueData.boutiques.map((store, idx) => (
                  <div key={store.store_id} className="boutique-card">
                    <div className="boutique-card-top">
                      <div className="boutique-rank">#{idx + 1}</div>
                      <div className="boutique-store-info">
                        <p className="boutique-store-name">{store.store_name}</p>
                        <p className="boutique-locality">📍 {store.locality}</p>
                      </div>
                      <div className="boutique-rating">⭐ {store.rating}</div>
                    </div>

                    <div className="boutique-trend-row">
                      <span className="boutique-trend-badge">#{store.extracted_visual_trend}</span>
                      <span className="boutique-vibe-cluster">{store.style_vibe_cluster}</span>
                    </div>

                    <div className="boutique-meta-row">
                      <span className="boutique-source">{store.social_signal_source}</span>
                      <span className="boutique-engagement">🔥 {(store.simulated_engagement / 1000).toFixed(1)}K</span>
                    </div>

                    {/* Matched Product Preview */}
                    {store.matched_product && (
                      <div className="boutique-matched-product">
                        <img
                          src={store.matched_product.image_url}
                          alt={store.matched_product.name}
                          className="boutique-match-img"
                          onError={(e) => { e.target.src = 'https://placehold.co/60x75/1a1a2e/a855f7?text=Item'; }}
                        />
                        <div className="boutique-match-details">
                          <span style={{ fontSize: '0.6rem', color: '#a855f7', fontWeight: 'bold' }}>TRENDING IN STORE</span>
                          <p className="boutique-match-name">{store.matched_product.name}</p>
                          {store.matched_product.product_url && (
                            <a href={store.matched_product.product_url} target="_blank" rel="noreferrer" className="creator-buy-btn" style={{ background: '#a855f7' }}>Shop ↗</a>
                          )}
                        </div>
                      </div>
                    )}

                    <a
                      href={store.maps_url}
                      target="_blank"
                      rel="noreferrer"
                      className="boutique-maps-btn"
                    >
                      🗺️ Open in Maps
                    </a>
                  </div>
                ))}
              </div>
            ) : boutiqueData === null ? (
              <div className="trends-empty">
                <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🏪</div>
                <p style={{ fontWeight: '600', color: 'white', marginBottom: '4px' }}>Local Stores not loaded</p>
                <p style={{ fontSize: '0.75rem' }}>Click the <strong>🏪 Local Stores</strong> tab above to load boutiques near {ZIP_CODES[currentZipCode].city}</p>
              </div>
            ) : (
              <div className="trends-empty">No local stores found for this region.</div>
            )}
          </div>
        )}
      </div>

      {/* Old YouTube modal — removed */}
      {false && (
        <div className="onboarding-overlay" onClick={() => { if (!isYoutubeLoading) setShowYoutubeModal(false); }}>
          <div 
            className="onboarding-modal" 
            onClick={(e) => e.stopPropagation()}
            style={{ maxWidth: '720px', maxHeight: '85vh', overflowY: 'auto' }}
          >
            <h2 style={{ textAlign: 'center', marginBottom: '8px' }}>
              🎬 Real-Time YouTube Trend Pipeline
            </h2>
            <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '20px' }}>
              Scraping → Vision LLM Analysis → Vector Similarity Match
            </p>

            {isYoutubeLoading && (
              <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                <div className="spinner" style={{ margin: '0 auto 20px auto' }}></div>
                <p style={{ color: '#ec4899', fontWeight: 'bold', fontSize: '1rem', marginBottom: '8px' }}>
                  🔍 Scraping YouTube Data API for {ZIP_CODES[currentZipCode].city} fashion hauls...
                </p>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  Running Vision LLM (Gemini 2.5 Pro) on video thumbnail...
                </p>
              </div>
            )}

            {Array.isArray(youtubeData) && !isYoutubeLoading && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', paddingBottom: '20px' }}>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 0 10px 0', textAlign: 'center' }}>
                  Found {youtubeData.length} matching creator styling hauls for this zone:
                </p>
                
                {youtubeData.map((item, idx) => (
                  <div key={idx} style={{ 
                    background: 'var(--bg-app)', 
                    border: '1px solid rgba(255,255,255,0.06)', 
                    borderRadius: '12px', 
                    padding: '16px',
                    display: 'grid',
                    gridTemplateColumns: '1.2fr 1fr',
                    gap: '16px'
                  }}>
                    {/* Left: YouTube Video Info */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                        <img 
                          src={item.youtube_video.thumbnail_url} 
                          alt="YouTube Thumbnail"
                          style={{ width: '100px', height: '60px', objectFit: 'cover', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}
                          onError={(e) => {
                            e.target.src = `https://placehold.co/120x90/1a1a2e/ec4899?text=Video+${idx+1}`;
                          }}
                        />
                        <div>
                          <p style={{ color: 'white', fontWeight: 'bold', fontSize: '0.75rem', margin: '0 0 2px 0', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                            {item.youtube_video.title}
                          </p>
                          <p style={{ color: 'var(--text-muted)', fontSize: '0.7rem', margin: '0' }}>
                            📺 {item.youtube_video.channel}
                          </p>
                        </div>
                      </div>
                      <p style={{ color: '#cbd5e1', fontSize: '0.7rem', margin: '4px 0', fontStyle: 'italic', lineHeight: '1.3' }}>
                        "{item.youtube_video.llm_extracted_description}"
                      </p>
                      
                      {item.youtube_video.video_url && (
                        <a 
                          href={item.youtube_video.video_url} 
                          target="_blank" 
                          rel="noreferrer"
                          style={{
                            alignSelf: 'flex-start',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            background: 'rgba(255, 63, 108, 0.1)',
                            border: '1px solid rgba(255, 63, 108, 0.2)',
                            padding: '3px 8px',
                            color: '#ff3f6c',
                            textDecoration: 'none',
                            borderRadius: '12px',
                            fontSize: '0.65rem',
                            fontWeight: 'bold',
                            marginTop: '2px'
                          }}
                        >
                          🎥 Watch Styling Video ↗
                        </a>
                      )}
                    </div>

                    {/* Right: Matched Catalog Product */}
                    {item.matched_product ? (
                      <div style={{ 
                        borderLeft: '1px solid rgba(255,255,255,0.06)', 
                        paddingLeft: '16px',
                        display: 'flex',
                        gap: '10px',
                        alignItems: 'center'
                      }}>
                        <img 
                          src={item.matched_product.image_url} 
                          alt={item.matched_product.name}
                          style={{ width: '50px', height: '65px', objectFit: 'cover', borderRadius: '4px', border: '1px solid rgba(34, 197, 94, 0.2)' }}
                          onError={(e) => {
                            e.target.src = `https://placehold.co/100x130/1a1a2e/22c55e?text=Match`;
                          }}
                        />
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                          <span style={{ fontSize: '0.6rem', color: '#22c55e', fontWeight: 'bold' }}>
                            🎯 Match: {item.matched_product.match_score ? (item.matched_product.match_score * 10).toFixed(0) : "100"}%
                          </span>
                          <span style={{ color: 'white', fontWeight: '500', fontSize: '0.75rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                            {item.matched_product.name}
                          </span>
                          {item.matched_product.product_url && (
                            <a 
                              href={item.matched_product.product_url} 
                              target="_blank" 
                              rel="noreferrer"
                              style={{
                                alignSelf: 'flex-start',
                                display: 'inline-block',
                                padding: '2px 6px',
                                background: '#ff3f6c',
                                color: 'white',
                                textDecoration: 'none',
                                borderRadius: '4px',
                                fontSize: '0.6rem',
                                fontWeight: 'bold',
                                marginTop: '2px'
                              }}
                            >
                              View on Myntra
                            </a>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                        No catalog match found
                      </div>
                    )}
                  </div>
                ))}

                <button 
                  onClick={() => setShowYoutubeModal(false)}
                  style={{ 
                    width: '100%', 
                    marginTop: '16px', 
                    padding: '10px', 
                    background: 'rgba(255,255,255,0.1)', 
                    border: '1px solid rgba(255,255,255,0.2)', 
                    borderRadius: '8px', 
                    color: 'white', 
                    cursor: 'pointer', 
                    fontSize: '0.9rem' 
                  }}
                >
                  Close Pipeline View
                </button>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
