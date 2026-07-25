"""
Average Order Value (AOV) Constraint Demonstration Module
=========================================================
ISOLATED MODULE — For presentation / demonstration purposes only.
This module demonstrates how AOV price-ratio penalty multipliers
decay recommendations when product prices deviate significantly from
a region's target Average Order Value.

Formula:
  AOV_Penalty = exp(-|Price_item - Target_AOV| / Target_AOV)
  S_penalized = S_raw * AOV_Penalty

Note: Per project specification, this module is kept separate in this folder
and IS NOT invoked in the live recommendation pipeline.
"""

import math

def calculate_aov_penalty(price: float, target_aov: float = 2500.0) -> float:
    """
    Calculates AOV price ratio penalty multiplier [0.0 to 1.0].
    
    Args:
        price: Price of the product in INR
        target_aov: Target regional Average Order Value (default 2500 INR)
        
    Returns:
        Penalty multiplier float between 0.0 and 1.0.
    """
    if target_aov <= 0 or price <= 0:
        return 1.0
        
    ratio_diff = abs(price - target_aov) / target_aov
    penalty = math.exp(-ratio_diff)
    return round(penalty, 4)

def apply_aov_constraint_demo(raw_score: float, price: float, target_aov: float = 2500.0) -> dict:
    """
    Demonstration function showing before & after score with AOV penalty.
    """
    penalty = calculate_aov_penalty(price, target_aov)
    penalized_score = round(raw_score * penalty, 4)
    
    return {
        "price": price,
        "target_aov": target_aov,
        "raw_score": raw_score,
        "aov_penalty_multiplier": penalty,
        "penalized_score": penalized_score,
        "score_drop_pct": round((1.0 - penalty) * 100, 2)
    }

if __name__ == "__main__":
    print("=== AOV Constraint Demonstration Module ===")
    test_prices = [1200.0, 2500.0, 5000.0, 12000.0]
    raw = 0.92
    for p in test_prices:
        res = apply_aov_constraint_demo(raw, p)
        print(f"Price: Rs {p:7.1f} | Raw Score: {raw:.2f} | Multiplier: {res['aov_penalty_multiplier']:.4f} | Penalized Score: {res['penalized_score']:.4f} (-{res['score_drop_pct']}%)")
