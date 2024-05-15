import telebot
import logging
import openai
import time
from llm_bot.models import TelegramBotConfig
from asgiref.sync import sync_to_async

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

def check_thread_status(client, thread_id, run_id):
    """
    Check the status of the conversation thread.

    Parameters:
        client (openai.Client): The OpenAI client instance.
        thread_id (str): The ID of the conversation thread.
        run_id (str): The ID of the conversation run.

    Returns:
        None
    """

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        if run.status == "completed":
            logging.info(f"Run is completed")
            break
        elif run.status == "expired":
            logging.info(f"Run is expired")
            break
        else:
            logging.info(f"OpenAI: Run is not yet completed. Waiting...")
            time.sleep(3)

def chat_functionality_gemini(user_input, message, api_key, assistant_id):
    """Perform chat functionality using OpenAI API."""
    import os
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')

    prompt = user_input
    response = model.generate_content(prompt)

    return response.text

    # Send the assistant's response to the channel
    

def chat_functionality(OPENAI_CLIENT, message, user_input, thread_id, assitant_id):
    """Perform chat functionality using OpenAI API"""

    OPENAI_CLIENT.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )

    # Run the conversation thread with the assistant
    run = OPENAI_CLIENT.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assitant_id,
    )

    # Check the status of the conversation thread
    check_thread_status(OPENAI_CLIENT, thread_id, run.id)

    # Retrieve messages from the conversation thread
    messages = OPENAI_CLIENT.beta.threads.messages.list(thread_id=thread_id)

    # Extract user and assistant messages
    user_message = messages.data[1].content[0].text.value
    assistant_message = messages.data[0].content[0].text.value
    return assistant_message

    # Send the assistant's response to the channel
    

def run_telegram_bot(api_key, assistant_id, telegram_bot_token, bot_thread_id):
    global stop_threads
    stop_threads = False

    config_store.set_param(api_key, assistant_id, telegram_bot_token, bot_thread_id)
    bot = telebot.TeleBot(telegram_bot_token, bot_thread_id=bot_thread_id)

    @bot.message_handler(func=lambda msg: True)
    def echo_all(message):

        user_input = message.text
        api_key, assitant_id, bot_token = config_store.get_param()

        if "asst_" in assitant_id:
            logging.info("Openai client created")
            openai.api_key = api_key
            OPENAI_CLIENT = openai.Client(api_key=api_key)
            logging.info(f"Message received: {user_input}")
            # Ensure the message is not empty
            if user_input:
                try:
                    thread = OPENAI_CLIENT.beta.threads.create()
                    thread_id = thread.id
                    assistant_message = chat_functionality(OPENAI_CLIENT, message, user_input, thread_id, assitant_id)
                    # print("message", message)
                    return bot.reply_to(message, assistant_message)
                except Exception as e:
                    logging.exception(e)
                    bot.reply_to(message, f"Failed to start chat: {str(e)}")
        else:
            assistant_message = chat_functionality_gemini(user_input, message, api_key, assitant_id)
            bot.reply_to(message, assistant_message)

    i = 0
    while not stop_threads:
        i = i+1
        if i == 2:
            break        
        bot.polling()
    return
