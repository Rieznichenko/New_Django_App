from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import EmailSchedule, TelegramBotConfig, DiscordBotConfig
from telegram_bot import run_telegram_bot
from discord_bot import run_discord_bot
import threading
import json
import random
from multiprocessing import Process


def setup_thread_store(telegram_bot_id, thread_id):
    with open("bot_thread_store/telegram_store.json", 'r') as file:
        data = json.load(file)

    data[str(telegram_bot_id)] = str(thread_id)
    with open("bot_thread_store/telegram_store.json", 'w') as file:
        json.dump(data, file, indent=4)

    return True

def get_thread_detail(telegram_bot_id):
    with open("bot_thread_store/telegram_store.json", 'r') as file:
        data = json.load(file)

    print("Jso data", data)
    get_thread = data.get(str(telegram_bot_id), None)
    print("Thread store get", get_thread)
    return get_thread

def generate_random_code():
    code = ''.join([str(random.randint(0, 9)) for _ in range(20)])
    return code


def run_bot_in_thread(instance):
    telegram_bot_token = instance.telegram_bot_token
    assistant_id = instance.telegram_llm_agent.assistant_id
    api_key = instance.telegram_llm_agent.llm_config.llmconfig.api_key
    args = (api_key, assistant_id, telegram_bot_token, instance.bot_thread_id)
    thread = threading.Thread(target=run_telegram_bot, args=args, name="wassup")
    thread.start()
    thread_id = thread.ident
    # setup_thread_store(instance.id, thread_id)
    return True


def run_discord_bot_in_thread(instance: DiscordBotConfig):    
    discord_bot_token = instance.discord_bot_token
    assistant_id = instance.discord_llm_agent.assistant_id
    api_key = instance.discord_llm_agent.llm_config.llmconfig.api_key
    args = (api_key, assistant_id, discord_bot_token, instance.bot_thread_id)
    thread = Process(target=run_discord_bot, args=args, name=f"discord_bot-{instance.bot_thread_id}")
    thread.start()
    return True

@receiver(post_save, sender=TelegramBotConfig)
def telegram_bot_config_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for post-save on TelegramBotConfig.
    """
    if created:
        random_code = generate_random_code()
        instance.bot_thread_id = random_code
        instance.save()
        run_bot_in_thread(instance)
        print("Post save")
    else:
        print("In update")

@receiver(post_delete, sender=TelegramBotConfig)
def telegram_bot_config_post_delete(sender, instance, **kwargs):
    """
    Signal handler for post-delete on TelegramBotConfig.
    """
    # Handle post-delete logic
    print("Post delete")



@receiver(post_save, sender=DiscordBotConfig)
def discord_bot_config_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for post-save on TelegramBotConfig.
    """
    if created:
        random_code = generate_random_code()
        instance.bot_thread_id = random_code
        instance.save()
        run_discord_bot_in_thread(instance)
        print("Post save")
    else:
        print("In update")

from django_celery_beat.models import PeriodicTask, IntervalSchedule


@receiver(post_save, sender=EmailSchedule)
def send_mail_post_save(sender, instance: EmailSchedule, created, **kwargs):
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=instance.frequency_hour,
        period=IntervalSchedule.HOURS,
    )

    task_name = f'send_mail_to_{instance.recipient}_{instance.id}'
    task_args = json.dumps([instance.recipient, instance.frequency_hour, instance.bot_type, instance.bot_name.chatbot_name, instance.state])

    if instance.periodic_task:
        instance.periodic_task.interval = schedule
        instance.periodic_task.name = task_name
        instance.periodic_task.args = task_args
        instance.periodic_task.save()
    else:
        task = PeriodicTask.objects.create(
            interval=schedule,
            name=task_name,
            task='llm_bot.tasks.send_mail',
            args=task_args,
        )
        instance.periodic_task = task
        instance.save()