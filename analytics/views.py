import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_code_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')

        try:
            # Compile the code to check for syntax errors
            # compile(code, '<string>', 'exec')
            local_vars = {}
            exec(code, globals(), local_vars)
            return JsonResponse({'message': f'Returned: {local_vars.get("result")}'})
        except SyntaxError as e:
            return JsonResponse({'message': f'Syntax Error: {e}'})
        except Exception as e:
            return JsonResponse({'message': f'Error: {e}'})
    return JsonResponse({'message': 'Invalid request.'})
