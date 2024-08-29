from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests
import json
from .models import VisionApplication, ApplicationUser

@method_decorator(csrf_exempt, name='dispatch')
class SendMessageView(View):
    def post(self, request, *args, **kwargs):
        # Check content type
        content_type = request.headers.get('Content-Type')
        print(f"Content-Type: {content_type}")

        # Extract parameters
        if 'application/json' in content_type:
            data = json.loads(request.body)
            token = data.get('token')
            message_type = data.get('message_type')
            image_url = data.get('image_url')
            text_message = data.get('text_message')
        else:
            token = request.POST.get('token')
            message_type = request.POST.get('message_type')
            image_url = request.POST.get('image_url')
            text_message = request.POST.get('text_message')

        print(f"Received token: {token}")
        print(f"Received message_type: {message_type}")

        # Validate token and get application and users
        try:
            vision_application = VisionApplication.objects.get(unique_token=token)
            bot_token = vision_application.telegram_bot_id
            print(f"Retrieved bot token: {bot_token}")
        except VisionApplication.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=400)
        except AttributeError:
            return JsonResponse({'error': 'Bot token not found in VisionApplication'}, status=500)

        application_users = ApplicationUser.objects.filter(vision_application=vision_application)

        # Send messages
        responses = []
        for user in application_users:
            chat_id = user.channel_username
            if image_url:
                response = self.send_image_message(bot_token, chat_id, image_url)
                responses.append(response)
            if text_message:
                response = self.send_text_message(bot_token, chat_id, text_message)
                responses.append(response)
            else:
                return JsonResponse({'error': 'Invalid message type'}, status=400)

        return JsonResponse({'status': 'Messages sent', 'responses': responses})

    def send_text_message(self, bot_token, chat_id, text_message):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {'chat_id': chat_id, 'text': text_message}
        response = requests.post(url, data=payload)
        return response.json()

    def send_image_message(self, bot_token, chat_id, image_url):
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        payload = {'chat_id': chat_id, 'photo': image_url}
        response = requests.post(url, data=payload)
        return response.json()
