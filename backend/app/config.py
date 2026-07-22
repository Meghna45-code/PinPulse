"""
PinPulse Configuration — State Machine Context Matrices & Constants
"""

# =============================================================================
# STATE MACHINE CONTEXT MATRICES (All weights sum to 1.0)
# Keys: w_aesthetic=Aesthetic, w_fabric=Fabric, w_festivity=Festivity,
#       w_boutique=Boutique, w_creator=Creator, w_cf=CF,
#       w_intent=Intent, w_velocity=Velocity
# =============================================================================

CONTEXT_MATRICES = {
    "discovery": {
        "w_aesthetic": 0.35,
        "w_fabric": 0.15,
        "w_festivity": 0.05,
        "w_boutique": 0.05,
        "w_creator": 0.05,
        "w_cf": 0.25,
        "w_intent": 0.05,
        "w_velocity": 0.05,
    },
    "high_intent": {
        "w_aesthetic": 0.15,
        "w_fabric": 0.10,
        "w_festivity": 0.0,
        "w_boutique": 0.0,
        "w_creator": 0.0,
        "w_cf": 0.15,
        "w_intent": 0.50,
        "w_velocity": 0.10,
    },
    "festive_season": {
        "w_aesthetic": 0.05,
        "w_fabric": 0.02,
        "w_festivity": 0.80,
        "w_boutique": 0.02,
        "w_creator": 0.02,
        "w_cf": 0.03,
        "w_intent": 0.03,
        "w_velocity": 0.03,
    },
    "hyper_local_boutique": {
        "w_aesthetic": 0.10,
        "w_fabric": 0.05,
        "w_festivity": 0.0,
        "w_boutique": 0.40,
        "w_creator": 0.0,
        "w_cf": 0.05,
        "w_intent": 0.10,
        "w_velocity": 0.30,
    },
    "social_commerce": {
        "w_aesthetic": 0.10,
        "w_fabric": 0.05,
        "w_festivity": 0.0,
        "w_boutique": 0.0,
        "w_creator": 0.40,
        "w_cf": 0.05,
        "w_intent": 0.10,
        "w_velocity": 0.30,
    },
}

# =============================================================================
# INTENT DECAY CONSTANTS
# =============================================================================

INTENT_DECAY_CONFIG = {
    "wishlist": {"initial": 0.3, "half_life_hours": 24.0},
    "cart": {"initial": 0.6, "half_life_hours": 24.0},
    "buy": {"initial": -1.0, "half_life_hours": 720.0},  # 30 days
}

# =============================================================================
# SCORING THRESHOLDS & CONSTANTS
# =============================================================================

WEATHER_VETO_THRESHOLD = 0.2        # Hard veto: if S_weather < 0.2, disqualify
CONFIDENCE_THRESHOLD = 0.6          # Hallucination gate for LLM tags
RELEVANCE_ALPHA = 0.6               # Trend noise gate
EVERGREEN_FIXED_SCORE = 0.85        # Bypass score for evergreen items
LOW_STOCK_THRESHOLD = 5             # Inventory penalty trigger
LOW_STOCK_PENALTY = 0.1             # Score multiplier for low stock
AOV_PRICE_MULTIPLIER = 2.0          # Price-affinity clamping threshold
LOW_REVIEW_THRESHOLD = 50           # Review count penalty gate
LOW_REVIEW_PENALTY = 0.5            # Multiplier for < 50 reviews

# Category Stratification
MIN_CATEGORIES_TOP_10 = 4           # Minimum distinct categories in top 10

# Exploration vs Exploitation
EXPLOITATION_RATIO = 0.9            # 90% top-scored items
EXPLORATION_RATIO = 0.1             # 10% discovery items

# Cache / State Hysteresis
CACHE_TTL_SECONDS = 60
