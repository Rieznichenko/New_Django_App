import schedule
from .views import *
from django.urls import path
from .models import TelegramBotConfig, DiscordBotConfig
from .signals import run_bot_in_thread, run_discord_bot_in_thread, generate_random_code

urlpatterns = [
    path('api/ajax/get-config', ajax_get_config, name="ajax_get_config"),
    path('api/webhook-whatsapp', webhook_whatsapp, name="webhook_whatsapp"),
    path('api/chatbot/details', chatbot_details, name='chatbot_details'),
    path('api/chatbot/call', call_llm_model, name="call_llm_model"),
    path('chatbot/<str:id>', chatbot_create, name="chatbot_create"),
    path('get_bot_names/', get_bot_names, name='get_bot_names'),
]

def start_bot_thread(instance, caller_function):
    try:
        caller_function(instance)
    except Exception as e:
        print(f'bot thread starting failed because {e}')


def start_required_threads():
    [start_bot_thread(bot, run_discord_bot_in_thread) for bot in DiscordBotConfig.objects.all()]
    [start_bot_thread(bot, run_bot_in_thread) for bot in TelegramBotConfig.objects.all()]


if 'runserver' in os.getenv('DJANGO_COMMAND', ''):
    print("oh yeahh")
    start_required_threads()
