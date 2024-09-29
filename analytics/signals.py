from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import AanlyticsSchedule, SaveAnalytic
from .google_job import SERVER_URL, GCP_SCHEDULER_JOB_PARENT, schedule_container
import google.auth
from google.cloud import scheduler_v1
from .models import AanlyticsSchedule
from django.utils import timezone


@receiver(post_save, sender=AanlyticsSchedule)
def send_mail_post_save(sender, instance: AanlyticsSchedule, created, **kwargs):
    """
    This signal creates or updates a Google Cloud Scheduler job that triggers a batch job to process CSV.
    """
    if instance.is_running or (instance.next_execution and instance.next_execution > timezone.now()):
        # this is request from batch job
        return True

    client, _ = google.auth.default()
    scheduler_client = scheduler_v1.CloudSchedulerClient()
    # parent = client.common_location_path(PROJECT_ID, REGION)
    job_name = f'{GCP_SCHEDULER_JOB_PARENT}/jobs/create-analytic-csv-{instance.id}'

    # Create HTTP target or Pub/Sub for your Batch Job
    body = json.dumps({ 'instance_id': instance.id })

    job = {
        'name': job_name,
        'schedule': f'every {instance.output_plan} hours',
        'time_zone': 'UTC',
        'http_target': {
            'uri': f'{SERVER_URL}/api/execute-batch-container',
            'http_method': scheduler_v1.HttpMethod.POST,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': body.encode('utf-8')
        },
    }

    # Update or create job
    try:
        existing_job = scheduler_client.get_job(name=job_name)
        scheduler_client.update_job(job=job)

    except Exception as e:
        ...
        # scheduler_client.create_job(parent=GCP_SCHEDULER_JOB_PARENT, job=job)

    instance.next_execution = timezone.now() + timezone.timedelta(hours=int(instance.output_plan))
    instance.save()

    #this needs to be removed on dev, currently this is for testing only
    schedule_container(instance)


@receiver(post_save, sender=SaveAnalytic)
def send_mail_post_save_a(sender, instance: SaveAnalytic, created, **kwargs):
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=instance.output_plan,
        period=IntervalSchedule.HOURS,
    )

    task_name = f'Create Genneration {instance.id}'
    task_args = json.dumps([instance.id, instance.embedded_code])

    if instance.periodic_task:
        instance.periodic_task.interval = schedule
        instance.periodic_task.name = task_name
        instance.periodic_task.args = task_args
        instance.periodic_task.save()
    else:
        task = PeriodicTask.objects.create(
            interval=schedule,
            name=task_name,
            task='llm_bot.tasks.process_analytic_save',
            args=task_args,
        )
        instance.periodic_task = task
        instance.save()