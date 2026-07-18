# PinPulse — Myntra for Bharat

**Hyper-Local Fashion Recommendation Engine for Tier 2/3 India**

Myntra WeForShe HackerRamp 2026 | Theme 1: The Bharat Opportunity

## Architecture

PinPulse is a **Continuous Scoring System** using Hybrid Search and Semantic/Vector Intelligence. Instead of rigid binary filters, it scores products across 8 dimensions using a State-Machine Routing Engine that dynamically adjusts weights based on user context.

### The PinPulse Formula

```
Final_Score = (w1·S_aesthetic + w2·S_fabric + w3·S_festivity + w4·S_boutique + w5·S_creator)
            + (w6·S_cf + w7·S_intent)
            + (w8·S_velocity)
```

### Key Features

1. **Tri-Layer Scoring** — Aesthetic, Climate-Fabric, and Festivity matching
2. **Trend Sensing** — Creator-based + Local Boutique demand signals
3. **Collaborative Filtering** — Co-purchase mapping with probabilistic strengths
4. **Intent Decay** — Time-based behavioral modifiers with exponential decay
5. **State Machine** — 5 context matrices (Discovery, High-Intent, Festive, Boutique, Social)
6. **Category Stratification** — Prevents feed collapse / "Wall of Yellow"
7. **Weather Hard Veto** — Disqualifies climate-inappropriate products
8. **Inventory Penalty** — Low-stock items scored 90% lower
9. **Exploration vs Exploitation** — 70/30 split for feed diversity
10. **Dual Frontend** — User UI + Judge Dev Panel

## Quick Start

### Backend (Python/Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5000`

### Frontend (React)

```bash
cd frontend
npm install
npm start
```

App runs on `http://localhost:3000`

## API Endpoints

### User-Facing
- `GET /api/feed` — Main recommendation feed (scored & ranked)
- `GET /api/product/:id` — Product detail + "People Also Bought"
- `POST /api/cart/add` — Add to cart (triggers session rerank)
- `POST /api/wishlist/add` — Wishlist (triggers intent boost)

### Dev Panel (Judge-Facing)
- `GET /api/dev/state` — Full engine state
- `POST /api/dev/set-state` — Switch state machine context
- `POST /api/dev/set-zip` — Change location
- `POST /api/dev/time-warp` — Fast-forward time (decay demo)
- `POST /api/dev/velocity-surge` — Simulate local trend surge
- `POST /api/dev/set-festival` — Toggle festival mode
- `POST /api/dev/reset` — Reset session

## Demo Flow (5-minute pitch)

1. Open app → Show personalized feed for Patna (800008)
2. Click a product → Show "People Also Bought" shelf
3. Add to cart → Show instant feed re-ranking (Session Rerank)
4. Dev Panel: Switch ZIP to Coimbatore → Feed adapts to local trends
5. Dev Panel: Activate Chhath Puja → Festival items surge
6. Dev Panel: Time Warp +24h → Intent decay demoed live
7. Dev Panel: Velocity Surge → New tab appears with toast notification

## Tech Stack

- **Backend:** Python, Flask, NumPy
- **Frontend:** React
- **Vector Math:** Local cosine similarity (no external vector DB needed for demo)
- **Data:** Pre-computed mock catalog with deterministic vectors

## Team

Built for Myntra WeForShe HackerRamp 2026
