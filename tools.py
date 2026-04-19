from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import trafilatura

def scrape_website(url: str) -> str:
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            geolocation={"latitude": 12.9716, "longitude": 77.5946},
            permissions=["geolocation"],
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-IN,en;q=0.9",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        html = page.content()
        browser.close()

    text = trafilatura.extract(html, include_tables=True, include_links=False)
    if text:
        print(f"Scraped {len(text)} characters from {url}")
        return text[:4000]
    return ""

def get_product_details_blinkit(item: str) -> str:
    return scrape_website(f"https://blinkit.com/s/?q={item.replace(' ', '+')}")

def get_product_details_zepto(item: str) -> str:
    return scrape_website(f"https://www.zepto.com/search?query={item.replace(' ', '+')}")

def get_product_details_bigbasket(item: str) -> str:
    return scrape_website(f"https://www.bigbasket.com/ps/?q={item.replace(' ', '+')}&nc=as")
    

if __name__ == "__main__":
    print(get_product_details_zepto("onion"))
    print(get_product_details_blinkit("onion"))
    print(get_product_details_bigbasket("onion"))