"""Dump creators.xlsx and stores.xlsx to text files for inspection."""
import pandas as pd
import os

root = os.path.join(os.path.dirname(__file__), "..", "..", "excel_sheets")
out_dir = os.path.dirname(__file__)

df = pd.read_excel(os.path.join(root, "creators.xlsx"))
with open(os.path.join(out_dir, "_creators_dump.txt"), "w", encoding="utf-8") as f:
    f.write("Columns: " + str(df.columns.tolist()) + "\n")
    f.write("Shape: " + str(df.shape) + "\n\n")
    for i, row in df.iterrows():
        f.write(f"ROW {i}:\n")
        for col in df.columns:
            f.write(f"  {col}: {row[col]}\n")
        f.write("\n")

df2 = pd.read_excel(os.path.join(root, "stores.xlsx"))
with open(os.path.join(out_dir, "_stores_dump.txt"), "w", encoding="utf-8") as f:
    f.write("Columns: " + str(df2.columns.tolist()) + "\n")
    f.write("Shape: " + str(df2.shape) + "\n\n")
    for i, row in df2.iterrows():
        f.write(f"ROW {i}:\n")
        for col in df2.columns:
            f.write(f"  {col}: {row[col]}\n")
        f.write("\n")

print("Done. Check _creators_dump.txt and _stores_dump.txt")
