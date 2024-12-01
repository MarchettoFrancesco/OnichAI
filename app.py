import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq
import requests
from bs4 import BeautifulSoup
import searchProducts

# Initialize Flask app
app = Flask(__name__)

# Initialize Groq client (make sure you set up your GROQ_API_KEY in your environment)
groq_client = Groq(api_key='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')

# Function to scrape supermarket promotions (Carrefour example)
def scrape_promotions(url):
    return searchProducts.searchProducts([url])

# Function to generate recipes based on the scraped products

def generate_recipe(products):
    if not isinstance(products, list):
        return "Invalid input: Products must be a list."

    # Construct the prompt with the product details
    ingredients = ", ".join([product for product in products])
    prompt = f"""
    Given the following ingredients: {ingredients}, generate different healthy recipes that use these ingredients. 
    If there are no recipes still write a recipe with "title" :"No recipe was possible".
    Include only the ingredients used in the single recipe, not others.
    Each recipe should include the following fields:
    - "title": the title of the recipe,
    - "description": a short description of the recipe,
    - "ingredients": a list of ingredients used in the recipe,
    - "price": the estimated price of the recipe.

    The response should be in italian and in valid JSON format as follows:
    [
        {{
            "title": "Recipe 1",
            "description": "Description of Recipe 1",
            "ingredients": ["Ingredient 1", "Ingredient 2"],
            "price": x.xx
        }},
        {{
            "title": "Recipe 2",
            "description": "Description of Recipe 2",
            "ingredients": ["Ingredient 3", "Ingredient 4"],
            "price": x.xx
        }},
        
    ]
    """

    try:
        
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",  # Use LLAMA model for recipe generation
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=1,  # Adjust temperature for creativity in recipes
            max_tokens=1024,
        )
        recipe_text = response.choices[0].message.content.strip()

        # Extract the JSON part by finding the first `[` and last `]`
        json_start = recipe_text.find('[')
        json_end = recipe_text.rfind(']') + 1  # Include the closing bracket
        if json_start == -1 or json_end == -1:
            print("Error: No valid JSON found in the response.")
            print(f"Raw response: {recipe_text}")
            return None

        json_text = recipe_text[json_start:json_end]

        # Parse and validate the JSON response
        try:
            recipes_data = json.loads(json_text)

            # Ensure recipes_data is a list
            if not isinstance(recipes_data, list):
                print("Error: The response is not a list of recipes.")
                print(f"Raw JSON: {json_text}")
                return None

            # Print details for each recipe
            for i, recipe in enumerate(recipes_data, start=1):
                # Ensure each item in recipes_data is a dictionary
                if not isinstance(recipe, dict):
                    print(f"Error: Recipe {i} is not a valid dictionary.")
                    continue

                title = recipe.get("title", "No title")
                description = recipe.get("description", "No description")
                ingredients = recipe.get("ingredients", [])
                price = recipe.get("price", "No price")

                print(f"Recipe {i}:")
                print(f"  Title: {title}")
                print(f"  Description: {description}")
                print(f"  Ingredients: {', '.join(ingredients) if isinstance(ingredients, list) else 'No ingredients listed'}")
                print(f"  Price: €{price}")
                print()  # Blank line between recipes

            # Return the parsed recipes data for further use
            return recipes_data

        except json.JSONDecodeError:
            print("Error: The extracted JSON is not valid.")
            print(f"Extracted JSON: {json_text}")
            return None
    
    except Exception as e:
        print(f"Error generating recipe: {str(e)}")
        return None


from flask import send_from_directory

@app.route('/templates/<path:path>')
def send_report(path):
    # Using request args for path will expose you to directory traversal attacks
    return send_from_directory('templates', path)
# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        url = request.json.get("url")
        # print(url)
        promotions = scrape_promotions(url)
        return jsonify({"promotions": promotions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate_recipe", methods=["POST"])
def recipe():
    try:
        selected_products = request.json.get("products")
        # Debugging to check the received data
        print("Received products:", selected_products)

        if not isinstance(selected_products, list):
            raise ValueError("Products should be a list")
        
        # Now, generate the recipe as before
        recipe = generate_recipe(selected_products)
        return jsonify({"recipe": recipe})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
