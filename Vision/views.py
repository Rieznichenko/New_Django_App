from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests
import json
from .models import VisionApplication, ApplicationUser, LLMConfiguration
from openai import OpenAI

import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import VisionApplication, LLMConfiguration
from PIL import Image
import io
import openai
import base64


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



def get_image_bae64(image_file):
    image = Image.open(image_file)
    buffered = io.BytesIO()
    image.save(buffered, format=image.format)
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/{image.format.lower()};base64,{img_base64}"



@method_decorator(csrf_exempt, name='dispatch')
class AnalyzeImage(View):
    def post(self, request, *args, **kwargs):
        # Check content type
        content_type = request.headers.get('Content-Type')
        print(f"Content-Type: {content_type}")

        token = request.POST.get('token')
        image_file = request.FILES.get('image') 

        print(f"Received token: {token}")
            # Validate token and get application and users
        try:
            vision_application = VisionApplication.objects.get(unique_token=token)
            bot_token = vision_application.telegram_bot_id
            print(f"Retrieved bot token: {bot_token}")
        except VisionApplication.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=400)
        except AttributeError:
            return JsonResponse({'error': 'Bot token not found in VisionApplication'}, status=500)

        # Retrieve OpenAI credentials and prompt
        llm_config = LLMConfiguration.objects.get(vision_application=vision_application)
        api_key = llm_config.openai_key
        assistant_id = llm_config.assistant_id
        prompt = llm_config.prompt

        client = OpenAI(api_key = api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{prompt}"},
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": get_image_bae64(image_file)
                        },
                        },
                    ],
                    }
                ],
                max_tokens=300,
                )
            # Get the analysis result from the API response
            result = response.choices[0].message.content
            return JsonResponse({"analysis": result}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)