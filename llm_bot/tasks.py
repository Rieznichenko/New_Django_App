import base64
import csv
from io import StringIO
from datetime import timedelta
import uuid
from mailersend import emails
from django.utils import timezone
from urd import schedulable_task
from .models import WhatsAppMessage, DiscordMessage, TelegramMessage

api_key = "mlsn.5e095ba5f2b2fdc2458c01ead42212b15d07216ba7e882b32dffeb7c41022833"
mailer = emails.NewEmail(api_key)

@schedulable_task
def send_mail(heartbeat):
    # Fetch all messages from each platform
    whatsapp_messages = WhatsAppMessage.objects.all().order_by('timestamp')
    discord_messages = DiscordMessage.objects.all().order_by('timestamp')
    telegram_messages = TelegramMessage.objects.all().order_by('timestamp')

    # Use StringIO to handle CSV in memory
    csv_buffer = StringIO()
    fieldnames = ['Platform', 'Content', 'Author', 'Timestamp']
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    
    writer.writeheader()

    # Write messages from each platform
    for message in whatsapp_messages:
        writer.writerow({
            'Platform': 'WhatsApp',
            'Content': message.content,
            'Author': message.author,
            'Timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        heartbeat()  # Call heartbeat for each message
    
    for message in discord_messages:
        writer.writerow({
            'Platform': 'Discord',
            'Content': message.content,
            'Author': message.author,
            'Timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        heartbeat()  # Call heartbeat for each message

    for message in telegram_messages:
        writer.writerow({
            'Platform': 'Telegram',
            'Content': message.content,
            'Author': message.author,
            'Timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        heartbeat()  # Call heartbeat for each message
    

    # Email setup and sending
    mail_body = {}
    mail_from = {"name": "Humany", "email": "MS_xRqMgk@trial-neqvygme1dd40p7w.mlsender.net"}
    recipients = [{"name": "testemail", "email": "rtksoni00@gmail.com"}]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("All Platform Messages CSV", mail_body)

    # Calculate some basic stats for the email body
    total_messages = len(whatsapp_messages) + len(discord_messages) + len(telegram_messages)
    html_content = f"""
    <p>Please find attached the CSV file with messages from WhatsApp, Discord, and Telegram.</p>
    <p>Summary:</p>
    <ul>
        <li>Total Messages: {total_messages}</li>
        <li>WhatsApp: {len(whatsapp_messages)}</li>
        <li>Discord: {len(discord_messages)}</li>
        <li>Telegram: {len(telegram_messages)}</li>
    </ul>
    """

    plain_content = f"""
    Please find attached the CSV file with messages from WhatsApp, Discord, and Telegram.

    Summary:
    - Total Messages: {total_messages}
    - WhatsApp: {len(whatsapp_messages)}
    - Discord: {len(discord_messages)}
    - Telegram: {len(telegram_messages)}
    """

    mailer.set_html_content(html_content, mail_body)
    mailer.set_plaintext_content(plain_content, mail_body)

    
    
    csv_content = csv_buffer.getvalue()

    csv_bytes = csv_content.encode('utf-8')
    csv_base64 = base64.b64encode(csv_bytes)
    csv_base64_str = csv_base64.decode('ascii')
    print(csv_base64_str)

    attachment = [{
        "content": csv_base64_str,
        "filename": "all_platform_messages.csv",
        "disposition": "attachment",
        "id": "csv-01",
    }]
    mailer.set_attachments(attachment, mail_body)

    heartbeat()  # Call heartbeat before sending the email

    # Send the email and handle response
    response = mailer.send(mail_body)

    return response