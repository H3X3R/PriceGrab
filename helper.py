from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import re

def scrape_google_shopping(query):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)

        page.goto("https://www.google.com/shopping", timeout=30000)
        page.wait_for_selector("textarea.gLFyf", timeout=10000)

        search_box = page.query_selector("textarea.gLFyf")
        search_box.click()
        search_box.fill(query)
        page.keyboard.press("Enter")

        page.wait_for_timeout(5000)

        product_cards = page.query_selector_all("div.MtXiu.mZ9c3d.wYFOId.M919M.W5CKGc.wTrwWd")
        # if product_cards is not None:
            # print("Found product cards!")
            # print(product_cards)
            
        for card in product_cards:
            try:
                click_target = card.query_selector("div.V5fewe.ekLdoc.BxoXlc") or card
                click_target.scroll_into_view_if_needed()
                click_target.click()
                page.wait_for_timeout(2000)

                price_span = card.query_selector("span.lmQWe")
                price_str = price_span.inner_text().strip() if price_span else None
                print(price_str)

                title_tag = card.query_selector("div.JK3kIe.fUZmuc.sjBi9c.uhHOwf.BYbUcd")
                title = title_tag.get_attribute("title") if title_tag else "Unknown"
                print(title)

                link_tag = page.query_selector("a.P9159d.hMk97e.BbI1ub")
                link = link_tag.get_attribute("href") if link_tag else None
                if link and not link.startswith("http"):
                    link = "https://www.google.com" + link
                    
                print(link)
                print("=====================")
                
                if not price_str or not link:
                    continue

                price_match = re.search(r"[\d,.]+", price_str)
                if not price_match:
                    continue

                price = price_match.group().replace(",", "")
                results.append({
                    "productName": title,
                    "price": price,
                    "currency": "USD",
                    "link": link
                })
            except Exception as e:
                print(f"[Card error] {e}")
                continue

        browser.close()
    return results

if __name__ == "__main__":
    from pprint import pprint

    query = "iPhone 16 Pro, 128GB"
    output = scrape_google_shopping(query)
    sorted_output = sorted(output, key=lambda x: float(x['price']))
    pprint(sorted_output)