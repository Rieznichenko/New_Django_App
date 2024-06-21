from typing import Iterable
from django.db import models



class OdooDatabase(models.Model):
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
        return self.db_name or "he"
    
    class Meta:
        verbose_name = "Database"
        verbose_name_plural = "Database"
    

class Test(models.Model):
    field=models.CharField(max_length=103, blank=True, null=True)




class OdooFields(models.Model):
    database_name = models.ForeignKey(OdooDatabase, on_delete=models.CASCADE)
    database_table = models.CharField(max_length=100,default = '')
    TYPE_CHOICES = (
        ('read', 'Read'),
        ('write', 'Write'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default = '', blank = True, null = True)


    def __str__(self):
        return f"{self.database_name} - {self.database_table}"

    class Meta:
        verbose_name = "Odoo Field"
        verbose_name_plural = "Odoo Fields"

    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        return super().save()


class OdooTableField(models.Model):
    odoo_field = models.ForeignKey(OdooFields, on_delete = models.CASCADE, default='', null=True, blank=True)
    field_name = models.CharField(max_length = 100, default = '', blank = True, null = True)


    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        return super().save()
    
    class Meta:
        verbose_name = 'Select table field'