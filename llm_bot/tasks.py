from datetime import datetime, timedelta
import time
from mailersend import emails
from .models import ChatBotMessage
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


api_key = "mlsn.2154de4397d32c740ac01986421919204147fe243ec614683192c4d8fd1adabe"


def generate_html_content(messages):
    message_row = []
    for message in messages:
        message_row.append({
            "Content": message.content,
            "Author": message.author,
            "Timestamp":message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return message_row

def send_mail_for_bot(email, messages, platform_name, bot_name = None):
    table_rows = generate_html_content(messages)
    total_messages = len(messages)
    
    api_key = "mlsn.2154de4397d32c740ac01986421919204147fe243ec614683192c4d8fd1adabe"

    mailer = emails.NewEmail(api_key)
    mail_body = {}

    mail_from = {
        "name": "test",
        "email": "MS_VwinvN@trial-7dnvo4dzykxl5r86.mlsender.net",
    }

    recipients = [
        {
            "name": "testemail",
            "email": email,
        }
    ]

    personalization = [
        {
            "email": email,
            "data": {
                "bot_name": bot_name,
                "bot_type": platform_name,
                "messages_row": table_rows,
                "total_messages": total_messages
            }
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(f"Notification for {platform_name}", mail_body)
    mailer.set_template("jy7zpl9mpjog5vx6", mail_body)
    mailer.set_advanced_personalization(personalization, mail_body)

    response = mailer.send(mail_body)
    print("email response", response)
    return response

@shared_task
def send_mail(email, hour, bot_type, bot_name, state):
    logger.info("Detials ***********", email, hour, bot_type, bot_name, state)
    if state == "paused":
        logger.info("Schedule is paused")
        return
    
    required_hours = datetime.now() - timedelta(hours=hour)
    logger.info(email, hour, "wtfffffffffffff")
    # whatsapp_messages = WhatsAppMessage.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    # discord_messages = DiscordMessage.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    # telegram_messages = TelegramMessage.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    # chat_bot_messages = ChatBotMessage.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')

    # whatsapp_messages = WhatsAppMessage.objects.all().order_by('timestamp')
    # discord_messages = DiscordMessage.objects.all().order_by('timestamp')
    # telegram_messages = TelegramMessage.objects.all().order_by('timestamp')
    one_hour_ago = timezone.now() - timedelta(hours=int(hour))
    chat_bot_messages = ChatBotMessage.objects.filter(timestamp__gte=one_hour_ago, bot_type = bot_type, chatbot_name = bot_name).order_by('timestamp')

    all_messages = []

    if bot_type == "discord":
        all_messages.append((chat_bot_messages, 'Discord'))
    if bot_type == "telegram":
        all_messages.append((chat_bot_messages, 'Telegram'))
    if bot_type == "webbot":
        all_messages.append((chat_bot_messages, 'ChatBot'))
    if bot_type == "whatsapp":
        all_messages.append((chat_bot_messages, 'WhatsApp'))

    logger.info("all_messages", all_messages)
    for messages, platform_name in all_messages:
        if len(messages) > 0:
            response=send_mail_for_bot(email, messages, platform_name, bot_name)
            logger("NICE")