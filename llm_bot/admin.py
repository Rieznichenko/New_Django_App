from django.contrib import admin
from .models import DiscordBotConfig, LLMAgent, LLMCOnfig, TelegramBotConfig, WhatsAppBotConfig
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class LLMConfigAdmin(admin.ModelAdmin):
    list_display = ('config_name','api_key', 'platform', )

class DiscordConfigAdmin(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return ('discord_bot_token', 'discord_client_id')

    def discord_bot(self, obj):
        button_style = 'background-color: #47bac1; color: #fff; font-size: 12px; font-size: 0.85714rem; font-weight: lighter; '
        discord_link = ''
        first_record = DiscordBotConfig.objects.first()
        if first_record:
            client_id = first_record.discord_client_id
            discord_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=328565073920&scope=bot"
        
        

        # Your button HTML with Facebook link
        Discord_bot = format_html(
            '<button id="approve-button-{0}" class="button" style="{1} cursor: pointer;" onclick="window.open(\'{2}\', \'_blank\')">View Discord Bot</button>',
            0,
            "",
            discord_link
        )

        actions = f'{Discord_bot}'

        return mark_safe(actions)

    exclude = ('bot_thread_id',)
    list_display = ('discord_bot_token', 'discord_client_id', 'discord_bot')

class LLMAgentAdmin(admin.ModelAdmin):
    list_display = ('agent_name', 'assistant_id', 'agent_name')


class TelegramConfigAdmin(admin.ModelAdmin):
    # readonly_fields = ('telegram_bot_token', )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return ('telegram_bot_token',)

    def telegram_bot(self, obj):
        button_style = 'background-color: #47bac1; color: #fff; font-size: 12px; font-size: 0.85714rem; font-weight: lighter; '
        discord_link = ''
        first_record = TelegramBotConfig.objects.first()
        if first_record:
            client_id = first_record.telegram_bot_token[:10]
            discord_link = f"https://web.telegram.org/a/#{client_id}"
        
        

        # Your button HTML with Facebook link
        Telegram_bot = format_html(
            '<button id="approve-button-{0}" class="button" style="{1} cursor: pointer;" onclick="window.open(\'{2}\', \'_blank\')">View Telegram Bot</button>',
            0,
            "",
            discord_link
        )

        actions = f'{Telegram_bot}'

        return mark_safe(actions)
    
    exclude = ('bot_thread_id',)
    list_display = ('telegram_bot_token', 'telegram_bot')

class WhatsappBotAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return ('whatsapp_bot_token', 'whatsapp_channel_id')
    
    list_display = ('whatsapp_bot_token', 'whatsapp_llm_config', 'whatsapp_llm_agent', )

admin.site.register(LLMCOnfig, LLMConfigAdmin)
admin.site.register(DiscordBotConfig, DiscordConfigAdmin)
admin.site.register(TelegramBotConfig, TelegramConfigAdmin)
admin.site.register(LLMAgent, LLMAgentAdmin)
admin.site.register(WhatsAppBotConfig, WhatsappBotAdmin)
