import sys
import os

try:
    from pinscrape import Pinterest
    print("Successfully imported Pinterest from pinscrape!")
    
    # Initialize the Pinterest scraper
    p = Pinterest(sleep_time=1)
    
    keyword = "minimalist cotton dress"
    images_to_download = 5
    
    print(f"Searching for '{keyword}'...")
    # search method signature: search(keyword, limit)
    res = p.search(keyword, images_to_download)
    print("Search result type:", type(res))
    
    if isinstance(res, dict):
        print("Keys in result:", res.keys())
        # Let's inspect the returned data structure
        # pinscrape usually returns a dict like {'isDownloaded': False, 'url_list': [...]}
        # or similar
        print("Sample data:", str(res)[:500])
    else:
        print("Result:", res)
        
except Exception as e:
    print("Error during test:", e)
