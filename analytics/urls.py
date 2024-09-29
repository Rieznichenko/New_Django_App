from .views import *
from django.urls import path


urlpatterns = [
    # endpoints for batch
    path('api/upload-csv', upload_csv_view, name="upload_csv_view"),
    path('api/create-analytic-history', create_analytic_history_view, name="create_analytic_history_view"),
    path('api/save-analytic-schedule', get_analytic_schedule_view, name="get_analytic_schedule_view"),
    path('api/update-analytic-schedule', update_analytic_schedule_view, name="update_analytic_schedule_view"),
    path('api/execute-batch-container', execute_batch_container, name="execute_batch_container")
]