import ftplib
import re
from datetime import datetime, timedelta
from analytics.models import AnalyticOutput


def dump_file_to_ftp(ftp_object_id, local_file_path):
    obj = AnalyticOutput.objects.get(id = ftp_object_id)
    try:
        # Connect to the FTP server
        session = ftplib.FTP(obj.ftp_destination_server, obj.ftp_destination_user, obj.ftp_destination_password)
        
        # Change to the desired directory on the FTP server
        session.cwd(obj.ftp_path)
        
        # Open the local CSV file to be uploaded
        with open(local_file_path, 'rb') as file:
            # Store the file on the FTP server
            session.storbinary(f'STOR {local_file_path.split("/")[-1]}', file)
        
        print("File uploaded successfully")
        
    except Exception as e:
        print(f"Failed to dump file to ftp because {e}")

