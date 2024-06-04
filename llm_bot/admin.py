from django.contrib import admin

from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import ChatBotMessage, DiscordBotConfig, EmailSchedule, LLMAgent, LLMCOnfig, TelegramBotConfig, WhatsAppBotConfig, ChatBot
from django.utils.html import format_html
from django.utils.safestring import mark_safe



class CustomBaseAdmin(admin.ModelAdmin):
    list_display = ('edit_link',  "view_related_model_button")
    edit_button_style = (
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

    def edit_link(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return format_html(
            '<a href="{}" style="{}">Edit</a>',
            url,
            self.edit_button_style
        )
    edit_link.short_description = 'Edit'
    
    def view_related_model_button(self, obj):
        cl_url = f"/admin/{obj._meta.app_label}/chatbotmessage/"
        # url = reverse('admin:appname_relatedmodel_changelist')
        url_with_filter = f"{cl_url}?chatbot_name={obj.chatbot_name}&bot_type={obj.bot_type}"
        return format_html('<a class="button" style="{}" href="{}">History</a>', self.edit_button_style, 
                           url_with_filter)

    view_related_model_button.short_description = 'History'

    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        chatbot_name = request.GET.get('chatbot_name')
        bot_type = request.GET.get('bot_type')
        if bot_type:
            qs = qs.filter(bot_type=bot_type, chatbot_name=chatbot_name)
        return qs
    

class LLMConfigAdmin(CustomBaseAdmin):
    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
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
    list_display = ('config_name','api_key', 'platform', 'delete') + tuple(
        field for field in CustomBaseAdmin.list_display if field != 'view_related_model_button'
    )

class DiscordConfigAdmin(CustomBaseAdmin):
    list_editable = ['state',]

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return ('discord_bot_token', 'discord_client_id')
    
    def discord_bot(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: var(--button-bg); '
            'color: white; '
            'cursor: pointer;'
        )
        discord_link = ''
        if obj:
            client_id = obj.discord_client_id
            discord_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=328565073920&scope=bot"
        
        Discord_bot = format_html(
            '<button id="approve-button-{0}" class="button" style="{1} cursor: pointer;" onclick="window.open(\'{2}\', \'_blank\')">View Discord Bot</button>',
            0,
            "",
            discord_link
        )

        actions = f'{Discord_bot}'

        return mark_safe(actions)

    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
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
    
    exclude = ('bot_thread_id',)
    list_display = ("chatbot_name", "state", 'discord_client_id', 'discord_bot', 'delete') + CustomBaseAdmin.list_display

class LLMAgentAdmin(CustomBaseAdmin):
    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
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
    
    list_display = ('agent_name', 'assistant_id', 'agent_name', 'delete') + tuple(
        field for field in CustomBaseAdmin.list_display if field != 'view_related_model_button'
    )

class TelegramConfigAdmin(CustomBaseAdmin):
    list_editable = ['state']
    
    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return ('telegram_bot_token',)

    def telegram_bot(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: var(--button-bg); '
            'color: white; '
            'cursor: pointer;'
        )
        telegram_link = obj.bot_link if obj else ''
        
        telegram_bot_button = format_html(
            '<button class="button" style="{0}" onclick="window.open(\'{1}\', \'_blank\')">View Telegram Bot</button>',
            button_style,
            telegram_link
        )

        return mark_safe(telegram_bot_button)

    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: #ff0000; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            delete_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.telegram_bot_token}/delete/'
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

    exclude = ('bot_thread_id',)
    list_display = ("chatbot_name", "state", 'telegram_bot', 'delete') + CustomBaseAdmin.list_display

    class Media:
        js = ('path/to/your/js/file.js',)  # Include your JavaScript file here


class WhatsappBotAdmin(CustomBaseAdmin):
    list_editable = ['state']
    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return ('whatsapp_bot_token', 'whatsapp_channel_id')
    
    def delete(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 2px 3px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: #ff0000; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            delete_url = f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.whatsapp_channel_id}/delete/'
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
    
    
    list_display = ("chatbot_name", "state", 'whatsapp_llm_config',
                    'whatsapp_llm_agent', 'delete') + CustomBaseAdmin.list_display


class ChatBotAdmin(CustomBaseAdmin):
    list_editable = ['state']
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

    def visit(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 4px 6px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: blue; '
            'color: white; '
            'cursor: pointer;'
        )

        if obj:
            delete_url = f'/chatbot/{obj.widget_id}'
            delete_button = format_html(
                '<a href="{0}" class="button" style="{1}" target="_blank">Visit</a>',
                delete_url,
                button_style
            )
        else:
            delete_button = format_html(
                '<button class="button" style="{0}" disabled>Visit</button>',
                button_style
            )
        return mark_safe(delete_button)
    
    def viewscript(self, obj):
        button_style = (
            'margin: 2px 0; '
            'padding: 4px 6px; '
            'vertical-align: middle; '
            'font-family: var(--font-family-primary); '
            'font-weight: normal; '
            'font-size: 0.8125rem; '
            'background-color: green; '
            'color: white; '
            'cursor: pointer;'
            'width: 80px;'
            'vertical-align: None; !important'
        )

        if obj:
            viewscript_button = format_html(
                '<button id="viewScript" type="button" class="button" style="{0}" onclick="openModal(\'{1}\')">View Script</button>',
                button_style,
                obj.widget_id
            )
        else:
            viewscript_button = format_html(
                '<button type="button" class="button" style="{0}" disabled>View Script</button>',
                button_style
            )
        return mark_safe(viewscript_button)
    class Media:
        js = ('js/custom_admin.js',)
        css = {
            'all': ('css/custom_admin.css',)
        }


    list_display = ('chatbot_name', 'widget_id', 'chatbot_llm_config', 'state',
                    'chatbot_llm_agent','welcome_message', 'logo', 'visit', 'delete', 'viewscript'
                    ) + CustomBaseAdmin.list_display



class ChatBotMessageAdmin(CustomBaseAdmin):
    list_display =  ('author', 'content','bot_type', 'timestamp') + tuple(
        field for field in CustomBaseAdmin.list_display if field != 'view_related_model_button'
    ) 
    

class EmailScheduleAdmin(admin.ModelAdmin):
    list_display = ["bot_type", "bot_name", "recipient", "frequency_hours"]

    class Media:
        js = ("js/get_chat_bot_name.js",)

from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            "LLM IA Configurations": 1,
            "LLM Agent Configurations": 2,
            "Discord Bot Configurations": 3,
            "Discord Chat Threads": 4,
            "Telegram Bot Configurations":5,
            "Telegram Chat Threads":6,
            "Whatsapp Bot Configurations":7,
            "Whatsapp Chat Threads":8,
            "WebBot Configurations":9,
            "WebBot Chat Threads":10,
            "Email schedules":11,
        }
        app_dict = self._build_app_dict(request, app_label)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering.get(x['name'], float('inf')))

        return app_list
admin_site = CustomAdminSite(name="ihorSite")
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(LLMCOnfig, LLMConfigAdmin)
admin_site.register(DiscordBotConfig, DiscordConfigAdmin)
admin_site.register(TelegramBotConfig, TelegramConfigAdmin)
admin_site.register(LLMAgent, LLMAgentAdmin)
admin_site.register(WhatsAppBotConfig, WhatsappBotAdmin)
admin_site.register(ChatBot, ChatBotAdmin)
admin_site.register(ChatBotMessage, ChatBotMessageAdmin)
admin_site.register(EmailSchedule, EmailScheduleAdmin)
