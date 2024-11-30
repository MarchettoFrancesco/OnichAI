import requests
from bs4 import BeautifulSoup

def scrape_carrefour_offers():
    url = "https://www.carrefour.it/promozioni/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("div", class_="card")  # Modifica il selettore per adattarlo al sito Carrefour

    offers = []
    for product in products:
        title = product.find("h3", class_="product-title").text.strip()
        price = product.find("span", class_="product-price").text.strip()
        offers.append({"title": title, "price": price})
    
    return offers

def scrapper_carrefour_v2(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to access {url}: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    promotions = []

    # Find all product div elements with relevant information
    promo_items = soup.find_all("div", class_="product tile product-item-with-tooltip")
    
    for item in promo_items:
        # Extract product data from the data-product-json attribute
        product_data = item.get("data-product-json", "{}")
        
        try:
            # Parse the JSON data inside the data-product-json attribute
            product_json = json.loads(product_data)

            product_name = product_json.get("name", "Unknown Product")
            product_price = product_json.get("price", "No Price")
            product_metric = product_json.get("metric19", "Unknown Metric")
            product_category = product_json.get("category", "No Category")
            product_discount = item.get("data-option-product-discountpercentage", "No Discount")
            promo_name = item.get("data-option-product-promotion-info", "{}")
            promo_json = json.loads(promo_name)
            promo_description = promo_json.get("name", "No Promotion")

            # Append product details to promotions list
            promotions.append({
                "product": product_name,
                "price": product_price,
                "metric": product_metric,
                "category": product_category,
                "discount": product_discount,
                "promotion": promo_description,
            })
        
        except json.JSONDecodeError:
            print("Error decoding JSON for a product.")

    return promotions
