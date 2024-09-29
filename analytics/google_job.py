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
    client, credentials = google.auth.default()
    batch_client = batch_v1.BatchServiceClient()
    job_name = f'analytic-csv-job-{instance.id}'
    
    resources = batch_v1.ComputeResource()
    resources.cpu_milli = 500  # 0.5 vCPU core (500 milliseconds per CPU-second)
    resources.memory_mib = 512  # 0.5 GB (512 MiB)

    job = batch_v1.Job()
    job.name = job_name
    job.task_groups = [
        batch_v1.TaskGroup(
            task_spec=batch_v1.TaskSpec(
                compute_resource =resources,
                runnables=[
                    batch_v1.Runnable(
                        container=batch_v1.Runnable.Container(
                            image_uri=CONTAINER_IMAGE_URI,  # Replace with your container image
                            entrypoint="python3",
                            commands=["app.py", str(instance.id), instance.embedded_code]
                        )
                    )
                ],
                max_run_duration="54000s",
                max_retry_count = 0,
                environment=batch_v1.Environment(
                    variables=[{
                        "SERVER_URL": SERVER_URL,
                        "AUTH_TOKEN": AUTH_TOKEN
                    }]
                )
            )
        )
    ]
    
    # Define job scheduling details
    # job.allocation_policy = batch_v1.AllocationPolicy(
    #     instances=[
    #         batch_v1.AllocationPolicy.InstancePolicyOrTemplate(
    #             instance_template=f"projects/{PROJECT_ID}/global/instanceTemplates/{template_id}"
    #         )
    #     ]
    # )

    # Submit the Batch job
    try:
        batch_client.create_job(parent=GCP_SCHEDULER_JOB_PARENT, job=job)
    except Exception as e:
        print(f"Failed to create Batch job: {str(e)}")