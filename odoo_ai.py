import xmlrpc.client
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
URL = os.environ.get("DB_URL")
DB = os.environ.get("DB_NAME")
USERNAME = os.environ.get("DB_USERNAME")
PASSWORD = os.environ.get("DB_PASSWORD")

# Messages
MESSAGES = [
  {
    "role": "system",
    "content": "You will be given an input string you need to find intent on it and Based on that Write an Odoo's XML-RPC query to answer the user's question. Please don't return extra commentary, just return the query. Valid Example: [['name', 'ilike', 'AJUSTE DE CONSIGNACION'], ['sale_ok', '=', True]], Invalid Example: [[['name', '=', 'AJUSTE DE CONSIGNACION'], ['sale_ok', '=', True]]]"
  }
]

def authenticate_odoo(url, db, username, password):
    """Authenticate with Odoo and return UID."""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    return common.authenticate(db, username, password, {})

def execute_query(models, db, uid, query):
    """Execute the given query using XML-RPC."""
    return models.execute_kw(db, uid, PASSWORD, 'product.product', 'search', [eval(query)])


def fetch_product_names(models, db, uid, product_ids):
    """Fetch product names from product IDs."""
    return models.execute_kw(db, uid, PASSWORD, 'product.product', 'read', [product_ids], {'fields': ['name', 'website_url', 'description']})

# Main function
def main(user_query, api_key):
    try:
        # Authenticate with Odoo
        with xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object') as models:
            uid = authenticate_odoo(URL, DB, USERNAME, PASSWORD)

            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)

            # Get OpenAI response
            MESSAGES.append({"role": "user", "content": f"Hi, tell me about {user_query}?"})
            openai_response = client.chat.completions.create(model="gpt-4o", messages=MESSAGES)

            # Extract the generated query
            generated_query = openai_response.choices[0].message.content

            # Execute the modified query
            product_ids = execute_query(models, DB, uid, generated_query)

            # Fetch product names
            products = fetch_product_names(models, DB, uid, product_ids)

            return products

    except Exception as e:
        print(f"An error occurred: {str(e)}")