from django.db import models
from django_celery_beat.models import PeriodicTask

# Create your models here.
class OdooDatabase(models.Model):
    connection_name = models.CharField(max_length=100, blank=True, null=True)
    AUTH_MODE_CHOICES = [
        ('credentials', 'Credentials'),
        ('api_key', 'API Key'),
    ]

    db_url = models.URLField(verbose_name='Database URL', blank=True, null=True)
    db_name = models.CharField(max_length=100, verbose_name='Database Name', blank=True, null=True)
    auth_mode = models.CharField(max_length=20, choices=AUTH_MODE_CHOICES, verbose_name='Select authentication mode', blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name='Username')
    password = models.CharField(max_length=100, blank=True, null=True, verbose_name='Password')
    api_key = models.CharField(max_length=100, blank=True, null=True, verbose_name='API Key')

    def __str__(self) -> str:
        return self.connection_name or self.db_name
    
    class Meta:
        verbose_name = "Database Configuration"
        verbose_name_plural = "Database Configuration"




class AnalyticHistory(models.Model):
    schedule_name = models.CharField(max_length=100, verbose_name='Schedule Name', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    file_name = models.CharField(max_length=100, verbose_name='File name', blank=True, null=True)

    # def __str__(self) -> str:
    #     return self.schedule_name
    
    class Meta:
        verbose_name = "Analytics Schedule History"
        verbose_name_plural = "Analytics Schedule History"


class AnalyticOutput(models.Model):
    connection_name = models.CharField(max_length=100, verbose_name='Connection Name', blank=True, null=True)
    ftp_path = models.CharField(max_length=100, blank=True, null=True)
    ftp_destination_server = models.CharField(max_length=100, blank=True, null=True)
    ftp_destination_user = models.CharField(max_length=100, blank=True, null=True)
    ftp_destination_password = models.CharField(max_length=100, blank=True, null=True)
    ftp_destination_port = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Analytics Output Coonnection"
        verbose_name_plural = "Analytics Output Coonnection"

    def __str__(self) -> str:
        return self.connection_name


class AanlyticsSchedule(models.Model):
    schedule_name = models.CharField(max_length=100, verbose_name='Schedule Name', blank=True, null=True)
    select_database = models.ForeignKey(OdooDatabase, on_delete=models.CASCADE)
    output_plan = models.IntegerField(help_text="Please input output plan in hours")
    periodic_task = models.OneToOneField(PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL)
    embedded_code = models.TextField(blank=True, null=True)
    output_detail = models.ForeignKey(AnalyticOutput, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.schedule_name
    
    class Meta:
        verbose_name = "Analytics Generate Schedule"
        verbose_name_plural = "Analytics Generate Schedule"


class SaveAnalytic(models.Model):
    analytic_name = models.CharField(max_length=100, verbose_name='Name', blank=True, null=True)
    analytic_output = models.ForeignKey(AnalyticOutput, on_delete=models.CASCADE, blank=True, null=True)
    select_database = models.ForeignKey(OdooDatabase, on_delete=models.CASCADE)
    embedded_code = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.analytic_name
    
    class Meta:
        verbose_name = "Save Analytic"
        verbose_name_plural = "Save Analytic"