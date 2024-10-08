import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import sys
from io import StringIO, BytesIO
import zipfile
import csv, os
from file_dump_store import dump_file_to_ftp
from analytics.models import AanlyticsSchedule, AnalyticOutput
from llm_bot.tasks import process_csv_generation, process_analytic_save
import paramiko
from .models import AnalyticHistory
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from functools import wraps
from django.utils import timezone
from .google_job import schedule_container


AUTHENTICATION_TOKEN = os.environ.get('AUTH_TOKEN', "99999")


def auth_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Get the Authorization token from headers
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return JsonResponse({'error': 'Authorization token is missing'}, status=401)

        if auth_header != AUTHENTICATION_TOKEN:
            return JsonResponse({'error': 'Invalid authorization token'}, status=403)

        return view_func(request, *args, **kwargs)

    return wrapped_view


@csrf_exempt
def test_connection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        instance_id = data.get('id', '')
        get_schedule_details = AnalyticOutput.objects.get(id = instance_id)

        try:
            # Create an SSH client
            ssh_client = paramiko.SSHClient()
            
            # Automatically add the server's host key
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to the server
            print("Connecting to SFTP server...")
            ssh_client.connect(hostname=get_schedule_details.ftp_destination_server, port=get_schedule_details.ftp_destination_port, 
                               username=get_schedule_details.ftp_destination_user, password=get_schedule_details.ftp_destination_password)
            print("Connected successfully to the SFTP server.")
            
            ssh_client.close()
            return JsonResponse({'success': True, 'message': 'Connection successful!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Unable to create connection with FTP because {e}'}, status=400)




@csrf_exempt
def test_code_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        instance_id = data.get('id', '')

        try:
            local_vars = {}
            get_schedule_details = AanlyticsSchedule.objects.get(id = instance_id)
            task = process_csv_generation.delay(instance_id, code)
            return JsonResponse({'task_id': task.id})



            local_vars["db_url"] = get_schedule_details.select_database.db_url
            local_vars["db_name"] = get_schedule_details.select_database.db_name
            local_vars["username"] = get_schedule_details.select_database.username
            local_vars["password"] = get_schedule_details.select_database.password
            local_vars["output_detail"] = get_schedule_details.output_detail.id
            local_vars["schedule_name"] = get_schedule_details.schedule_name


            # Capture printed output
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()

            exec(code, globals(), local_vars)
            sys.stdout = old_stdout

            # Collect results for multiple CSVs
            results = [value for key, value in local_vars.items() if isinstance(value, tuple) and len(value) == 2]

            if results:
                # Create a zip archive in memory
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_name, csv_data in results:
                        csv_buffer = StringIO()
                        csv_writer = csv.writer(csv_buffer)
                        csv_writer.writerows(csv_data)
                        zip_file.writestr(file_name, csv_buffer.getvalue().encode('utf-8'))  # Encode as bytes

                # Prepare zip file for download
                response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=csv_files.zip'
                return response

            else:
                output = redirected_output.getvalue()
                return JsonResponse({'message': f'Returned: {output}'})
                
        except SyntaxError as e:
            return JsonResponse({'message': f'Syntax Error: {e}'})
        except Exception as e:
            return JsonResponse({'message': f'Error: {e}'})
    return JsonResponse({'message': 'Invalid request.'})



# def create_mist_csv(url, db, username, password, schedule_name, output_detail):
#     """Create MIST CSV from Odoo and write them to a CSV file."""

#     import xmlrpc.client
#     import csv
#     from datetime import datetime
#     from django.conf import settings
#     import os
#     from analytics.models import AnalyticHistory
#     from file_dump_store import dump_file_to_ftp

#     company_ids = [1]  # IDs de las empresas a considerar
#     header_row = ['sku', 'location', 'onhand', 'transit']
#     memory_data = []

#     if url:
#         common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
#         uid = common.authenticate(db, username, password, {})

#         models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

#         # Get product IDs
#         product_ids = models.execute_kw(
#             db, uid, password, 
#             'product.product', 
#             'search', 
#             [[['type', '=', 'product'], ['company_id', 'in', company_ids]]]
#         )

#         if not product_ids:
#             print("No products found.")
#             return None

#         # Get warehouse locations
#         warehouse_ids = models.execute_kw(
#             db, uid, password, 
#             'stock.warehouse', 
#             'search', 
#             [[['company_id', 'in', company_ids]]]
#         )

#         if not warehouse_ids:
#             print("No warehouses found.")
#             return None

#         warehouse_locations = {}
#         for warehouse_id in warehouse_ids:
#             warehouse = models.execute_kw(
#                 db, uid, password, 
#                 'stock.warehouse', 
#                 'read', 
#                 [warehouse_id], 
#                 {'fields': ['lot_stock_id']}
#             )
#             lot_stock_id = warehouse[0].get('lot_stock_id', [None])[0]

#             if lot_stock_id:
#                 location = models.execute_kw(
#                     db, uid, password, 
#                     'stock.location', 
#                     'read', 
#                     [lot_stock_id], 
#                     {'fields': ['complete_name']}
#                 )
#                 location_name = location[0].get('complete_name', '')
#             else:
#                 location_name = ''

#             warehouse_locations[warehouse_id] = location_name

#         # Create CSV file
#         file_name = f'{schedule_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
#         file_path = os.path.join(settings.MEDIA_ROOT, file_name)

#         with open(file_path, mode='w', newline='') as file:
#             writer = csv.writer(file, delimiter=';')
#             writer.writerow(header_row)
#             memory_data.append(header_row)

#             for product_id in product_ids[:5]:
#                 product = models.execute_kw(
#                     db, uid, password, 
#                     'product.product', 
#                     'read', 
#                     [product_id], 
#                     {'fields': ['default_code']}
#                 )

#                 if not product:
#                     continue

#                 sku = product[0].get('default_code', '')

#                 for warehouse_id, location_name in warehouse_locations.items():
#                     row = [sku, location_name, 'N', 'N']
#                     writer.writerow(row)
#                     memory_data.append(row)

#         print(f'Successfully exported stock details to CSV: {file_path}')

#         return file_path  # Return the file path


# # Ejecutar el script
# mist_csv = create_mist_csv(db_url, db_name, username, password, schedule_name, output_detail)


@csrf_exempt
def test_code_analytic_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        instance_id = data.get('id', '')

        try:
            local_vars = {}
            task = process_analytic_save.delay(instance_id, code)
            return JsonResponse({'task_id': task.id})
        except SyntaxError as e:
            return JsonResponse({'message': f'Syntax Error: {e}'})
        except Exception as e:
            return JsonResponse({'message': f'Error: {e}'})
    return JsonResponse({'message': 'Invalid request.'})


#view functions called from batch
@auth_required
@csrf_exempt
def upload_csv_view(request):
    if request.method == 'POST':
        
        file = request.FILES.get('file')
        file_name = request.POST.get('file_name', file.name)
        output_detail = request.POST.get('output_detail', {})
        
        if file:
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            
            # Save the file to the media folder
            path = default_storage.save(file_path, ContentFile(file.read()))
            dump_file_to_ftp(output_detail, file_path)
            
            return JsonResponse({'message': 'File uploaded successfully', 'file_path': path}, status=200)
        else:
            return JsonResponse({'error': 'No file uploaded'}, status=400)


@auth_required
@csrf_exempt
def get_analytic_schedule_view(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            instance_id = request_body.get('instance_id')

            if not instance_id:
                return JsonResponse({'error': 'instance_id is required'}, status=400)

            # Fetch the schedule details
            get_schedule_details = AanlyticsSchedule.objects.get(id=instance_id)
            get_schedule_details.is_running = True
            get_schedule_details.last_run = timezone.now()
            get_schedule_details.save()

            # Return schedule details as response
            response_data = {
                "select_dataabase": {
                    "db_url": get_schedule_details.select_database.db_url,
                    "db_name": get_schedule_details.select_database.db_name,
                    "username": get_schedule_details.select_database.username,
                    "password": get_schedule_details.select_database.password
                },
                "output_details_id": get_schedule_details.output_detail.id,
                "schedule_name": get_schedule_details.schedule_name
            }

            return JsonResponse(response_data, status=200)

        except AanlyticsSchedule.DoesNotExist:
            return JsonResponse({'error': 'Schedule not found'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@auth_required
@csrf_exempt
def update_analytic_schedule_view(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            instance_id = request_body.get('instance_id')

            if not instance_id:
                return JsonResponse({'error': 'instance_id is required'}, status=400)

            # Fetch the schedule details
            get_schedule_details = AanlyticsSchedule.objects.get(id=instance_id)
            get_schedule_details.is_running = False
            get_schedule_details.next_execution = timezone.now() + timezone.timedelta(hours=int(get_schedule_details.output_plan))
            get_schedule_details.save()


            return JsonResponse({}, status=200)

        except AanlyticsSchedule.DoesNotExist:
            return JsonResponse({'error': 'Schedule not found'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@auth_required
@csrf_exempt
def create_analytic_history_view(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            schedule_name = request_body.get('schedule_name')
            file_name = request_body.get('file_name')

            # Create a new AnalyticHistory record
            AnalyticHistory.objects.create(
                schedule_name=schedule_name,
                file_name=file_name
            )

            return JsonResponse({}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@auth_required
@csrf_exempt
def execute_batch_container(request):
    if request.method == "POST":
        try:
            request_body = json.loads(request.body)
            instance_id = request_body.get("instance_id")

            get_schedule_details = AanlyticsSchedule.objects.get(id=instance_id)
            schedule_container(get_schedule_details)
            return JsonResponse({'status': True, "error": ""}, status=200)

        except Exception as e:
            return JsonResponse({'status': False, "error": f"Failed: {str(e)}"}, status=500)