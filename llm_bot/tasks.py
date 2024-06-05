from datetime import datetime, timedelta
import time
from mailersend import emails
from .models import ChatBotMessage
from celery import shared_task

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


api_key = "mlsn.0521cea73d9c4bccd3445809899bb66d795c7e5d8d609a0ad141e2ecce645de6"


def generate_html_content(messages):
    message_row = []
    for message in messages:
        message_row.append({
            "Content": message.content,
            "Author": message.author,
            "Timestamp":message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return message_row

def send_mail_for_bot(email, messages, platform_name):
    table_rows = generate_html_content(messages)
    total_messages = len(messages)
    
    api_key = "mlsn.0521cea73d9c4bccd3445809899bb66d795c7e5d8d609a0ad141e2ecce645de6"

    mailer = emails.NewEmail(api_key)
    mail_body = {}

    mail_from = {
        "name": "test",
        "email": "MS_vB2uCK@trial-v69oxl5o9pzg785k.mlsender.net",
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
                "bot_name": platform_name,
                "messages_row": table_rows,
                "total_messages": total_messages
            }
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(f"Notification for {platform_name}", mail_body)
    mailer.set_template("3z0vklo032xl7qrx", mail_body)
    mailer.set_advanced_personalization(personalization, mail_body)

    response = mailer.send(mail_body)
    print("email response", response)
    return response

@shared_task
def send_mail(email, hour):
    one_hour_ago = datetime.now() - timedelta(hours=hour)
    logger.info(email, hour, "wtfffffffffffff")
    # whatsapp_messages = WhatsAppMessage.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    # discord_messages = DiscordMessage.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    # telegram_messages = TelegramMessage.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    # chat_bot_messages = ChatBotMessage.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')

    # whatsapp_messages = WhatsAppMessage.objects.all().order_by('timestamp')
    # discord_messages = DiscordMessage.objects.all().order_by('timestamp')
    # telegram_messages = TelegramMessage.objects.all().order_by('timestamp')
    chat_bot_messages = ChatBotMessage.objects.all().order_by('timestamp')
    all_messages = [
        (chat_bot_messages, 'WhatsApp'),
        (chat_bot_messages, 'Discord'),
        (chat_bot_messages, 'Telegram'),
        (chat_bot_messages, 'ChatBot')
    ]

    for messages, platform_name in all_messages:
        if len(messages) > 0:
            response=send_mail_for_bot(email, messages, platform_name)
            print("NICE",response)