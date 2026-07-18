"""
PinPulse API Server — Flask backend for the recommendation engine.
Dual-frontend architecture: User UI + Dev Panel.
"""

import sys
import os

# Add data directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))

from flask import Flask, jsonify, request
from flask_cors import CORS

from pinpulse_engine import PinPulseEngine
from config import CONTEXT_MATRICES
from mock_catalog import PRODUCT_CATALOG
from mock_zip_data import (
    ZIP_DATA,
    FESTIVAL_RULES,
    WEATHER_RULES,
    CREATORS,
    STORES,
    CF_LOOKUP,
)

app = Flask(__name__)
CORS(app)

# Initialize the PinPulse Engine
engine = PinPulseEngine(
    product_catalog=PRODUCT_CATALOG,
    zip_data=ZIP_DATA,
    festival_rules=FESTIVAL_RULES,
    weather_rules=WEATHER_RULES,
    creators=CREATORS,
    stores=STORES,
    cf_lookup=CF_LOOKUP,
)

# In-memory session state (for hackathon demo)
user_session = {
    "zip_code": "800008",
    "aesthetic": "ethnic",
    "aesthetic_vector": PRODUCT_CATALOG[0]["aesthetic_vector"],  # Use first product as proxy
    "age_group": "gen-z",
    "state": "discovery",
    "session_cart": [],
    "interactions": [],
    "time_offset_hours": 0,
}


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "engine": "PinPulse v1.0"})


@app.route("/api/feed", methods=["GET"])
def get_feed():
    """Main recommendation feed — scored and ranked products."""
    scored = engine.score_all_products(user_session)
    
    # Clean up vectors from response (they're large)
    clean_results = []
    for item in scored[:20]:  # Return top 20
        clean_item = {k: v for k, v in item.items() 
                      if not k.endswith("_vector")}
        clean_results.append(clean_item)
    
    return jsonify({
        "products": clean_results,
        "state": user_session["state"],
        "zip_code": user_session["zip_code"],
        "total_scored": len(scored),
    })


@app.route("/api/product/<product_id>", methods=["GET"])
def get_product(product_id):
    """Product Detail Page — includes 'People Also Bought' recommendations."""
    product = next((p for p in PRODUCT_CATALOG if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # Get co-purchase recommendations
    pdp_recs = engine.get_pdp_recommendations(product_id)
    
    # Clean vectors
    clean_product = {k: v for k, v in product.items() if not k.endswith("_vector")}
    clean_recs = [
        {k: v for k, v in r.items() if not k.endswith("_vector")}
        for r in pdp_recs
    ]
    
    return jsonify({
        "product": clean_product,
        "also_bought": clean_recs,
    })


@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    """Add item to cart — triggers session rerank."""
    data = request.json
    item_id = data.get("item_id")
    
    if item_id and item_id not in user_session["session_cart"]:
        user_session["session_cart"].append(item_id)
        
        # Record interaction
        user_session["interactions"].append({
            "item_id": item_id,
            "action_type": "cart",
            "hours_elapsed": 0,
        })
        
        # Switch to high-intent state
        user_session["state"] = "high_intent"
    
    return jsonify({
        "cart": user_session["session_cart"],
        "state": user_session["state"],
    })


@app.route("/api/cart/remove", methods=["POST"])
def remove_from_cart():
    """Remove item from cart."""
    data = request.json
    item_id = data.get("item_id")
    
    if item_id in user_session["session_cart"]:
        user_session["session_cart"].remove(item_id)
    
    # If cart is empty, revert to discovery state
    if not user_session["session_cart"]:
        user_session["state"] = "discovery"
    
    return jsonify({
        "cart": user_session["session_cart"],
        "state": user_session["state"],
    })


@app.route("/api/wishlist/add", methods=["POST"])
def add_to_wishlist():
    """Add item to wishlist — triggers intent boost."""
    data = request.json
    item_id = data.get("item_id")
    
    if item_id:
        user_session["interactions"].append({
            "item_id": item_id,
            "action_type": "wishlist",
            "hours_elapsed": 0,
        })
    
    return jsonify({"status": "wishlisted", "item_id": item_id})


# =============================================================================
# DEV PANEL ENDPOINTS (Judge-facing controls)
# =============================================================================


@app.route("/api/dev/state", methods=["GET"])
def get_dev_state():
    """Get full engine state for Dev Panel."""
    return jsonify({
        "session": user_session,
        "available_states": list(CONTEXT_MATRICES.keys()),
        "available_zips": list(ZIP_DATA.keys()),
        "current_weights": CONTEXT_MATRICES.get(user_session["state"], {}),
    })


@app.route("/api/dev/set-state", methods=["POST"])
def set_state():
    """Manually switch the state machine context."""
    data = request.json
    new_state = data.get("state", "discovery")
    
    if new_state in CONTEXT_MATRICES:
        user_session["state"] = new_state
    
    return jsonify({"state": user_session["state"]})


@app.route("/api/dev/set-zip", methods=["POST"])
def set_zip():
    """Switch the user's ZIP code (simulates location change)."""
    data = request.json
    new_zip = data.get("zip_code", "800008")
    
    if new_zip in ZIP_DATA:
        user_session["zip_code"] = new_zip
        # Clear cache to force recalculation
        engine._cache = {}
    
    return jsonify({
        "zip_code": new_zip,
        "city": ZIP_DATA.get(new_zip, {}).get("city", "Unknown"),
        "festival": ZIP_DATA.get(new_zip, {}).get("active_festival", None),
    })


@app.route("/api/dev/time-warp", methods=["POST"])
def time_warp():
    """
    Time Warp: Add hours to session time to demonstrate decay.
    This is the 'fast forward' button for the hackathon demo.
    """
    data = request.json
    hours_to_add = data.get("hours", 24)
    
    user_session["time_offset_hours"] += hours_to_add
    
    # Also add hours to all existing interactions
    for interaction in user_session["interactions"]:
        interaction["hours_elapsed"] += hours_to_add
    
    return jsonify({
        "time_offset_hours": user_session["time_offset_hours"],
        "message": f"Fast-forwarded {hours_to_add}h. Total offset: {user_session['time_offset_hours']}h",
    })


@app.route("/api/dev/velocity-surge", methods=["POST"])
def velocity_surge():
    """
    Simulate a local velocity surge — the 'What's New in Your Locality' trigger.
    Returns hardcoded theme + matched items (faked LLM for instant demo).
    """
    result = engine.simulate_velocity_surge(user_session["zip_code"])
    
    # Clean vectors from response
    clean_products = [
        {k: v for k, v in p.items() if not k.endswith("_vector")}
        for p in result["products"]
    ]
    
    return jsonify({
        "theme": result["theme"],
        "products": clean_products,
        "log": result["log"],
    })


@app.route("/api/dev/reset", methods=["POST"])
def reset_session():
    """Reset the entire session to fresh state."""
    user_session.update({
        "zip_code": "800008",
        "aesthetic": "ethnic",
        "age_group": "gen-z",
        "state": "discovery",
        "session_cart": [],
        "interactions": [],
        "time_offset_hours": 0,
    })
    engine._cache = {}
    
    return jsonify({"status": "reset", "session": user_session})


@app.route("/api/dev/set-festival", methods=["POST"])
def set_festival():
    """Toggle festival mode for current ZIP."""
    data = request.json
    festival = data.get("festival", None)
    zip_code = user_session["zip_code"]
    
    if zip_code in ZIP_DATA:
        ZIP_DATA[zip_code]["active_festival"] = festival
        
        # Switch to festive state if festival is active
        if festival:
            user_session["state"] = "festive_season"
        else:
            user_session["state"] = "discovery"
        
        engine._cache = {}
    
    return jsonify({
        "zip_code": zip_code,
        "festival": festival,
        "state": user_session["state"],
    })


if __name__ == "__main__":
    print("🚀 PinPulse Engine starting...")
    print(f"📊 Loaded {len(PRODUCT_CATALOG)} products")
    print(f"🗺️  Loaded {len(ZIP_DATA)} ZIP codes")
    print(f"🎯 Available states: {list(CONTEXT_MATRICES.keys())}")
    app.run(debug=True, port=5000)
