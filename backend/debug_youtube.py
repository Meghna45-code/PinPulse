import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app.youtube_scraper import get_youtube_trend_match

def debug():
    res = get_youtube_trend_match("800001")
    print("Result length:", len(res))
    if len(res) > 0:
        print("First item:", res[0])

if __name__ == "__main__":
    debug()
