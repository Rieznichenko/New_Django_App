import ftplib
import re
from datetime import datetime, timedelta
from analytics.models import AnalyticOutput
import paramiko


def dump_file_to_ftp(ftp_object_id, local_file_path):
    try:
        obj = AnalyticOutput.objects.get(id = ftp_object_id)
        print(f"Retrieved ftp object is : {obj}")
        print(f"local file path {local_file_path}")
        # Initialize SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the SFTP server
        ssh_client.connect(hostname=obj.ftp_destination_server, port=obj.ftp_destination_port, username=obj.ftp_destination_user, password=obj.ftp_destination_password)
        
        # Open SFTP session
        sftp_client = ssh_client.open_sftp()
        
        # Change to the desired directory on the SFTP server
        sftp_client.chdir(obj.ftp_path)
        
        # Upload the file to the SFTP server
        remote_file_name = local_file_path.split('/')[-1]
        print(f"remote_file_name {remote_file_name}, {obj.ftp_path}")
        sftp_client.put(local_file_path, f'{obj.ftp_path}/{remote_file_name}')
        
        print("File uploaded successfully to SFTP")
        
        # Close the SFTP connection
        sftp_client.close()
        ssh_client.close()
        
    except Exception as e:
        if sftp_client:
            try:
                sftp_client.close()
                print("SFTP client closed successfully")
            except Exception as e:
                print(f"Error closing SFTP client: {e}")
        
        if ssh_client:
            try:
                ssh_client.close()
                print("SSH client closed successfully")
            except Exception as e:
                print(f"Error closing SSH client: {e}")

