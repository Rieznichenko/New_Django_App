import xmlrpc.client


def authenticate_odoo(url, db, username, password):
    """Authenticate with Odoo and return UID."""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    return common.authenticate(db, username, password, {})

def get_odoo_tables(url, db, uid, password):
    """Get all models (tables) from Odoo."""
    with xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object') as models:
        tables = models.execute_kw(db, uid, password, 'ir.model', 'search_read', [[], ['model']])
        return [table['model'] for table in tables]


def get_odoo_table_fields(url, db, uid, password, table_name):
    """Get fields of a specific table (model) from Odoo."""
    with xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object') as models:
        fields = models.execute_kw(db, uid, password, 'ir.model.fields', 'search_read', 
                                   [[('model', '=', table_name)], ['name']])
        return [field['name'] for field in fields]