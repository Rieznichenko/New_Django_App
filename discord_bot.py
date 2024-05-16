from collections import defaultdict
import discord
from dotenv import load_dotenv
import openai
import time
from llm import  chat_functionality_gemini, chat_functionality, check_thread_status
import logging

load_dotenv()


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
        return self.api_key, self.assistant_id, self.discord_bot_token, self.bot_thread_id
    
config_store = ConfigStore()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
thread_data = defaultdict()


@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")



@client.event
async def on_message(message):
    """An event handler triggered upon receiving a message"""
    api_key, assistant_id, discord_bot_token, bot_thread_id = config_store.get_param()

    try:
        import sqlite3
        conn = sqlite3.connect('/Users/apple/Documents/projects/gpt_discord/db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM llm_bot_discordbotconfig WHERE bot_thread_id = ?", (bot_thread_id,))
        row = cursor.fetchone()
        if row:
            print("Got row", row)
        else:
            raise Exception("something went wrong")

    except Exception as e:
        print("Closing down the bot as signal issued")
        await client.close()

    if message.author == client.user:
        print("qual")
        return

    
    user_input = message.content
    print(user_input)

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
                assistant_message = chat_functionality(OPENAI_CLIENT, message.channel, user_input, thread_id, assistant_id)
                await message.channel.send(assistant_message)
            except Exception as e:
                logging.exception(e)
                await message.channel.send(f"Failed to start chat: {str(e)}")
    else:
        gemini_response = chat_functionality_gemini(user_input, message.channel, api_key, assistant_id)
        await message.channel.send(gemini_response)


def start_discord_bot(discord_bot_token):
    client.run(discord_bot_token)


def run_discord_bot(api_key, assistant_id, discord_bot_token, bot_thread_id):
    config_store.set_param(api_key, assistant_id, discord_bot_token, bot_thread_id)
    try:

        start_discord_bot(discord_bot_token)
    except Exception as e:
        logging.error(f"Exception {e}")
        return