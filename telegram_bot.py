import telebot
import logging
import openai
import time
from llm_bot.models import ChatBotMessage, TelegramBotConfig
from asgiref.sync import sync_to_async
from llm import chat_functionality_gemini, chat_functionality, check_thread_status

logging.basicConfig(
    format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", level=logging.INFO
)

class ConfigStore:
    def __init__(self) -> None:
        self.api_key = None
        self.assistant_id = None
        self.telegram_bot_token = None
        self.bot_thread_id = None

    def set_param(self, api_key, assistant_id, telegram_bot_token, bot_thread_id):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.telegram_bot_token = telegram_bot_token
        self.bot_thread_id = bot_thread_id

    def get_param(self):
        try:
            instance = sync_to_async(TelegramBotConfig.objects.get(bot_thread_id = self.bot_thread_id))
            assistant_id = instance.telegram_llm_agent.assistant_id
            api_key = instance.telegram_llm_agent.llm_config.llmconfig.api_key
            logging.info(f"Giving back {api_key} and {assistant_id}")

            return api_key, assistant_id, self.telegram_bot_token, self.bot_thread_id
        except Exception as e:
            logging.error(f"Failed while pulling param {e}")
            return self.api_key, self.assistant_id, self.telegram_bot_token, self.bot_thread_id
    
config_store = ConfigStore()


def run_telegram_bot(api_key, assistant_id, telegram_bot_token, bot_thread_id):
    global stop_threads
    stop_threads = False

    config_store.set_param(api_key, assistant_id, telegram_bot_token, bot_thread_id)
    bot = telebot.TeleBot(telegram_bot_token, bot_thread_id=bot_thread_id)

    @bot.message_handler(func=lambda msg: True)
    def echo_all(message):
        user_input = message.text
        user_name = message.from_user.username or message.from_user.first_name

        api_key, assitant_id, bot_token, bot_thread_id = config_store.get_param()
        try:
            obj = TelegramBotConfig.objects.get(telegram_bot_token=bot_token)
            bot_name = obj.chatbot_name
            if obj.state == "paused":
                return
        except TelegramBotConfig.DoesNotExist:
            return
        if "asst_" in assitant_id:
            logging.info("Openai client created")
            openai.api_key = api_key
            OPENAI_CLIENT = openai.Client(api_key=api_key)
            logging.info(f"Message received: {user_input}")
            if user_input:
                try:
                    thread = OPENAI_CLIENT.beta.threads.create()
                    thread_id = thread.id
                    assistant_message = chat_functionality(OPENAI_CLIENT, message, user_input, thread_id, assitant_id)
                    ChatBotMessage.objects.create(content=user_input, author="Human", bot_name=bot_name, bot_type="telegram")
                    ChatBotMessage.objects.create(content=assistant_message, author="BOT", bot_name=bot_name, bot_type="telegram")
                    return bot.reply_to(message, assistant_message)
                except Exception as e:
                    logging.exception(e)
                    bot.reply_to(message, f"Failed to start chat: {str(e)}")
        else:
            assistant_message = chat_functionality_gemini(user_input, message, api_key, assitant_id)
            ChatBotMessage.objects.create(content=assistant_message, author="BOT", bot_name=bot_name, bot_type="telegram")
            ChatBotMessage.objects.create(content=user_input, author="Human", bot_name=bot_name, bot_type="telegram")
            bot.reply_to(message, assistant_message)

    thread_iteartion = 0
    while not stop_threads:
        thread_iteartion = thread_iteartion + 1
        if thread_iteartion == 2:
            break        
        bot.polling()
    return
