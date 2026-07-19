# PinPulse Hyperlocal Data Seeder Guide

This directory contains `backend/run_transcript_seeder.py`, an automated data pipeline script designed to fetch YouTube transcripts, extract structured fashion insights using Gemini, generate vector embeddings, and compile them into a unified mock database.

---

## 1. Input Excel Format

To run the seeder, please upload an Excel file named `pinpulse_youtube_seed.xlsx` in the workspace root containing the following columns:

| Column Name | Type | Description | Example |
|---|---|---|---|
| `video_id` | Text | The 11-character YouTube video ID | `dQw4w9WgXcQ` |
| `pincode` | Text | The target postal code (e.g. Patna, Kochi, Shillong) | `800008` |
| `type` | Text | Category: `creator` (fashion vlogs) or `boutique` (retail tours) | `creator` |
| `store_name` | Text | Optional store/market name (useful for boutiques) | `Khetan Market` |

---

## 2. Setup Dependencies

Make sure the following Python dependencies are installed in your environment:

```bash
pip install pandas openpyxl youtube-transcript-api google-generativeai python-dotenv
```

Also, ensure the `backend/.env` file contains your Gemini API key:
```env
GEMINI_API_KEY=AIzaSy...
```

---

## 3. How to Run the Seeder

Open your terminal in the workspace root and run:

```bash
python backend/run_transcript_seeder.py
```

*Note: If you have named your Excel file differently (e.g. `my_fashion_trends.xlsx`), you can pass it as an argument:*
```bash
python backend/run_transcript_seeder.py my_fashion_trends.xlsx
```

---

## 4. Pipeline Output

The seeder automatically generates a file named `backend/pinpulse_mock_db.json`. 

During the live demo, the recommendation engine consumes this JSON cache:
- When changing region to Patna (`800008`), the engine reads Patna-tagged vectors.
- It performs cosine similarity matching against the Myntra products to instantly rank and re-order the feed based on creator trends and boutique arrivals.
