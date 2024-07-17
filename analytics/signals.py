from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import AanlyticsSchedule


@receiver(post_save, sender=AanlyticsSchedule)
def send_mail_post_save(sender, instance: AanlyticsSchedule, created, **kwargs):
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=instance.output_plan,
        period=IntervalSchedule.SECONDS,
    )
    print("HEy", schedule)

    task_name = f'Create anaalytic CSV {instance.schedule_name}_{instance.id}'
    task_args = json.dumps([instance.schedule_name, instance.output_plan, instance.id])

    if instance.periodic_task:
        instance.periodic_task.interval = schedule
        instance.periodic_task.name = task_name
        instance.periodic_task.args = task_args
        instance.periodic_task.save()
    else:
        task = PeriodicTask.objects.create(
            interval=schedule,
            name=task_name,
            task='llm_bot.tasks.create_analytic_csv',
            args=task_args,
        )
        instance.periodic_task = task
        instance.save()