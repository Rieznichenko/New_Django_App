from django.contrib import admin
from .models import DiscordBotConfig, LLMAgent, LLMCOnfig, TelegramBotConfig, WhatsAppBotConfig, ChatBot
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class LLMConfigAdmin(admin.ModelAdmin):
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
    list_display = ('config_name','api_key', 'platform', 'delete')

class DiscordConfigAdmin(admin.ModelAdmin):

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
    list_display = ('discord_bot_token', 'discord_client_id', 'discord_bot', 'delete')

class LLMAgentAdmin(admin.ModelAdmin):
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
    
    list_display = ('agent_name', 'assistant_id', 'agent_name', 'delete')


class TelegramConfigAdmin(admin.ModelAdmin):
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
    list_display = ('telegram_bot_token', 'telegram_bot', 'delete')

    class Media:
        js = ('path/to/your/js/file.js',)  # Include your JavaScript file here


class WhatsappBotAdmin(admin.ModelAdmin):
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
    
    list_display = ('whatsapp_bot_token', 'whatsapp_llm_config', 'whatsapp_llm_agent', 'delete')


class ChatBotAdmin(admin.ModelAdmin):
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

    def visit(self, obj):
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
            delete_url = f'/chatbot/{obj.widget_id}'
            delete_button = format_html(
                '<a href="{0}" class="button" style="{1}">Visit</a>',
                delete_url,
                button_style
            )
        else:
            delete_button = format_html(
                '<button class="button" style="{0}" disabled>Visit</button>',
                button_style
            )
        return mark_safe(delete_button)

    list_display = ('chatbot_name', 'widget_id', 'chatbot_llm_config', 'chatbot_llm_agent', 'logo', 'visit', 'delete')


admin.site.register(LLMCOnfig, LLMConfigAdmin)
admin.site.register(DiscordBotConfig, DiscordConfigAdmin)
admin.site.register(TelegramBotConfig, TelegramConfigAdmin)
admin.site.register(LLMAgent, LLMAgentAdmin)
admin.site.register(WhatsAppBotConfig, WhatsappBotAdmin)
admin.site.register(ChatBot, ChatBotAdmin)
