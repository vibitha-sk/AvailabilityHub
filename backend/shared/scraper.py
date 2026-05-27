"""Product availability scraper using BeautifulSoup."""
import logging
import re
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 15


def check_availability(url: str, desired_size: str) -> bool:
    """
    Scrape the product page and return True if the desired size appears
    to be available (not sold out / out of stock).

    Strategy:
    1. Fetch the page HTML.
    2. Look for size selector elements (buttons, options, labels).
    3. Check if the desired size text is present and not marked as disabled/sold-out.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    size_str = desired_size.strip().upper()

    # --- Strategy 1: look for <button> or <option> elements with the size text ---
    for tag in soup.find_all(["button", "option", "li", "span", "label"]):
        tag_text = tag.get_text(strip=True).upper()
        if tag_text == size_str or tag_text == size_str.replace(" ", ""):
            classes = " ".join(tag.get("class", [])).lower()
            aria_disabled = tag.get("aria-disabled", "").lower()
            disabled_attr = tag.get("disabled")
            # If the element is explicitly disabled or has sold-out class, skip
            if (
                disabled_attr is not None
                or aria_disabled == "true"
                or any(kw in classes for kw in ["sold-out", "soldout", "unavailable", "disabled", "out-of-stock"])
            ):
                return False
            return True

    # --- Strategy 2: JSON-LD structured data ---
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            data = json.loads(script.string or "{}")
            offers = data.get("offers", [])
            if isinstance(offers, dict):
                offers = [offers]
            for offer in offers:
                name = (offer.get("name") or "").upper()
                avail = (offer.get("availability") or "").lower()
                if size_str in name and "instock" in avail.replace("/", "").replace("schema.org", ""):
                    return True
        except Exception:
            pass

    # --- Strategy 3: plain text search as fallback ---
    page_text = soup.get_text(" ", strip=True).upper()
    size_pattern = re.compile(rf"\b{re.escape(size_str)}\b")
    if size_pattern.search(page_text):
        # Check if "out of stock" or "sold out" appears near the size mention
        out_of_stock_pattern = re.compile(r"(OUT OF STOCK|SOLD OUT|UNAVAILABLE)", re.I)
        if not out_of_stock_pattern.search(page_text):
            return True

    return False
