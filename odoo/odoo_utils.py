import xmlrpc.client
import csv
from datetime import datetime
from django.conf import settings
import os
from analytics.models import AnalyticHistory
from file_dump_store import dump_file_to_ftp

def authenticate_odoo(url, db, username, password):
    """Authenticate with Odoo and return UID."""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    return common.authenticate(db, username, password, {})

def get_odoo_tables(url, db, uid, password):
    """Get all models (tables) from Odoo."""
    with xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object') as models:
        tables = models.execute_kw(db, uid, password, 'ir.model', 'search_read', [[], ['model']])
        field_names = [table['model'] for table in tables]
        return sorted(field_names)


def get_odoo_table_fields(url, db, uid, password, table_name):
    """Get fields of a specific table (model) from Odoo."""
    with xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object') as models:
        fields = models.execute_kw(db, uid, password, 'ir.model.fields', 'search_read', 
                                   [[('model', '=', table_name)], ['name']])
        
        field_names = [field['name'] for field in fields]
        return sorted(field_names)


def fetch_product_details(url, db, username, password, schedule_name, output_detail):
    """Fetch product details from Odoo and write them to a CSV file."""
    if url:
        uid = authenticate_odoo(url, db, username, password)

        with xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object') as models:
            product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[]])
            products = models.execute_kw(db, uid, password, 'product.template', 'read', [product_ids], {'fields': ['default_code', 'name', 'description', 'standard_price', 'warehouse_id']})
            
            # Create CSV file
            create_csv(products, schedule_name, output_detail)
            
            print('Successfully exported product details to CSV')

    # except Exception as e:
    #     print(f'An error occurred: {str(e)}')

def create_csv(products, schedule_name, output_detail):
    """Create a CSV file with product details."""
    file_name = f'{schedule_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SKU', 'Name', 'Description', 'Unit cost', 'location'])  # Header row
        
        for product in products:
            sku = product.get('default_code', '')
            name = product.get('name', '')
            description = product.get('description', '')
            standard_price = product.get('standard_price', 0.0)
            warehouse_id = None
            
            writer.writerow([sku, name, description, standard_price, warehouse_id])

    AnalyticHistory.objects.create(
            schedule_name=schedule_name,
            file_name=file_name
        )
    
    dump_file_to_ftp(output_detail, file_path)
    
    return file_name
