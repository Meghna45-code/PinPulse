---
name: pinpulse_seeder
description: Automated seeder for regional fashion creators and local boutique trends from YouTube transcripts.
---

# Instruction for PinPulse Seeding Skill

You have triggered the automated seeding pipeline for regional fashion creators and local boutiques. When the user (or their team member) provides fashion transcripts, excel files, or requests to rebuild the mockup database, follow these steps:

## 1. Locate the Input Excel File
Look in the workspace root for `pinpulse_youtube_seed.xlsx` or any Excel file uploaded by the user/friend.

## 2. Run the Seeder Script
Execute the seeder script in the background using the environment's python:
```powershell
python backend/run_transcript_seeder.py [optional_path_to_excel]
```

## 3. Verify Output
Make sure that the file `backend/pinpulse_mock_db.json` has been created or updated.

## 4. Rerank Recommendations
Instruct the user that the backend now holds these vectors, which will be automatically queried by the recommendation engine on geographic boundary shifts.
