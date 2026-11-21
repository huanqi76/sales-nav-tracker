###############################################################################
# Google-Sheet helpers   (replace the old helper chunk with this one)
###############################################################################
import gspread, asyncio, concurrent.futures, functools, datetime
from gspread_formatting import format_cell_range, CellFormat, Color
import urllib.parse

import re
HANDLE_RE = re.compile(r"/in/([^/]+)/")

SA_JSON     = "auth/gcp_service_account.json"
SHEET_NAME  = "Connections to Track"
# LINKS_TAB   = "links"
DATA_TAB    = "data"
DELTA_TAB   = "new_this_run"
TODAY       = datetime.date.today().isoformat()          # '2025-06-03'


def extract_search_name(url: str) -> str:
    """
    Extracts the 'text' value from the CONNECTION_OF filter in the LinkedIn Sales Navigator URL.
    """
    decoded = urllib.parse.unquote(url)
    match = re.search(r"type:CONNECTION_OF.*?text:(.*?)\b", decoded)
    if match:
        return match.group(1).replace("%20", " ").strip()
    return "UNKNOWN"


def clean_rows(raw_rows):
    """
    raw_rows → list like [[url, interest_or_followers, date], …]
    returns   → list [[handle, interest_name, date], …]  (followers rows dropped)
    """
    cleaned = []
    for url, col2, date in raw_rows:
        if "followers" in col2.lower():
            continue                          # skip the follower-count line
        m = HANDLE_RE.search(url)
        handle = m.group(1) if m else url     # fallback to full URL
        cleaned.append([handle, col2.strip(), date])
    return cleaned

def _open_wb():
    return gspread.service_account(filename=SA_JSON).open(SHEET_NAME)

# ── read profile URLs ---------------------------------------------------------
# def get_urls_from_sheet():
#     ws  = _open_wb().worksheet(LINKS_TAB)
#     col = [c.strip() for c in ws.col_values(1) if c.strip()]
#     return col[1:] if col and not col[0].startswith("http") else col

# ── write + dedup -------------------------------------------------------------
def _append_rows_dedup(rows, *, clear_delta: bool = False):
    """
    • Appends *new* rows to DATA_TAB (with highlighting).
    • Writes the very same rows to DELTA_TAB.
      ▸ If clear_delta=False (default) → they’re appended.
      ▸ If clear_delta=True  → the tab is wiped first, like before.
    """
    wb        = _open_wb()
    try:
        ws_da = wb.worksheet(DATA_TAB)
    except gspread.exceptions.WorksheetNotFound:
        ws_da = wb.add_worksheet(title=DATA_TAB, rows=1, cols=4)

    # build a set of existing (url, interest) pairs
    existing = set(zip(ws_da.col_values(1), ws_da.col_values(2)))
    new_rows = [r for r in rows if (r[0], r[1]) not in existing]
    if not new_rows:
        print("No NEW interests this run.")
        return

    # 1 append into DATA_TAB
    ws_da.append_rows(new_rows, value_input_option="RAW")

    # 2 append (or reset) DELTA_TAB
    try:
        ws_de = wb.worksheet(DELTA_TAB)
    except gspread.exceptions.WorksheetNotFound:
        ws_de = wb.add_worksheet(title=DELTA_TAB, rows=1, cols=4)

    if clear_delta:
        ws_de.clear()
        ws_de.update("A1", new_rows)
    else:
        ws_de.append_rows(new_rows, value_input_option="RAW")

    # 3 highlight the freshly–added block in DATA_TAB
    first = ws_da.row_count - len(new_rows) + 1
    last  = ws_da.row_count
    fmt   = CellFormat(backgroundColor=Color(0.87, 0.97, 0.87))  # light green
    format_cell_range(ws_da, f"A{first}:C{last}", fmt)
    print(f"✓ appended {len(new_rows)} rows → "
          f"'{DATA_TAB}' (+highlight) and '{DELTA_TAB}'")

async def push_to_gsheet(rows, *, clear_delta: bool = False):
    loop = asyncio.get_running_loop()
    fn   = functools.partial(_append_rows_dedup, rows, clear_delta=clear_delta)
    await loop.run_in_executor(None, fn)