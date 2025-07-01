import csv, pathlib
from processing.tools import push_to_gsheet, clean_rows   # existing helper module

async def write_csv(rows, basename="scrape_output"):
    out = pathlib.Path(__file__).with_name(f"{basename}.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print(f"✓ wrote {len(rows)} rows → {out}")

async def send_to_gsheet(rows):
    rows_for_sheet = clean_rows(rows)
    await push_to_gsheet(rows_for_sheet)
    print(f"⇢ {len(rows)} rows pushed to Google Sheets")
