import ftplib
import re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging

from analytics.models import AnalyticOutput

logger = logging.getLogger(__name__)


def start_scheduler():
    history_scheduler = BackgroundScheduler()
    now = datetime.now()

    history_scheduler.add_job(
        remove_history_files,
        trigger=IntervalTrigger(days=3, start_date=now),  # Repeat every 3 days
        id='my_job_repeated',  # Unique ID for the repeated job
        max_instances=1,
        replace_existing=True
    )

    try:
        history_scheduler.start()
        logger.info("Scheduler started successfully!")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


def remove_history_files():
    return
    # try:
    #     ftp_objects = AnalyticOutput.objects.all()
    #         # obj = AnalyticOutput.objects.get(id=ftp_object_id)
    #         # Connect to the FTP server
    #         try:
    #             session = ftplib.FTP(obj.ftp_destination_server, obj.ftp_destination_user, obj.ftp_destination_password)

    #             # Change to the desired directory on the FTP server
    #             session.cwd(obj.ftp_path)

    #             # Get list of files in the directory
    #             files = session.nlst()

    #             # Define the date pattern in the filename
    #             date_pattern = re.compile(r'(\d{8}_\d{6})\.csv')

    #             # Calculate the cutoff date
    #             cutoff_date = datetime.now() - timedelta(days=3)

    #             for filename in files:
    #                 match = date_pattern.search(filename)
    #                 if match:
    #                     file_date_str = match.group(1)
    #                     file_date = datetime.strptime(file_date_str, '%Y%m%d_%H%M%S')
    #                     if file_date < cutoff_date:
    #                         try:
    #                             session.delete(filename)
    #                         except Exception as e:
    #                             print(f"Failed to delete file {filename} {e}")
    #         except:
    #             print(f"Failed to remove files to ftp because {e}")
    #         finally:
    #             session.quit()
    # except Exception as e:
    #     print(f"Failed to remove files to ftp because {e}")
    # print('Successfully removed history files.')