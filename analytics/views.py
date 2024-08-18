import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import sys
from io import StringIO, BytesIO
import zipfile
import csv
from analytics.models import AanlyticsSchedule

@csrf_exempt
def test_code_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        instance_id = data.get('id', '')

        try:
            local_vars = {}
            get_schedule_details = AanlyticsSchedule.objects.get(id = instance_id)

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
