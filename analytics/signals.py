from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import AanlyticsSchedule, SaveAnalytic
from .google_job import SERVER_URL, GCP_SCHEDULER_JOB_PARENT, AUTH_TOKEN
import google.auth
from google.cloud import scheduler_v1
from .models import AanlyticsSchedule
from django.utils import timezone
from google.protobuf import field_mask_pb2
from google.cloud.scheduler_v1 import Job


def get_update_job_payload(instance: AanlyticsSchedule, body, job_name):
    return Job(
        name=job_name,
        time_zone='UTC',
        schedule=f'every {instance.output_plan} hours',
    )

def create_job_payload(instance: AanlyticsSchedule, body, job_name):
    return {
        'name': job_name,
        'schedule': f'every {instance.output_plan} hours',
        'time_zone': 'UTC',
        'http_target': {
            'uri': f'{SERVER_URL}/api/execute-batch-container',
            'http_method': scheduler_v1.HttpMethod.POST,
            'headers': {
                'Content-Type': 'application/json',
                'Authorization': AUTH_TOKEN
            },
            'body': body.encode('utf-8')
        }
    }


@receiver(post_save, sender=AanlyticsSchedule)
def send_mail_post_save(sender, instance: AanlyticsSchedule, created, **kwargs):
    """
    This signal creates or updates a Google Cloud Scheduler job that triggers a batch job to process CSV.
    """
    if hasattr(instance, '_skip_signal') and instance._skip_signal:
        return

    client, _ = google.auth.default()
    scheduler_client = scheduler_v1.CloudSchedulerClient()
    # parent = client.common_location_path(PROJECT_ID, REGION)
    job_name = f'{GCP_SCHEDULER_JOB_PARENT}/jobs/create-analytic-csv-{instance.id}'
    body = json.dumps({ 'instance_id': instance.id })

    try:
        existing_job = scheduler_client.get_job(name=job_name)
        update_mask = field_mask_pb2.FieldMask(paths=['schedule'])
        scheduler_client.update_job(
            job=get_update_job_payload(instance, body, job_name),
            update_mask=update_mask,
        )

    except Exception as e:
        job = create_job_payload(instance, body, job_name)
        scheduler_client.create_job(parent=GCP_SCHEDULER_JOB_PARENT, job=job)

    instance.next_execution = timezone.now() + timezone.timedelta(hours=int(instance.output_plan))
    # Set the flag to skip the signal
    instance._skip_signal = True
    instance.save()

    # Reset the flag after save to avoid any unintended consequences
    instance._skip_signal = False


@receiver(post_delete, sender=AanlyticsSchedule)
def delete_scheduler_job(sender, instance: AanlyticsSchedule, **kwargs):
    """
    This signal deletes the Google Cloud Scheduler job associated with the
    AanlyticsSchedule instance when it is deleted.
    """
    client, _ = google.auth.default()
    scheduler_client = scheduler_v1.CloudSchedulerClient()
    job_name = f'{GCP_SCHEDULER_JOB_PARENT}/jobs/create-analytic-csv-{instance.id}'

    try:
        # Try to get the job to see if it exists
        existing_job = scheduler_client.get_job(name=job_name)
        if existing_job:
            # Delete the existing job
            scheduler_client.delete_job(name=job_name)
            print(f"Deleted Cloud Scheduler job: {job_name}")

    except Exception as e:
        print(f"Error deleting Cloud Scheduler job: {e}")


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