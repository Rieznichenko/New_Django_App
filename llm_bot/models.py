from django.db import models
import uuid

class Page(models.Model):
    config_name = models.CharField(max_length=100, default='', blank=True, null=True)

    def __str__(self) -> str:
        return self.config_name
    


class LLMCOnfig(Page):
    PLATFORM_CHOICES = [
        ('openai', 'OpenAI'),
        ('gemini', 'Gemini'),
        
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    api_key = models.CharField(max_length=100, default='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return self.platform

    class Meta:
        verbose_name = "LLM Configuration"
        verbose_name_plural = "LLM Configuration"

class LLMAgent(models.Model):
    agent_name = models.CharField(max_length=100, default='', blank=True, null=True)
    llm_config = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    assistant_id = models.CharField(max_length=100, default='', blank=True, null=True)
    def __str__(self) -> str:
        return self.agent_name
    
    class Meta:
        verbose_name = "LLM Agent Configuration"
        verbose_name_plural =  "LLM Agent Configuration"


class DiscordBotConfig(models.Model):
    discord_bot_token = models.CharField(max_length=100, default='', blank=True, null=True)
    discord_client_id = models.CharField(max_length=100, default='', blank=True, null=True)
    discord_llm_config = models.ForeignKey(Page, on_delete=models.CASCADE)
    discord_llm_agent = models.ForeignKey(LLMAgent, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    bot_thread_id = models.CharField(max_length=100, default='', blank=True, null=True)


    def __str__(self) -> str:
        return self.discord_bot_token

    class Meta:
        verbose_name = "Discord Bot Configuration"
        verbose_name_plural = "Discord Bot Configuration"
        ordering = ['created_at']


class TelegramBotConfig(models.Model):
    telegram_bot_token = models.CharField(max_length=100, primary_key=True)
    telegram_llm_config = models.ForeignKey(Page, on_delete=models.CASCADE)
    telegram_llm_agent = models.ForeignKey(LLMAgent, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    bot_thread_id = models.CharField(max_length=100, default='', blank=True, null=True)
    bot_link = models.CharField(max_length=100, default='', blank=True, null=True)


    def __str__(self) -> str:
        return self.telegram_bot_token

    class Meta:
        verbose_name = "Telegram Bot Configuration"
        verbose_name_plural = "Telegram Bot Configuration"
        ordering = ['created_at']

class WhatsAppBotConfig(models.Model):
    whatsapp_bot_token = models.CharField(max_length=100, default='')
    whatsapp_channel_id = models.CharField(max_length=100, primary_key=True)
    whatsapp_llm_config = models.ForeignKey(Page, on_delete=models.CASCADE)
    whatsapp_llm_agent = models.ForeignKey(LLMAgent, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.whatsapp_bot_token


    class Meta:
        verbose_name = "Whatsapp Bot Configuration"
        verbose_name_plural = "Whatsapp Bot Configuration"
        ordering = ['created_at']
