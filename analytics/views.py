import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import sys
from io import StringIO


@csrf_exempt
def test_code_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')

        try:
            # Compile the code to check for syntax errors
            # compile(code, '<string>', 'exec')
            local_vars = {}

            # Capture printed output
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()

            exec(code, globals(), local_vars)
            sys.stdout = old_stdout

            output = redirected_output.getvalue()
            result = local_vars.get("result", output)


            return JsonResponse({'message': f'Returned: {result}'})
        except SyntaxError as e:
            return JsonResponse({'message': f'Syntax Error: {e}'})
        except Exception as e:
            return JsonResponse({'message': f'Error: {e}'})
    return JsonResponse({'message': 'Invalid request.'})
