from .views import *
from django.urls import path

urlpatterns = [
    path('/ajax/get-config', ajax_get_config, name="ajax_get_config"),
]
