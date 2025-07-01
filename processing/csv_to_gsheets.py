import csv
import gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
CSV_PATH = "scrape_output.csv"  # or whatever your filename is
SHEET_NAME = "Connections to Track"
SERVICE_ACCOUNT_FILE = "service_account.json"

# === AUTH ===
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]
)
gc = gspread.authorize(creds)

# === LOAD AND CLEAN CSV ===
rows = []
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) != 3:
            continue  # skip malformed rows
        url, person_name, date = row
        # Extract "Nimi Katragadda" from the URL (search name)
        if "text%3ANimi%2520Katragadda" in url:
            search_name = "Nimi Katragadda"
        else:
            search_name = "UNKNOWN"
        rows.append([search_name, person_name.strip(), date.strip()])

# === PUSH TO SHEET ===
try:
    sh = gc.open(SHEET_NAME)
except gspread.SpreadsheetNotFound:
    sh = gc.create(SHEET_NAME)

worksheet = sh.sheet1
worksheet.clear()
worksheet.update([["Search Name", "Person Name", "Date"]] + rows)
print(f"✓ Pushed {len(rows)} rows to '{SHEET_NAME}'")
