import os
import pandas as pd

excel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Fashion Apparel2.xlsx"))

def read_excel2():
    if not os.path.exists(excel_path):
        print("Excel file not found at:", excel_path)
        return
        
    xl = pd.ExcelFile(excel_path)
    print("Sheets in Excel:", xl.sheet_names)
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
        print(f"\nSheet '{sheet}' has {len(df)} rows and {df.shape[1]} columns.")
        print("First 5 rows:")
        print(df.head(5))

if __name__ == "__main__":
    read_excel2()
