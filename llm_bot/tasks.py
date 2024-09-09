from datetime import datetime, timedelta
import time
from mailersend import emails
from .models import ChatBotMessage
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from dotenv import load_dotenv
import os
from analytics.models import AanlyticsSchedule, SaveAnalytic
from odoo.odoo_utils import fetch_product_details
from io import StringIO
import sys


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

load_dotenv()

api_key = os.environ.get("API_KEY")


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
    platform_name = "WebBot" if platform_name == "ChatBot" else platform_name
    table_rows = generate_html_content(messages)
    total_messages = len(messages)
    
    api_key = os.environ.get("API_KEY")

    mailer = emails.NewEmail(api_key)
    mail_body = {}

    mail_from = {
        "name": "test",
        "email": os.environ.get("MAIL_USER"),
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
    mailer.set_template(os.environ.get("TEMPLATE_ID"), mail_body)
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

    for messages, platform_name in all_messages:
        if len(messages) > 0:
            response = send_mail_for_bot(email, messages, platform_name, bot_name)
            logger.info("Mail sent")

@shared_task
def create_analytic_csv(schedule_name, output_plan, instance_id, output_detail, python_code):
    logger.info("Detials ***********", schedule_name, output_plan, instance_id, output_detail)

    get_schedule_details = AanlyticsSchedule.objects.get(id = instance_id)

    db_url = get_schedule_details.select_database.db_url
    db_name = get_schedule_details.select_database.db_name
    username = get_schedule_details.select_database.username
    password = get_schedule_details.select_database.password

    local_vars = {
        "db_url": db_url,
        "db_name": db_name,
        "username": username,
        "password": password,
        "schedule_name": schedule_name,
        "output_detail": output_detail,
    }

    exec(get_schedule_details.embedded_code, globals(), local_vars)


@shared_task
def process_analytic_save(instance_id, code):
    try:
        # Retrieve the schedule details
        get_schedule_details = SaveAnalytic.objects.get(id=instance_id)

        # Extract related models
        analytic_output = get_schedule_details.analytic_output
        odoo_database = get_schedule_details.select_database

        # Set up local variables for dynamic execution
        local_vars = {
            "sftp_hostname": analytic_output.ftp_destination_server,
            "sftp_port": int(analytic_output.ftp_destination_port),  # Convert to integer
            "sftp_username": analytic_output.ftp_destination_user,
            "sftp_password": analytic_output.ftp_destination_password,
            # Local directory and file paths
            "local_dir_path": "/Users/apple/Documents/projects/gpt_discord/ftp",  # Path to save the file
            # Odoo credentials
            "odoo_url": odoo_database.db_url,
            "odoo_db": odoo_database.db_name,
            "odoo_user": odoo_database.username,
            "odoo_password": odoo_database.password,
        }

        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        try:
            # Execute the provided code with dynamic variables
            exec(code, globals(), local_vars)

            # Capture the output of the execution (if it uses print)
            exec_output = redirected_output.getvalue()

            # Extract result from local_vars
            result = local_vars.get("file_path")  # Change 'file_path' to any variable name that is expected

            print(f"Execution output: {exec_output}")  # Debugging: Print what was captured
            print(f"Local variables after execution: {local_vars}")  # Debugging: Print local_vars

            return result, exec_output
        except Exception as exec_error:
            # Handle any execution errors
            print(f"Execution error: {exec_error}")
            return None, str(exec_error)
        finally:
            # Restore the original stdout
            sys.stdout = old_stdout

    except Exception as e:
        # Handle errors in retrieving schedule details
        print(f"Error retrieving schedule details: {e}")
        return None, str(e)



@shared_task
def process_csv_generation(instance_id, code):
    # Fetch the schedule details
    get_schedule_details = AanlyticsSchedule.objects.get(id=instance_id)

    # Set up local variables for dynamic execution
    local_vars = {
        "db_url": get_schedule_details.select_database.db_url,
        "db_name": get_schedule_details.select_database.db_name,
        "username": get_schedule_details.select_database.username,
        "password": get_schedule_details.select_database.password,
        "output_detail": get_schedule_details.output_detail.id,
        "schedule_name": get_schedule_details.schedule_name
    }

    # Execute the custom code with dynamic variables
    old_stdout = sys.stdout
    redirected_output = StringIO()

    try:
        sys.stdout = redirected_output

        # Use `exec` to execute the provided code
        exec(code, globals(), local_vars)

        # Capture the output of the execution (if it uses print)
        exec_output = redirected_output.getvalue()

        # If there is a specific result to return from the code, ensure it's in local_vars
        # For example, if `file_path` is expected to be generated in the code
        result = local_vars.get("file_path")  # Change 'file_path' to any variable name that is expected

        return result, exec_output
    except Exception as e:
        print(str(e))
        # Handle any execution errors
        return None, str(e)
    finally:
        # Restore the original stdout
        sys.stdout = old_stdout
