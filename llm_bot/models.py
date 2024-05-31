from django.db import models
import uuid
from singleton_model import SingletonModel
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
        verbose_name = "LLM IA Configuration"
        verbose_name_plural = "LLM IA Configurations"

class LLMAgent(models.Model):
    agent_name = models.CharField(max_length=100, default='', blank=True, null=True)
    llm_config = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    assistant_id = models.CharField(max_length=100, default='', blank=True, null=True)
    def __str__(self) -> str:
        return self.agent_name
    
    class Meta:
        verbose_name = "LLM Agent Configuration"
        verbose_name_plural =  "LLM Agent Configurations"


class DiscordBotConfig(models.Model):
    STATE_CHOICES = [
        ('running', 'Running'),
        ('paused', 'Puased'),
    ]
    
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="running")
    chatbot_name = models.CharField(max_length=100, default='')
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
        verbose_name_plural = "Discord Bot Configurations"


class TelegramBotConfig(models.Model):
    STATE_CHOICES = [
        ('running', 'Running'),
        ('paused', 'Puased'),
    ]
    
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="running")
    chatbot_name = models.CharField(max_length=100, default='')
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
        verbose_name_plural = "Telegram Bot Configurations"

class WhatsAppBotConfig(models.Model):
    STATE_CHOICES = [
        ('running', 'Running'),
        ('paused', 'Puased'),
    ]
    
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="running")
    chatbot_name = models.CharField(max_length=100, default='')
    whatsapp_bot_token = models.CharField(max_length=100, default='')
    whatsapp_channel_id = models.CharField(max_length=100, primary_key=True)
    whatsapp_llm_config = models.ForeignKey(Page, on_delete=models.CASCADE)
    whatsapp_llm_agent = models.ForeignKey(LLMAgent, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.whatsapp_bot_token


    class Meta:
        verbose_name = "Whatsapp Bot Configuration"
        verbose_name_plural = "Whatsapp Bot Configurations"


class ChatBot(models.Model):
    STATE_CHOICES = [
        ('running', 'Running'),
        ('paused', 'Puased'),
    ]
    
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="running")
    chatbot_name = models.CharField(max_length=100, default='')
    widget_id = models.UUIDField(default=uuid.uuid4, editable=False)
    chatbot_llm_config = models.ForeignKey(Page, on_delete=models.CASCADE)
    chatbot_llm_agent = models.ForeignKey(LLMAgent, on_delete=models.CASCADE, null=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    welcome_message = models.TextField(default='', blank=True, null=True)

    def __str__(self) -> str:
        return self.chatbot_name
    

    class Meta:
        verbose_name = "WebBot Configuration"
        verbose_name_plural = "WebBot Configurations"

class ChatBotMessage(models.Model):
    content = models.TextField()
    author = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "WebBot Chat Thread"
        verbose_name_plural = "WebBot Chat Threads"

    def __str__(self):
        return f'{self.author}: {self.content[:50]}...'
        

class DiscordMessage(models.Model):
    content = models.TextField()
    author = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Discord Chat Thread"
        verbose_name_plural = "Discord Chat Threads"

    def __str__(self):
        return f'{self.author}: {self.content[:50]}...'

class WhatsAppMessage(models.Model):
    content = models.TextField()
    author = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Whatsapp Chat Thread"
        verbose_name_plural = "Whatsapp Chat Threads"

    def __str__(self):
        return f'{self.author}: {self.content[:50]}...'

class TelegramMessage(models.Model):
    content = models.TextField()
    author = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author}: {self.content[:50]}...'

    class Meta:
        verbose_name = "Telegram Chat Thread"
        verbose_name_plural = "Telegram Chat Threads"
        

class EmailSchedule(models.Model):
    recipient = models.EmailField()
    frequency_hours = models.PositiveIntegerField(default=24)  # Change this line

