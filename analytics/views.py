import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import sys
from io import StringIO, BytesIO
import zipfile

@csrf_exempt
def test_code_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')

        try:
            local_vars = {}

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
                    for idx, (file_name, csv_content) in enumerate(results):
                        zip_file.writestr(file_name, csv_content)

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
