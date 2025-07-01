import asyncio, sys, textwrap
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

from scraping.config     import START_URLS, NAME_SELECTOR
from scraping.scroll     import load_everything
from scraping.pagination import click_next_if_present
from scraping.extractor  import extract_rows
from processing.export     import write_csv, send_to_gsheet

async def process_url(context, url, all_rows, seen):
    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded", timeout=70_000)
    await page.wait_for_selector(NAME_SELECTOR, timeout=10_000)

    # quick sanity-check
    if await page.locator(NAME_SELECTOR).count() == 0:
        msg = textwrap.dedent(
            f"""
            🛑 NAME_SELECTOR matches 0 elements on the first screen.
            Re-inspect the page and update NAME_SELECTOR.
            """
        )
        sys.exit(msg)

    page_no = 1
    while True:
        print(f"📄 Page {page_no}")

        await load_everything(page)                          # infinite scroll
        batch = await extract_rows(page, url, seen)          # pull rows
        all_rows.extend(batch)
        print(f"  ↳ grabbed {len(batch)} rows "
              f"(cumulative {len(all_rows)})")

        if not await click_next_if_present(page):            # pagination
            break
        page_no += 1

    await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=250)
        context = await browser.new_context(storage_state="auth/state.json")

        all_rows, seen = [], set()
        for url in START_URLS:
            await process_url(context, url, all_rows, seen)

        await write_csv(all_rows)
        await send_to_gsheet(all_rows)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except PWTimeout:
        sys.exit("Playwright timed out — try raising SCROLL_PAUSE_MS.")
