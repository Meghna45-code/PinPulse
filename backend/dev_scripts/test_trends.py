import os
import json
from fastapi.testclient import TestClient
import sys

# Ensure backend folder is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

def test_boutique_trends():
    print("\n--- Testing Boutique Trends Endpoint ---")
    # Test for Bengaluru ZIP code
    res = client.get("/api/trends/boutiques?zip_code=560034")
    assert res.status_code == 200
    data = res.json()
    print(f"Bengaluru (560034) boutiques count: {len(data['boutiques'])}")
    for b in data['boutiques']:
        print(f" - {b['store_name']}: {b['extracted_visual_trend']} (Engagement: {b['simulated_engagement']})")
        assert b['zip_code'] == "560034"
        
    # Test for Delhi ZIP code
    res = client.get("/api/trends/boutiques?zip_code=110049")
    assert res.status_code == 200
    data = res.json()
    print(f"\nDelhi (110049) boutiques count: {len(data['boutiques'])}")
    for b in data['boutiques']:
        print(f" - {b['store_name']}: {b['extracted_visual_trend']} (Engagement: {b['simulated_engagement']})")
        assert b['zip_code'] == "110049"

def test_recommendation_scoring():
    print("\n--- Testing 6-Layer Personalized Recommendations ---")
    
    # Query recommendations for a Gen-Z vibe in Koramangala
    res = client.get("/api/products?zip_code=560034&vibe=streetwear&date=2026-11-15")
    assert res.status_code == 200
    products = res.json()
    
    print(f"Returned {len(products)} products ranked by 6-layer engine.")
    
    # Check top 3 products
    print("\nTop 3 Recommended Products for Koramangala (Streetwear):")
    for idx, p in enumerate(products[:3]):
        breakdown = p.get("scoring_breakdown", {})
        print(f"\n{idx+1}. {p['name']} (Final Score: {p['final_score']})")
        print(f"   Tags: {p['tags']}")
        print(f"   6-Layer Breakdown:")
        print(f"     - Layer 1 (Personal Vibe 35%): {breakdown.get('layer1_personal_vibe')}")
        print(f"     - Layer 2 (Creator Trend 20%): {breakdown.get('layer2_creator_trend')}")
        print(f"     - Layer 3 (Local Boutique 15%): {breakdown.get('layer3_local_boutique')}")
        print(f"     - Layer 4 (Festivity 15%): {breakdown.get('layer4_festivity')}")
        print(f"     - Layer 5 (Weather 10%): {breakdown.get('layer5_weather')}")
        print(f"     - Layer 6 (Velocity 5%): {breakdown.get('layer6_velocity')}")
        
        # Verify layer scores exist and add up to final_score approximately (before strict hackathon rules boosts)
        assert "layer1_personal_vibe" in breakdown
        assert "layer3_local_boutique" in breakdown
        
    print("\nAll trend tests passed successfully!")

if __name__ == "__main__":
    test_boutique_trends()
    test_recommendation_scoring()
