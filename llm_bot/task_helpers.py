import os
from django.conf import settings
from file_dump_store import dump_file_to_ftp
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from analytics.models import AnalyticHistory




def create(schedule_name, file_name):
    AnalyticHistory.objects.create(
        schedule_name=schedule_name,
        file_name=file_name
    )


def upload_csv(file_name, output_detail):
    with open(file_name, 'rb') as f:
        file_content = f.read()

    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    path = default_storage.save(file_path, ContentFile(file_content))
    dump_file_to_ftp(output_detail, file_path)

    os.remove(path=file_name)
    return {"file_path": path}