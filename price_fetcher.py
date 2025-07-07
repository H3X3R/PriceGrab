# import requests
# from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
from pprint import pprint
# from playwright.sync_api import sync_playwright
# import re
from helper import scrape_google_shopping

# === SOURCE REGISTRY ===

SOURCE_REGISTRY = {
    "US": [
        # {"name": "Amazon", "type": "api", "handler": "fetch_amazon"},
        # {"name": "Walmart", "type": "api", "handler": "fetch_walmart"},
        # {"name": "BestBuy", "type": "scrape", "handler": "scrape_bestbuy"},
        {"name": "Google Shopping", "type": "aggregator", "handler": "scrape_google_shopping"}
    ],
    "IN": [
        # {"name": "Flipkart", "type": "scrape", "handler": "scrape_flipkart"},
        # {"name": "Amazon.in", "type": "scrape", "handler": "scrape_amazon_in"},
        # {"name": "Sangeetha", "type": "scrape", "handler": "scrape_sangeetha"},
        {"name": "Google Shopping", "type": "aggregator", "handler": "scrape_google_shopping"}
    ]
}

# === HANDLER REGISTRATION ===

# def fetch_amazon(query):
#     return [{
#         "productName": "iPhone 16 Pro",
#         "price": "999",
#         "currency": "USD",
#         "link": "https://amazon.com/product1"
#     }]

# def fetch_walmart(query):
#     return [{
#         "productName": "iPhone 16 Pro - Walmart",
#         "price": "989",
#         "currency": "USD",
#         "link": "https://walmart.com/product1"
#     }]

# def scrape_bestbuy(query):
#     return [{
#         "productName": "iPhone 16 Pro - Blue",
#         "price": "979",
#         "currency": "USD",
#         "link": "https://bestbuy.com/product2"
#     }]

# def scrape_google_shopping(query):
#     base_url = "https://www.google.com/search"
#     gl = "US"
#     if "india" in query.lower() or "₹" in query or "inr" in query.lower():
#         gl = "IN"

#     params = {
#         "q": query,
#         "tbm": "shop",
#         "gl": gl,
#         "udm": "28"
#     }
#     headers = {
#         "User-Agent": UserAgent().random
#     }

#     try:
#         response = requests.get(base_url, params=params, headers=headers, timeout=10)
#         print(response)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         print(soup)

#         results = []

#         product_blocks = soup.select('div.sh-dgr__content') 

#         for block in product_blocks:
#             title_tag = block.select_one("h3.tAxDx")
#             link_tag = block.select_one("a.shntl")
#             price_tag = block.select_one("span.a8Pemb")

#             if not title_tag or not link_tag or not price_tag:
#                 continue

#             name = title_tag.text.strip()
#             link = "https://www.google.com" + link_tag["href"]
#             price_str = price_tag.text.strip()
#             price_match = re.search(r"[\d,]+(?:\.\d{2})?", price_str)

#             if not price_match:
#                 continue

#             price = price_match.group().replace(",", "")
#             results.append({
#                 "productName": name,
#                 "price": price,
#                 "currency": "USD",
#                 "link": link
#             })
#         # print("======")
#         # print(results)
#         # print("======")
#         return results

#     except Exception as e:
#         print(f"[Google Shopping] Failed: {e}")
#         return []



# def scrape_google_shopping(query):
#     results = []
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
#         page = context.new_page()

#         search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=shop&gl=US"
#         page.goto(search_url, timeout=30000)
#         page.wait_for_load_state("domcontentloaded")
#         page.wait_for_timeout(10000)  

#         cards = page.query_selector_all("g-card.tkfIqc")

#         if not cards:
#             print("[DEBUG] No g-card.tkfIqc found. Dumping partial HTML:")
#             print(page.content()[:1000]) 

#         for card in cards:
#             try:
#                 title_el = card.query_selector("div[role='heading']") or card.query_selector("div.tAxDx")
#                 price_el = card.query_selector("span.a8Pemb")
#                 link_el = card.query_selector("a")

#                 if not title_el or not price_el or not link_el:
#                     continue

#                 name = title_el.inner_text().strip()
#                 price_str = price_el.inner_text().strip()
#                 link = link_el.get_attribute("href")
#                 if not link:
#                     continue

#                 price_match = re.search(r"[\d,]+(?:\.\d{2})?", price_str)
#                 if not price_match:
#                     continue

#                 price = price_match.group().replace(",", "")
#                 results.append({
#                     "productName": name,
#                     "price": price,
#                     "currency": "USD",
#                     "link": "https://www.google.com" + link
#                 })
#             except Exception as e:
#                 print(f"[card error] {e}")
#                 continue

#         browser.close()
#     return results



HANDLER_FUNCTIONS = {
    "scrape_google_shopping": scrape_google_shopping,
    # "fetch_amazon": fetch_amazon,
    # "fetch_walmart": fetch_walmart,
    # "scrape_bestbuy": scrape_bestbuy,
    # "scrape_flipkart": scrape_flipkart,
    # "scrape_amazon_in": scrape_amazon_in,
    # "scrape_sangeetha": scrape_sangeetha
}

# === QUERY PIPELINE ===

def get_sources_for_country(country_code):
    return SOURCE_REGISTRY.get(country_code.upper(), [])

def run_query_pipeline(user_input):
    country = user_input["country"]
    query = user_input["query"]
    
    sources = get_sources_for_country(country)
    results = []

    for source in sources:
        handler_func = HANDLER_FUNCTIONS.get(source["handler"])
        if handler_func:
            try:
                source_results = handler_func(query)
                results.extend(source_results)
            except Exception as e:
                print(f"[{source['name']}] error: {e}")
    
    return results

# === TEST MAIN ===

if __name__ == "__main__":
    input_data = {
        "country": "US",
        "query": "iPhone 16 Pro, 128GB"
    }

    output = run_query_pipeline(input_data)
    output_sorted = sorted(output, key=lambda x: float(x['price']))
    
    pprint(output_sorted)