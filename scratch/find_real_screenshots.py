import os
import glob
import pandas as pd

print("=== Checking Excel Files for Creator & Store Screenshots ===")

for xlsx in glob.glob("excel_sheets/*.xlsx") + glob.glob("*.xlsx"):
    print("\n--- File:", xlsx)
    try:
        df = pd.read_excel(xlsx)
        print("Columns:", df.columns.tolist())
        print("First 3 rows:")
        print(df.head(3))
    except Exception as e:
        print("Error reading excel:", e)

print("\n=== Checking root image files ===")
root_m_imgs = sorted(glob.glob("M*.jpg") + glob.glob("M*.webp") + glob.glob("M*.avif"))
print("M-images (Mock/Market/Creator images?):", root_m_imgs)

root_png_imgs = sorted(glob.glob("*.png"))
print("PNG images:", root_png_imgs)
