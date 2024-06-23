import xmlrpc.client
from openai import OpenAI
import os
from dotenv import load_dotenv
from odoo.models import *
load_dotenv()

# Constants
URL = ''
DB = ''
USERNAME = ''
PASSWORD = ''

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

def execute_query(models, db, uid, query, PASSWORD, field_details):
    """Execute the given query using XML-RPC."""
    database_table = field_details.get("database_table")
    return models.execute_kw(db, uid, PASSWORD, database_table, 'search', [eval(query)], {'limit': 10})


def fetch_product_names(models, db, uid, product_ids, field_details, PASSWORD):
    """Fetch product names from product IDs."""
    table_fields = field_details.get("table_fields")
    database_table = field_details.get("database_table")
    return models.execute_kw(db, uid, PASSWORD, database_table, 'read', [product_ids], {'fields': table_fields})

# Main function
def main(user_query, api_key, field_details):
    try:
        # Authenticate with Odoo
        URL = field_details.get("database_url")
        with xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object') as models:
            DB = field_details.get("database_name")
            USERNAME = field_details.get("database_username")
            PASSWORD = field_details.get("database_password")


            uid = authenticate_odoo(URL, DB, USERNAME, PASSWORD)

            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)

            # Get OpenAI response
            MESSAGES.append({"role": "user", "content": f"Hi, tell me about {user_query}?"})

            if "cars" not in user_query:
                openai_response = client.chat.completions.create(model="gpt-4o", messages=MESSAGES)
                generated_query = openai_response.choices[0].message.content
            else:
                generated_query = "[(1, '=', 1)]"

            # Execute the modified query
            product_ids = execute_query(models, DB, uid, generated_query, PASSWORD, field_details)

            # Fetch product names
            products = fetch_product_names(models, DB, uid, product_ids, field_details, PASSWORD)

            return products

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def _create_sale_order(models, db, uid, password, partner_id, order_lines):
    """Create a new sale order."""
    order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
        'partner_id': partner_id,
        'order_line': order_lines,
    }])
    return order_id


def create_sale_order(product_id, partner_id, price_unit, product_name):
    uid = authenticate_odoo(URL, DB, USERNAME, PASSWORD)
    with xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object') as models:
        order_lines = [
                (0, 0, {
                    'product_id': product_id,
                    'product_uom_qty': 1,
                    'price_unit': price_unit,
                    'name': product_name
                }),
            ]
            
    order_id = _create_sale_order(models, DB, uid, PASSWORD, partner_id, order_lines)
    return order_id

    