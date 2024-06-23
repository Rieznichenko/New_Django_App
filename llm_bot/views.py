from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import os
import openai
import time
import logging
from functools import wraps
from llm_bot.models import ChatBotMessage, DiscordBotConfig, EmailSchedule, LLMCOnfig, LLMAgent, \
    TelegramBotConfig, WhatsAppBotConfig, ChatBot
from odoo.models import *
import requests
import logging
from llm import chat_functionality_gemini,chat_functionality
from odoo_ai import main, create_sale_order
from django.shortcuts import get_object_or_404
from odoo.models import OdooDatabase
from odoo.odoo_utils import get_odoo_tables, authenticate_odoo, get_odoo_table_fields
from django.core.serializers import serialize
from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(
    format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", level=logging.INFO
)

VALID_PROVIDERS = ["gemini", "openai"]


def authorize(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = os.getenv('AUTH_TOKEN')  # Get the token from environment variables
        if not token:
            return JsonResponse({'error': 'Token is not set in environment'}, status=500)
        
        header_token = request.headers.get('Authorization')  # Get the token from request headers
        if header_token == token:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({'error': 'Unauthorized, Please provide a valid token'}, status=401)
    
    return _wrapped_view


def ajax_get_config(request):
    llm_config_id = request.GET.get('id', '')

    llm_config_instance = LLMCOnfig.objects.get(id=llm_config_id)

    llm_agents = LLMAgent.objects.filter(llm_config = llm_config_instance)

    result = list(llm_agents.values('id', 'agent_name'))
    return HttpResponse(json.dumps(result), content_type="application/json")

def ajax_get_odoo_database(request):
    llm_config_id = request.GET.get('id', '')

    llm_config_instance = OdooDatabase.objects.filter(id=llm_config_id)

    result = list(llm_config_instance.values('id', 'database_name', 'read_model', 'write_model'))
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
    api_key, assitant_id, bot_token = get_llm_config(channel_id)

    try:
        obj = WhatsAppBotConfig.objects.get(whatsapp_bot_token=bot_token)
        bot_name = obj.chatbot_name
        if obj.state == "paused":
            return JsonResponse({"status": False}, status=400)
    except WhatsAppBotConfig.DoesNotExist:
            return JsonResponse({"status": False}, status=400)
    if incoming_message['messages'][0]['from_me']:
        return JsonResponse({"status": True}, status=200)



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
                assistant_message = chat_functionality(OPENAI_CLIENT, '', message_text, thread_id, assitant_id)
                ChatBotMessage.objects.create(content=message_text, author="Human", chatbot_name=bot_name, bot_type="whatsapp")
                ChatBotMessage.objects.create(content=assistant_message, author='Bot', chatbot_name=bot_name, bot_type="whatsapp")

                send_message(assistant_message, message_from, bot_token)
            except Exception as e:
                logging.exception(e)

    else:
        gemini_message = chat_functionality_gemini(message_text, '', api_key, assitant_id)
        ChatBotMessage.objects.create(content=message_text, author="Human", chatbot_name=bot_name, bot_type="whatsapp")
        ChatBotMessage.objects.create(content=assistant_message, author='Bot', chatbot_name=bot_name, bot_type="whatsapp")
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


@authorize
def chatbot_details(request):
    try:
        widget_id = request.GET.get('widget_id')
        type = request.GET.get('type')
        if not type:
            chatbot = ChatBot.objects.get(widget_id=widget_id)

        if chatbot:
            response_data = {
                'widget_id': widget_id,
                'chatbot_name': chatbot.chatbot_name,
                'logo': f"https://ia.humanytek.com{chatbot.logo.url}" if chatbot.logo else None,
                "welcome_message": chatbot.welcome_message
            }
        else:
            response_data = { "message": "Please add a chatbot first." }

        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({"error": f"faiure occurred because {e}"}, status=500)
    
@authorize
def sale_odoo_products(request):
    product_id = request.GET.get('product_id')
    partner_id = 30970
    product_quantity = 1
    unit_price = request.GET.get('unit_price')
    product_name = request.GET.get('product_name')

    if product_id and partner_id and unit_price:
        order_id = create_sale_order(product_id, partner_id, unit_price, product_name)
        return JsonResponse({"order_id": order_id})
    else:
        return JsonResponse({"error": f"faiure occurred because one of the fields among product_id, unit_price is missing"}, status=500)




    
@authorize
def call_llm_model(request):
    widget_id = request.GET.get('widget_id')
    user_input = request.GET.get('user_input')

    chatbot = ChatBot.objects.get(widget_id=widget_id)
    bot_name=chatbot.chatbot_name
    if chatbot.state == "paused":
        return JsonResponse({"error": "Bot has been stopped."}, status=400)
    
    lm_config_instance = LLMCOnfig.objects.get(id=chatbot.chatbot_llm_config.id)
    llm_agent = LLMAgent.objects.get(llm_config = chatbot.chatbot_llm_agent.id)

    assistant_id = llm_agent.assistant_id
    api_key = lm_config_instance.api_key

    print(user_input)

    try:
        # Ensure the message is not empty
        if user_input:
            if "asst_" in assistant_id:
                logging.info("Openai client created")
                openai.api_key = api_key
                OPENAI_CLIENT = openai.Client(api_key=api_key)
                logging.info(f"Message received: {user_input}")
                
                thread = OPENAI_CLIENT.beta.threads.create()
                thread_id = thread.id
                assistant_message = chat_functionality(OPENAI_CLIENT, "", user_input, thread_id, assistant_id)
                ChatBotMessage.objects.create(content=user_input, author="Human", chatbot_name=bot_name, bot_type="webbot")
                ChatBotMessage.objects.create(content=assistant_message, author='Bot', chatbot_name=bot_name, bot_type="webbot")

                return JsonResponse({"message": assistant_message}, status=200)
            else:
                gemini_response = chat_functionality_gemini(user_input, "", api_key, assistant_id)
                ChatBotMessage.objects.create(content=user_input, author="Human", chatbot_name=bot_name, bot_type="webbot")
                ChatBotMessage.objects.create(content=gemini_response, author='Bot', chatbot_name=bot_name, bot_type="webbot")

                return JsonResponse({"message": gemini_response}, status=200)
        else:
            return JsonResponse({"error": "please provide user input"}, status=400)

    except Exception as e:
        logging.exception(e)
        return JsonResponse({"error": "failure occurred because {e}"}, status=500)


def chatbot_create(request, id):
    return render(request, 'index.html', context={"widget_id": id})


from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def get_bot_names(request):
    bot_type = request.GET.get('bot_type')
    bots = []
    if bot_type == 'discord':
        bots = DiscordBotConfig.objects.all().only('id', 'chatbot_name')
    elif bot_type == 'telegram':
        bots = TelegramBotConfig.objects.all().only('id', 'chatbot_name')
    elif bot_type == 'webbot':
        bots = ChatBot.objects.all().only('id', 'chatbot_name')
    elif bot_type == 'whatsapp':
        bots = WhatsAppBotConfig.objects.all().only('id', 'chatbot_name')
    else:
        return JsonResponse({'error': 'Invalid bot type'}, status=400)

    bot_list = [{'id': bot.id, 'name': bot.chatbot_name} for bot in bots]
    return JsonResponse({'bots': bot_list})


def get_table_choices(request, database_id):
    database = get_object_or_404(OdooDatabase, pk=database_id)
    uid = authenticate_odoo(database.db_url, database.db_name, database.username, database.password)
    table_choices = get_odoo_tables(database.db_url, database.db_name, uid, database.password)
    return JsonResponse({'choices': table_choices})

def get_field_choices(request, table_name, database_id):
    database = get_object_or_404(OdooDatabase, pk=database_id)
    uid = authenticate_odoo(database.db_url, database.db_name, database.username, database.password)
    table_choices = get_odoo_table_fields(database.db_url, database.db_name, uid, database.password, table_name)
    return JsonResponse({'choices': table_choices})

## Here is the new APIs

def get_required_odoo_fields(requested_id):
    response_dict = {}
    get_param = get_object_or_404(OdooFields, pk=requested_id)
    response_dict["id"] = get_param.id
    response_dict["database_name"] = get_param.database_name.db_name
    response_dict["database_url"] = get_param.database_name.db_url
    response_dict["database_table"] = get_param.database_table
    response_dict["database_username"] = get_param.database_name.username
    response_dict["database_password"] = get_param.database_name.password
    response_dict["type"] = get_param.type

    # Fetch related OdooTableField instances
    table_fields = OdooTableField.objects.filter(odoo_field=get_param)
    table_fields_list = []
    for table_field in table_fields:
        table_fields_list.append(table_field.field_name)
    
    response_dict["table_fields"] = table_fields_list
    return response_dict


@authorize
def get_odoo_field_data(request):
    requested_id = request.GET.get('id')
    return JsonResponse(get_required_odoo_fields(requested_id))


@authorize
def read_odoo_api(request):
    requested_id = request.GET.get('id')
    user_input = request.GET.get('user_input')

    field_details = get_required_odoo_fields(requested_id)
    # bot_name = chatbot.chatbot_name
    # if chatbot.state == "paused":
    #     return JsonResponse({"error": "Bot has been stopped."}, status=400)
    print(user_input)

    try:
        resp = {}
        product_data = []
        if user_input:
            agent_response = main(user_input, os.environ.get("OPENAI_KEY"), field_details)

            for product in agent_response:
                resp = {key: product.get(key) for key in field_details.get("table_fields")}
                
                product_data.append(resp.copy())
                resp = {}

            return JsonResponse({"data": product_data}, status=200)
        else:
            return JsonResponse({"error": "please provide user input"}, status=400)

    except Exception as e:
        logging.exception(e)
        return JsonResponse({"error": "failure occurred because {e}"}, status=500)
