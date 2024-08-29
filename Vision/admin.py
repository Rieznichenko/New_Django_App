# admin.py

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from . import views
from .models import VisionApplication, ApplicationUser
from llm_bot.admin import admin_site
from django.http import HttpResponse
from django.conf import settings
import os
from django.urls import reverse, path
from llm_bot.admin import CustomAdminSite, admin_site


# Register your models here.

class VisionAdmin(admin.ModelAdmin):
    readonly_fields = ('unique_token',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # When editing an existing object
            return self.readonly_fields + ('application_name',)  # Example of making other fields read-only
        return self.readonly_fields


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
    
    list_display = ("application_name", "telegram_bot_id", "unique_token", "delete", "edit")



class ApplicationUserAdmin(admin.ModelAdmin):

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
    
    list_display = ("name", "telegram_id", "delete", "edit")

admin_site.register(VisionApplication, VisionAdmin)
admin_site.register(ApplicationUser, ApplicationUserAdmin)