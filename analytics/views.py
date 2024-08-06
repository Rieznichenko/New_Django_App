# myapp/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import traceback

@csrf_exempt
def execute_code_view(request, object_id):
    if request.method == 'POST':
        code = request.POST.get('code', '')
        try:
            compile(code, '<string>', 'exec')
            return JsonResponse({'output': 'Syntax is correct.'})
        except SyntaxError as e:
            return JsonResponse({'output': f'Syntax Error: {str(e)}'}, status=400)
        except Exception as e:
            output = str(e) + "\n" + traceback.format_exc()
            return JsonResponse({'output': output}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
