from playwright.async_api import Locator
from scraping.config import NEXT_BTN_SELECTOR

async def click_next_if_present(page) -> bool:
    """
    Returns True if it successfully clicked to the next page.
    Returns False when the control is missing or disabled.
    """
    next_btn: Locator = page.locator(NEXT_BTN_SELECTOR)
    if await next_btn.count() == 0:
        return False
    if not await next_btn.is_enabled():
        return False

    await next_btn.click()
    # let DOM stabilize – tailor this wait if the site behaves differently
    await page.wait_for_load_state("domcontentloaded")
    return True
