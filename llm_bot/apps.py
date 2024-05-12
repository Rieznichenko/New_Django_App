from django.apps import AppConfig

class LlmBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'llm_bot'

    def ready(self):
        # Import signal handlers here to ensure they are registered after the app registry is ready
        from . import signals
