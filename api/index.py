import os
import sys

# Add backend directory and app package to Python path for Vercel serverless function
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
APP_DIR = os.path.join(BACKEND_DIR, "app")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app.main import app
