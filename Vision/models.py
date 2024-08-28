from django.db import models

# Create your models here.


class VisionApplication(models.Model):
    application_name = models.CharField(max_length=200, null=True, blank=True)
    telegram_bot_id = models.CharField(max_length=200, null=True, blank=True)
    application_id = models.CharField(max_length=200, null=True, blank=True)
    unique_token = models.CharField(max_length=200, null=True, blank=True)


    class Meta:
        verbose_name = "Vision Application"
        verbose_name_plural = "Vision Application"

    def __str__(self) -> str:
        return self.application_name
    



class ApplicationUser(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    vision_application = models.ForeignKey(VisionApplication, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Application User"
        verbose_name_plural = "Application User"

    def __str__(self) -> str:
        return self.name

