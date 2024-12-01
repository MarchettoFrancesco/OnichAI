import requests
from bs4 import BeautifulSoup
import json


from groq import Groq


def format(products):
    promotions=[]
    for item in products:
        # Extract product data from the data-product-json attribute
        
        try:
            # Parse the JSON data inside the data-product-json attribute
            product_json = item

            product_name = product_json.get("name", "Unknown Product")
            product_price = product_json.get("price", "No Price")
            product_metric = product_json.get("metric19", "Unknown Metric")
            product_category = product_json.get("category", "No Category")
            product_discount = item.get("discount", "No Discount")
            promo_name = item.get("promo_name", "{}")
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
def extract_images(soup):
    images = soup.find_all('img')# Extract and print image URLs and alt attributes
    result = []
    for img in images:
        img_url = img.get('src',None)
        alt_text = img.get('alt', 'No alt attribute')
        result.append({
            'src':img_url,
            'alt_text': alt_text
        })
    return result
        
def searchProducts(urls):
    client = Groq(
        api_key="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",
    )
    products=[]
    for url in urls:
        # print(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        data = soup.get_text()
        data = ' '.join(data.split()) 
       

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f'Read the next text and scrapp the name of the products and their prices return all as a list of product price and only food: {data} '
                        
                }
            ],
            model="llama3-70b-8192",
        )
        text= chat_completion.choices[0].message.content
        print(text)
        chat_completion=client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content":"Yor are a text to JSON parser the result is a JSON {products:[ {name: <description>, price: <name>, category: <category>}}]}, you only use the data in the input to create the list, you only respond with the JSON, remove products that are not food"                        
                },
                {
                    "role": "user",
                    "content":text       
                }
            ],
            model="llama3-70b-8192",
            max_tokens=7340,
            response_format={"type": "json_object"},
        )
        print(chat_completion.choices[0].message.content)
        
        
        products_json= chat_completion.choices[0].message.content
        # images_dict = extract_images(soup)
        # images_json=json.dump({'images':images_dict},indent=2)
        # merge = chat_completion=client.chat.completions.create(
        #     messages=[
        #         {
        #             "role": "system",
        #             "content":"Yor are a text to JSON parser the result is a JSON {products:[ {name: <description>, price: <name>, category: <category>, discount:<discoun>, image:<image> alt_src:<alt_src>}}]}, you only use the data in the input to create the list, you only respond with the JSON, remove products that are not food"                        
        #         },
        #         {
        #             "role": "user",
        #             "content":f'using the next two json try to merge if and only if you think they can be together base on name product and image_alt :{products_json} {images_json} '       
        #         }
        #     ],
        #     model="llama3-70b-8192",
        #     max_tokens=7340,
        #     # response_format={"type": "json_object"},
        # )

        # print(merge)
        r = json.loads(products_json)
        r = format(products=r['products'])
        products.extend(r)
    print(products)   
    return  products
    
if __name__ == "__main__":
    products_json = searchProducts(['https://www.aldi.it/it/offerte-settimanali/offerte-di-questa-settimana.html#freschezza',
                    # 'https://pamacasa.pampanorama.it/spesa-consegna-domicilio/00144/prodotti-in-promozione?sort=promo',
                    # 'https://www.carrefour.it/promozioni/'
                    ])
