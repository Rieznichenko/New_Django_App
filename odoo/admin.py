# admin.py
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import OdooDatabase, OdooFields, OdooTableField
from llm_bot.admin import CustomAdminSite, admin_site

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
    
    list_display = ("db_url", "db_name", "auth_mode", "delete", "edit")

    class Media:
        js = ('js/admin/dbconfig.js',)  # Include the JavaScript file

admin_site.register(OdooDatabase, OdooDatabaseAdmin)



class OdooTableFieldForm(forms.ModelForm):
    class Meta:
        model = OdooTableField
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field_name'].widget = forms.Select()
        self.fields['field_name'].disabled = True

        if 'instance' in kwargs:
            if kwargs.get("instance"):
                if kwargs['instance'].id:
                    CHOICES = [
                        (kwargs['instance'].field_name, kwargs['instance'].field_name)
                    ]
                    print("Ch", CHOICES)
                    self.fields['field_name'].widget = forms.Select(choices=CHOICES)
                    # self.fields['field_name'].disabled = True



class OdooFieldsInline(admin.TabularInline):
    model = OdooTableField
    form = OdooTableFieldForm
    extra = 1  # Set a positive integer to control the number of extra forms displayed


class OdooFieldsForm(forms.ModelForm):
    class Meta:
        model = OdooFields
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['database_table'].widget = forms.Select()

        if 'instance' in kwargs:
            if kwargs.get("instance"):
                if kwargs['instance'].id:
                    CHOICES = [
                        (kwargs['instance'].database_table, kwargs['instance'].database_table)
                    ]
                    self.fields['database_table'].widget = forms.Select(choices=CHOICES)

        # self.fields['database_table'].disabled = True


class OdooFieldsAdmin(admin.ModelAdmin):
    inlines = [OdooFieldsInline]
    form = OdooFieldsForm

    class Media:
        js = ('js/admin/custom_odoo_fields.js',)
        

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_view'] = 'change'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_view'] = 'add'
        return super().add_view(request, form_url, extra_context=extra_context)

admin_site.register(OdooFields, OdooFieldsAdmin)

