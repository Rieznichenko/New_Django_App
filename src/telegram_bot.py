import os
import openai
import telebot
from completion import check_thread_status
from constants import (
    fetch_telegram_credentials
)
import logging
from utils import (
    logger
)
logging.basicConfig(
    format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", level=logging.INFO
)

api_key, assitant_id, bot_token = fetch_telegram_credentials()

BOT_TOKEN = bot_token

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    user_input = message.text


    if "asst_" in assitant_id:
        logger.info("Openai client created")
        openai.api_key = api_key
        OPENAI_CLIENT = openai.Client(api_key=api_key)
        logger.info(f"Message received: {user_input}")
        # Ensure the message is not empty
        if user_input:
            try:
                thread = OPENAI_CLIENT.beta.threads.create()
                thread_id = thread.id
                chat_functionality(OPENAI_CLIENT, message, user_input, thread_id, assitant_id)
            except Exception as e:
                logger.exception(e)
                bot.reply_to(message, f"Failed to start chat: {str(e)}")
    else:
        chat_functionality_gemini(user_input, message, api_key, assitant_id)


def chat_functionality_gemini(user_input, message, api_key, assistant_id):
    """
    Perform chat functionality using OpenAI API.

    Parameters:
        channel (discord.TextChannel): The channel where the response will be sent.
        user_input (str): The user input for the chat.

    Returns:
        None
    """
  
    import os
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')

    prompt = user_input
    response = model.generate_content(prompt)

    print(response.text) 

    # Send the assistant's response to the channel
    bot.reply_to(message, response.text)

def chat_functionality(OPENAI_CLIENT, message, user_input, thread_id, assitant_id):
    """
    Perform chat functionality using OpenAI API.

    Parameters:
        channel (discord.TextChannel): The channel where the response will be sent.
        user_input (str): The user input for the chat.

    Returns:
        None
    """
    # Configure OpenAI API


    # Create a new thread for the conversation
    # Send user's message to the thread
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

    # Send the assistant's response to the channel
    bot.reply_to(message, assistant_message)



bot.infinity_polling()
