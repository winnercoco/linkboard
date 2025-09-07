import pandas as pd
from pathlib import Path

# Base directory = project root (where this script lives, one level up from /scripts)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# File paths
excel_file = DATA_DIR / "links.xlsx"   # your Excel input
json_file = DATA_DIR / "links.json"    # JSON output

# Load Excel file
df = pd.read_excel(excel_file)

# Convert to JSON
df.to_json(json_file, orient="records", indent=2)

print(f"✅ Excel converted to JSON and saved as {json_file}")