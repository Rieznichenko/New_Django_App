from django.contrib import admin
from .models import DiscordBotConfig, LLMAgent, LLMCOnfig
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class LLMConfigAdmin(admin.ModelAdmin):
    list_display = ('config_name','api_key', 'platform', )

class DiscordConfigAdmin(admin.ModelAdmin):
    readonly_fields = ('discord_bot_token', 'discord_client_id')

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

    list_display = ('discord_bot_token', 'discord_client_id', 'discord_bot')

class LLMAgentAdmin(admin.ModelAdmin):
    list_display = ('agent_name', 'assistant_id', 'agent_name')

admin.site.register(LLMCOnfig, LLMConfigAdmin)
admin.site.register(DiscordBotConfig, DiscordConfigAdmin)
admin.site.register(LLMAgent, LLMAgentAdmin)
