from collections import defaultdict
import discord
from discord import Message as DiscordMessage, app_commands
import logging
import asyncio
import os
from dotenv import load_dotenv
import openai
from telegram_bot import check_thread_status
from llm_bot.models import DiscordBotConfig
from asgiref.sync import sync_to_async

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", level=logging.INFO
)

class ConfigStore:
    def __init__(self) -> None:
        self.api_key = None
        self.assistant_id = None
        self.discord_bot_token = None
        self.bot_thread_id = None

    def set_param(self, api_key, assistant_id, discord_bot_token, bot_thread_id):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.discord_bot_token = discord_bot_token
        self.bot_thread_id = bot_thread_id

    def get_param(self):
        try:
            obj = sync_to_async(DiscordBotConfig.objects.get(bot_thread_id = self.bot_thread_id))
            api_key = obj.discord_llm_agent.llm_config.llmconfig.api_key
            assistant_id = obj.discord_llm_agent.assistant_id
            logging.info(f"Giving back {api_key} and {assistant_id}")

            return api_key, assistant_id, self.discord_bot_token, self.bot_thread_id
        except Exception as e:
            logging.error(f"Failed while pulling param {e}")
            return self.api_key, self.assistant_id, self.discord_bot_token, self.bot_thread_id
    
config_store = ConfigStore()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
thread_data = defaultdict()


@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")


async def chat_functionality_gemini(user_input, channel, api_key, assistant_id):
    """
    Perform chat functionality using OpenAI API.

    Parameters:
        channel (discord.TextChannel): The channel where the response will be sent.
        user_input (str): The user input for the chat.

    Returns:
        None
    """
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')

    prompt = user_input
    response = model.generate_content(prompt)

    print(response.text)

    # Send the assistant's response to the channel
    await channel.send(response.text)


async def chat_functionality(OPENAI_CLIENT, channel, user_input, thread_id, assistant_id):
    """
    Perform chat functionality using OpenAI API.

    Parameters:
        channel (discord.TextChannel): The channel where the response will be sent.
        user_input (str): The user input for the chat.

    Returns:
        None
    """
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
        assistant_id=assistant_id,
    )

    # Check the status of the conversation thread
    check_thread_status(OPENAI_CLIENT, thread_id, run.id)

    # Retrieve messages from the conversation thread
    messages = OPENAI_CLIENT.beta.threads.messages.list(thread_id=thread_id)

    # Extract user and assistant messages
    user_message = messages.data[1].content[0].text.value
    assistant_message = messages.data[0].content[0].text.value

    # Send the assistant's response to the channel
    await channel.send(assistant_message)

@client.event
async def on_message(message):
    """
    An event handler triggered upon receiving a message.

    Parameters:
        message (discord.Message): The message received by the bot.

    Returns:
        None
    """
    api_key, assistant_id, discord_bot_token, bot_thread_id = config_store.get_param()

    try:
        bot_config = await sync_to_async(DiscordBotConfig.objects.get)(bot_thread_id=bot_thread_id)
    except Exception as e:
        print("Closing down the bot as signal issued")
        await client.close()

    if message.author == client.user:
        return

    
    user_input = message.content

    if "asst_" in assistant_id:
        logging.info("Openai client created")
        openai.api_key = api_key
        OPENAI_CLIENT = openai.Client(api_key=api_key)
        logging.info(f"Message received: {user_input}")
        # Ensure the message is not empty
        if user_input:
            try:
                thread = OPENAI_CLIENT.beta.threads.create()
                thread_id = thread.id
                await chat_functionality(OPENAI_CLIENT, message.channel, user_input, thread_id, assistant_id)
            except Exception as e:
                logging.exception(e)
                await message.channel.send(f"Failed to start chat: {str(e)}")
    else:
        await chat_functionality_gemini(user_input, message.channel, api_key, assistant_id)


def start_discord_bot(discord_bot_token):
    client.run(discord_bot_token)


def run_discord_bot(api_key, assistant_id, discord_bot_token, bot_thread_id):
    config_store.set_param(api_key, assistant_id, discord_bot_token, bot_thread_id)
    try:

        start_discord_bot(discord_bot_token)
    except Exception as e:
        logging.error(f"Exception {e}")