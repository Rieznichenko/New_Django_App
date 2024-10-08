from .views import *
from django.urls import path
from .models import TelegramBotConfig, DiscordBotConfig
from .signals import run_bot_in_thread, run_discord_bot_in_thread,\
    generate_random_code
from Vision.views import SendMessageView, AnalyzeImage


urlpatterns = [
    path('api/ajax/get-config', ajax_get_config, name="ajax_get_config"),
    path('api/ajax/get-odoo-database-config', ajax_get_odoo_database, name="ajax_get_odoo_database"),
    path('api/webhook-whatsapp', webhook_whatsapp, name="webhook_whatsapp"),
    path('api/chatbot/details', chatbot_details, name='chatbot_details'),
    path('api/chatbot/call', call_llm_model, name="call_llm_model"),
    path('chatbot/<str:id>', chatbot_create, name="chatbot_create"),
    path('get_bot_names/', get_bot_names, name='get_bot_names'),

    # for Odoo AI
    path('api/sale/products', sale_odoo_products, name="sale_odoo_products"),
    path('get_table_choices/<int:database_id>/', get_table_choices, name='get_table_choices'),
    path('get_field_choices/<str:table_name>/<int:database_id>', get_field_choices, name='get_field_choices'),
    path('get_field_choices-relation/<int:database_id>/<int:read_id>/<int:write_id>', get_field_choices_relation, name='get_field_choices_relation'),

    # for odoo config
    path('get-read-choices/<str:config_type>/', get_read_choices, name='get_read_choices'),


    path('api/sale/products', sale_odoo_products, name="sale_odoo_products"),
    path('api/get-odoo-field-data', get_odoo_field_data, name='get_odoo_field_data'),
    path('api/read-odoo-api', read_odoo_api, name="read_odoo_api"),
    path('api/write-odoo-api', write_odoo_api, name="write_odoo_api"),

    # for vissoonn
    path('api/vision', SendMessageView.as_view(), name='send_message'),
    path('api/analyze-image', AnalyzeImage.as_view(), name='AnalyzeImage'),

    # for polling
    path('api/task/<str:task_id>/', get_task_status, name='get_task_status'),
    path('api/celery/result/<str:task_id>/', get_celery_result, name='get_celery_result'),
    path('api/stop_task/<str:task_id>/', stop_celery_task, name='stop_celery_task'),


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
