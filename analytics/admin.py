# admin.py

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from . import views
from .models import OdooDatabase, AanlyticsSchedule, AnalyticHistory, AnalyticOutput, SaveAnalytic
from llm_bot.admin import admin_site
from django.http import HttpResponse
from django.conf import settings
import os
from django.urls import reverse, path


# Register your models here.
class OdooDatabaseForm(forms.ModelForm):
    class Meta:
        model = OdooDatabase
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(OdooDatabaseForm, self).__init__(*args, **kwargs)
        self.fields['auth_mode'].widget.attrs.update({'onchange': 'toggleFields(this)'})
        self.fields['username'].widget.attrs.update({'style': 'display:none'})
        self.fields['password'].widget.attrs.update({'style': 'display:none'})
        self.fields['api_key'].widget.attrs.update({'style': 'display:none'})

        if self.instance and self.instance.auth_mode == 'credentials':
            self.fields['username'].widget.attrs.update({'style': 'display:block'})
            self.fields['password'].widget.attrs.update({'style': 'display:block'})
        elif self.instance and self.instance.auth_mode == 'api_key':
            self.fields['api_key'].widget.attrs.update({'style': 'display:block'})

class OdooDatabaseAdmin(admin.ModelAdmin):
    form = OdooDatabaseForm

    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 4px 6px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: #ff0000; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            delete_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/delete/'
            delete_button = format_html(
                '<a href="{0}" class="button" style="{1}">Delete</a>',
                delete_url,
                button_style
            )
        else:
            delete_button = format_html(
                '<button class="button" style="{0}" disabled>Delete</button>',
                button_style
            )
        return mark_safe(delete_button)

    def edit(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: blue; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            edit_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/'
            edit_button = format_html(
                '<a href="{0}" class="button" style="{1}">Edit</a>',
                edit_url,
                button_style
            )
        else:
            edit_button = format_html(
                '<button class="button" style="{0}" disabled>Edit</button>',
                button_style
            )
        return mark_safe(edit_button)
    
    list_display = ("connection_name", "db_url", "db_name", "auth_mode", "delete", "edit")

    class Media:
        js = ('js/admin/dbconfig.js',)  # Include the JavaScript file


class AanlyticsScheduleAdmin(admin.ModelAdmin):
    change_form_template = 'admin/analytics/aanlyticsschedule/change_form.html'
    exclude = ('periodic_task',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test_code/', self.admin_site.admin_view(views.test_code_view), name='test_code'),
        ]
        return custom_urls + urls

    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 4px 6px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: #ff0000; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            delete_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/delete/'
            delete_button = format_html(
                '<a href="{0}" class="button" style="{1}">Delete</a>',
                delete_url,
                button_style
            )
        else:
            delete_button = format_html(
                '<button class="button" style="{0}" disabled>Delete</button>',
                button_style
            )
        return mark_safe(delete_button)

    def edit(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: blue; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            edit_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/'
            edit_button = format_html(
                '<a href="{0}" class="button" style="{1}">Edit</a>',
                edit_url,
                button_style
            )
        else:
            edit_button = format_html(
                '<button class="button" style="{0}" disabled>Edit</button>',
                button_style
            )
        return mark_safe(edit_button)
    
    def history(self, obj):
        button_style = (
            'border-radius: 4px;'
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: #417690; '
            'color: white; '
            'cursor: pointer;'
        )
        cl_url = f"/admin/analytics/analytichistory/"
        # url = reverse('admin:appname_relatedmodel_changelist')
        url_with_filter = f"{cl_url}?schedule_name={obj.schedule_name}"
        return format_html('<a class="button" style="{}" href="{}">History</a>', button_style, 
                           url_with_filter)
    
    list_display = ("schedule_name", "select_database", "output_plan", "delete", "edit", "history")


class AnalyticHistoryAdmin(admin.ModelAdmin):
    def download(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: blue; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj.file_name:  # Check if file_name exists
            download_url = reverse('admin:download-csv', args=[obj.id])
            download_btn = format_html(
                '<a href="{0}" class="button" style="{1}">Download</a>',
                download_url,
                button_style
            )
        else:
            download_btn = format_html(
                '<button class="button" style="{0}" disabled>Download</button>',
                button_style
            )
        return mark_safe(download_btn)

    download.short_description = 'Download CSV'

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/download/', self.admin_site.admin_view(self.download_view), name='download-csv'),
        ]
        return custom_urls + urls

    def download_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if not obj or not obj.file_name:
            return HttpResponse("File not found", status=404)

        file_path = os.path.join(settings.MEDIA_ROOT, obj.file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{obj.file_name}"'
                return response
        else:
            return HttpResponse("File not found", status=404)


    list_display = ("schedule_name", "timestamp", "file_name", "download")



class AnalyticOutputAdmin(admin.ModelAdmin):


    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 4px 6px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: #ff0000; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            delete_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/delete/'
            delete_button = format_html(
                '<a href="{0}" class="button" style="{1}">Delete</a>',
                delete_url,
                button_style
            )
        else:
            delete_button = format_html(
                '<button class="button" style="{0}" disabled>Delete</button>',
                button_style
            )
        return mark_safe(delete_button)

    def edit(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: blue; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            edit_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/'
            edit_button = format_html(
                '<a href="{0}" class="button" style="{1}">Edit</a>',
                edit_url,
                button_style
            )
        else:
            edit_button = format_html(
                '<button class="button" style="{0}" disabled>Edit</button>',
                button_style
            )
        return mark_safe(edit_button)

    list_display = ("connection_name", "ftp_path", "delete", "edit")





class AanlyticsSaveAdmin(admin.ModelAdmin):
    change_form_template = 'admin/analytics/aanlyticsschedule/change_form.html'
    exclude = ('periodic_task',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test_code/', self.admin_site.admin_view(views.test_code_analytic_view), name='test_code_analytic_view'),
        ]
        return custom_urls + urls

    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 4px 6px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: #ff0000; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            delete_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/delete/'
            delete_button = format_html(
                '<a href="{0}" class="button" style="{1}">Delete</a>',
                delete_url,
                button_style
            )
        else:
            delete_button = format_html(
                '<button class="button" style="{0}" disabled>Delete</button>',
                button_style
            )
        return mark_safe(delete_button)

    def edit(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: blue; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            edit_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/change/'
            edit_button = format_html(
                '<a href="{0}" class="button" style="{1}">Edit</a>',
                edit_url,
                button_style
            )
        else:
            edit_button = format_html(
                '<button class="button" style="{0}" disabled>Edit</button>',
                button_style
            )
        return mark_safe(edit_button)
    
    # def history(self, obj):
    #     button_style = (
    #         'border-radius: 4px;'
    #         'margin: 2px 0; '
    #         'padding: 2px 3px; '
    #         'vertical-align: middle; '
    #         'font-family: var(--font-family-primary); '
    #         'font-weight: normal; '
    #         'font-size: 0.8125rem; '
    #         'background-color: #417690; '
    #         'color: white; '
    #         'cursor: pointer;'
    #     )
    #     cl_url = f"/admin/analytics/analytichistory/"
    #     # url = reverse('admin:appname_relatedmodel_changelist')
    #     url_with_filter = f"{cl_url}?schedule_name={obj.analytic_name}"
    #     return format_html('<a class="button" style="{}" href="{}">History</a>', button_style, 
    #                        url_with_filter)
    
    list_display = ("analytic_name", "analytic_output", "select_database", "embedded_code", "delete", "edit", )



admin_site.register(AanlyticsSchedule, AanlyticsScheduleAdmin)
admin_site.register(OdooDatabase, OdooDatabaseAdmin)
admin_site.register(AnalyticHistory, AnalyticHistoryAdmin)
admin_site.register(AnalyticOutput, AnalyticOutputAdmin)
admin_site.register(SaveAnalytic, AanlyticsSaveAdmin)