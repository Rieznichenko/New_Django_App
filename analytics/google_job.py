import os
import google.auth
from google.cloud import batch_v1


SERVER_URL = os.getenv("SERVER_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
CONTAINER_IMAGE_URI = os.getenv("CONTAINER_IMAGE_URI")

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
GCP_SCHEDULER_JOB_PARENT = f'projects/{PROJECT_ID}/locations/{REGION}'


def schedule_container(instance):
    """
    This function creates a Google Cloud Batch job to process CSV generation.
    """
    batch_client = batch_v1.BatchServiceClient()
    job_name = f'analytic-csv-job-{instance.id}'
    
    resources = batch_v1.ComputeResource()
    resources.cpu_milli = 500  # 0.5 vCPU core (500 milliseconds per CPU-second)
    resources.memory_mib = 512  # 0.5 GB (512 MiB)

    task_spec = batch_v1.TaskSpec(
        compute_resource=resources,
        runnables=[
            batch_v1.Runnable(
                container=batch_v1.Runnable.Container(
                    image_uri="us-central1-docker.pkg.dev/quixotic-elf-198705/analytic-job-scheduler/batch-app:latest",  # Replace with your container image
                    # entrypoint="python",  # Main executable
                    commands=["python", "app.py", str(instance.id), instance.embedded_code]  #Arguments passed to your app.py
                )
            )
        ],
        max_run_duration="54000s",  # Max run time of 15 hours
        max_retry_count=0,  # No retries
    )

    task_spec.environment.variables["SERVER_URL"] = SERVER_URL
    task_spec.environment.variables["AUTH_TOKEN"] = AUTH_TOKEN

    task_group = batch_v1.TaskGroup(task_spec=task_spec)

    # Define the job with the task group
    job = batch_v1.Job(
        name=job_name,
        task_groups=[task_group]
    )

    job.logs_policy = batch_v1.LogsPolicy(
        destination=batch_v1.LogsPolicy.Destination.CLOUD_LOGGING
    )

    # Submit the Batch job
    try:
        parent = f"projects/{PROJECT_ID}/locations/{REGION}"
        batch_client.create_job(parent=parent, job=job)
    except Exception as e:
        print(f"Failed to create Batch job: {str(e)}")