import pathlib

# --- USER SETTINGS --------------------------------------------------
# One Sales Navigator search URL per line in urls.txt; lines starting with # are skipped.
_URLS_FILE = pathlib.Path(__file__).resolve().parents[1] / "urls.txt"
START_URLS = [
    line.strip()
    for line in _URLS_FILE.read_text().splitlines()
    if line.strip() and not line.lstrip().startswith("#")
] if _URLS_FILE.exists() else []

# Card-level selectors
NAME_SELECTOR = "[data-anonymize='person-name']"

# Pagination control (outside the scroll area)
NEXT_BTN_SELECTOR = "[aria-label='Next']"

# Safety / performance knobs
SCROLL_PAUSE_MS = 15_000
STALL_LIMIT      = 4
MAX_SCROLLS      = 300
