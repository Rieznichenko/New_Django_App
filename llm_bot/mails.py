from datetime import timedelta
import threading
from mailersend import emails
from sched import scheduler
api_key = "mlsn.5e095ba5f2b2fdc2458c01ead42212b15d07216ba7e882b32dffeb7c41022833"

mailer = emails.NewEmail(api_key)
# define an empty dict to populate with mail values
mail_body = {}

def send_mail():

    mail_from = {
        "name": "Humany",
        "email": "MS_xRqMgk@trial-neqvygme1dd40p7w.mlsender.net",
    }

    recipients = [
        {
            "name": "testemail",
            "email": "rtksoni00@gmail.com",
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Hello!", mail_body)
    mailer.set_html_content("This is the HTML content", mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)

    # using print() will also return status code and data
    print(mailer.send(mail_body))

