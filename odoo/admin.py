# admin.py
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import OdooDatabase, OdooFields, OdooTableField, OddoBotConfig, OdooRelationField
from llm_bot.admin import CustomAdminSite, admin_site
from llm_bot.views import get_field_choices, get_field_choices_relation

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
            self.fields['username'].widget.attrs.update({'style': 'display:block'})
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

admin_site.register(OdooDatabase, OdooDatabaseAdmin)


class OdooRelationFieldForm(forms.ModelForm):
    class Meta:
        model = OdooTableField
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oddo_write_field'].widget = forms.Select()
        self.fields['oddo_read_field'].widget = forms.Select()
        # self.fields['field_name'].disabled = True

        if 'instance' in kwargs:
            if kwargs.get("instance"):
                if kwargs['instance'].id:
                    instance = kwargs.get('instance')

                    odoo_write_field = instance.oddo_write_field
                    odoo_read_field = instance.oddo_read_field
                    CHOICES_READ = [(instance.oddo_read_field, instance.oddo_read_field)]
                    CHOICES_WRITE = [(instance.oddo_write_field, instance.oddo_write_field)]

                    read_fields, write_fields = get_relation_model_choices(kwargs)
                    
                    for choice in write_fields:
                        if choice != odoo_write_field:
                            CHOICES_WRITE.append((choice, choice))

                    for choice in read_fields:
                        if choice != odoo_read_field:
                            CHOICES_READ.append((choice, choice))
                    

                self.fields['oddo_write_field'].widget = forms.Select(choices = CHOICES_WRITE)
                self.fields['oddo_read_field'].widget = forms.Select(choices = CHOICES_READ)




class OdooTableFieldForm(forms.ModelForm):
    class Meta:
        model = OdooTableField
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field_name'].widget = forms.Select()
        # self.fields['field_name'].disabled = True

        if 'instance' in kwargs:
            if kwargs.get("instance"):
                if kwargs['instance'].id:
                    instance = kwargs.get('instance')
                    CHOICES = [(instance.field_name, instance.field_name)]
                    existing_choice = instance.field_name
                    get_choices = get_model_choices(kwargs)
                    if get_choices:
                        for choice in get_choices:
                            if choice != existing_choice:
                                CHOICES.append((choice, choice))

                    self.fields['field_name'].widget = forms.Select(choices=CHOICES)
                    # self.fields['field_name'].disabled = True


def get_model_choices(kwargs):
    try:
        database_id = kwargs['instance'].odoo_field.database_name.id
        table_name = kwargs['instance'].odoo_field.database_table
        fields = get_field_choices(None, table_name, database_id)
        return fields
    except:
        return []
    
def get_relation_model_choices(kwargs):
    try:
        read_fields, write_fields = get_field_choices_relation(read_id = kwargs['instance'].odoo_relation_field.select_read_model.id, write_id = kwargs['instance'].odoo_relation_field.select_write_model.id)
        return read_fields, write_fields
    except:
        return [], []

class OdooRelationFieldsInline(admin.TabularInline):
    model = OdooRelationField
    form = OdooRelationFieldForm
    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.id:
            return 0
        return 1


class OdooFieldsInline(admin.TabularInline):
    model = OdooTableField
    form = OdooTableFieldForm
    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.id:
            return 0
        return 1

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
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_view'] = 'change'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_view'] = 'add'
        return super().add_view(request, form_url, extra_context=extra_context)
    
    list_display = ("models_and_fields_name", "database_name", "database_table", "type", "delete", "edit")




class OddoBotConfigAdmin(admin.ModelAdmin):
    inlines = [OdooRelationFieldsInline]
    class Media:
        js = ('js/admin/custom_odoo_fields.js',)

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
        cl_url = f"/admin/llm_bot/chatbotmessage/"
        # url = reverse('admin:appname_relatedmodel_changelist')
        url_with_filter = f"{cl_url}?chatbot_name={obj.chatbot_name}&bot_type={obj.bot_type}"
        return format_html('<a class="button" style="{}" href="{}">History</a>', button_style, 
                           url_with_filter)


    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_view'] = 'change'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_view'] = 'add'
        return super().add_view(request, form_url, extra_context=extra_context)
    
    list_display = ('chatbot_name', 'widget_id', 'state'
                    ,'welcome_message', 'logo', 'edit','delete','history',)



admin_site.register(OdooFields, OdooFieldsAdmin)
admin_site.register(OddoBotConfig, OddoBotConfigAdmin)

