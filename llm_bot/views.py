from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponse
import os
import openai
import time
import logging
from llm_bot.models import LLMCOnfig, LLMAgent, WhatsAppBotConfig
import requests
import logging
from llm import chat_functionality_gemini,chat_functionality

logging.basicConfig(
    format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", level=logging.INFO
)

VALID_PROVIDERS = ["gemini", "openai"]



def ajax_get_config(request):
    llm_config_id = request.GET.get('id', '')

    llm_config_instance = LLMCOnfig.objects.get(id=llm_config_id)

    llm_agents = LLMAgent.objects.filter(llm_config = llm_config_instance)

    result = list(llm_agents.values('id', 'agent_name'))
    return HttpResponse(json.dumps(result), content_type="application/json")

def get_llm_config(channel_id):
    most_recent_config = WhatsAppBotConfig.objects.get(whatsapp_channel_id = channel_id)
    llm_config_id = most_recent_config.whatsapp_llm_config.id
    llm_config = LLMCOnfig.objects.get(id = llm_config_id)

    llm_assistant_id = most_recent_config.whatsapp_llm_agent.assistant_id
    api_key = llm_config.api_key
    bot_token = most_recent_config.whatsapp_bot_token

    return api_key, llm_assistant_id, bot_token

@csrf_exempt
def webhook_whatsapp(request):
    # Retrieving incoming message
    incoming_message = json.loads(request.body)
    
    # Retrieving the text of the message
    message_text = incoming_message['messages'][0]['text'].get("body")
    message_from = incoming_message['messages'][0].get("from")
    channel_id = incoming_message.get("channel_id")

    if incoming_message['messages'][0]['from_me']:
        return JsonResponse({"status": True}, status=200)


    api_key, assitant_id, bot_token = get_llm_config(channel_id)

    if "asst_" in assitant_id:
        logging.info("Openai client created")
        openai.api_key = api_key
        OPENAI_CLIENT = openai.Client(api_key=api_key)
        logging.info(f"Message received: {message_text}")
        # Ensure the message is not empty
        if message_text:
            try:
                thread = OPENAI_CLIENT.beta.threads.create()
                thread_id = thread.id
                assistant_message = chat_functionality(OPENAI_CLIENT, message_text, thread_id, assitant_id, message_from, bot_token)
                send_message(assistant_message, message_from, bot_token)
            except Exception as e:
                logging.exception(e)

    else:
        gemini_message = chat_functionality_gemini(message_text, api_key, assitant_id, message_from, bot_token)
        send_message(gemini_message, message_from, bot_token)

    return JsonResponse({"status": True}, status=200)



def send_message(response_text, to, bot_token):
    # URL to send messages through the Whapi.Cloud API
    url = f"https://gate.whapi.cloud/messages/text?token={bot_token}"

    # Forming the body of the message
    payload = {
        "to": to,
        "body": response_text
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    # Sending the message
    response = requests.post(url, json=payload, headers=headers)
    logging.info(response.text)
    return True