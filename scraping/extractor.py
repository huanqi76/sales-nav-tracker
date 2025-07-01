from datetime import date
from scraping.config import NAME_SELECTOR
from processing.tools import extract_search_name

TODAY = date.today().isoformat()


async def extract_rows(page, source_url, seen):
    """
    Returns a list of [url, text, date] for the current page,
    skipping duplicates via `seen` (a set).
    """
    texts = await page.locator(NAME_SELECTOR).all_inner_texts()
    results = []
    search_name = extract_search_name(source_url)

    for raw in texts:
        txt = raw.strip().split("\n")[0]
        if txt not in seen:
            seen.add(txt)
            results.append([search_name, txt, TODAY])
    return results
