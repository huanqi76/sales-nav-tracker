import asyncio
from playwright.async_api import TimeoutError as PWTimeout

from scraping.config import (
    NAME_SELECTOR,
    # SHOW_MORE_TEXT,
    SCROLL_PAUSE_MS,
    STALL_LIMIT,
    MAX_SCROLLS,
)

async def load_everything(page):
    """
    Scrolls the list container until `ITEM_SELECTOR` stops growing or
    `MAX_SCROLLS` iterations are reached.  Re-uses the logic you had before.
    """
    stalled, seen = 0, -1

    for _ in range(MAX_SCROLLS):
        # scroll one viewport on whichever element owns the scrollbar
        await page.evaluate("""
            () => {
                let scrollBox = document.querySelector('#search-results-container');
                if (!scrollBox) return;
                scrollBox.scrollBy({ top: scrollBox.clientHeight, behavior: 'instant' });
            }
        """)

        # wait for LinkedIn spinner (if any) to appear/disappear
        try:
            await page.locator("div.artdeco-loader").wait_for(
                state="attached", timeout=7_000
            )
            await page.locator("div.artdeco-loader").wait_for(
                state="detached", timeout=7_000
            )
        except PWTimeout:
            pass  # spinner never appeared or took too long

        await page.wait_for_timeout(500)  # debounce

        new_seen = await page.locator(NAME_SELECTOR).count()
        if new_seen == seen:
            stalled += 1
            if stalled >= STALL_LIMIT:
                print("⇢ No new rows after", STALL_LIMIT, "tries — stopping.")
                break
        else:
            seen, stalled = new_seen, 0
            print(f"⇢ rows collected so far: {seen}")
