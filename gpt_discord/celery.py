import logging
import os
from celery import Celery
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gpt_discord.settings')

app = Celery('gpt_discord')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
