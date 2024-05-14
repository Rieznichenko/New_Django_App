from collections import defaultdict
import openai
import discord
from discord import Message as DiscordMessage, app_commands
import logging
from base import Message, Conversation
from constants import (
    BOT_INVITE_URL,
    DISCORD_BOT_TOKEN,
    EXAMPLE_CONVOS,
    fetch_llm_credentials
)
import asyncio
from utils import (
    logger
)
from completion import check_thread_status, thread_store_get, thread_store_put
import os
from dotenv import load_dotenv
import openai
import gemini_api

# Load environment variables from .env file
load_dotenv()



logging.basicConfig(
    format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", level=logging.INFO
)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
thread_data = defaultdict()


@client.event
async def on_ready():
    logger.info(f"We have logged in as {client.user}. Invite URL: {BOT_INVITE_URL}")
    await tree.sync()

@client.event
async def on_message(message):
    """An event handler triggered upon receiving a message."""
    if message.author == client.user:
        return

    api_key, assitant_id = fetch_llm_credentials()
    user_input = message.content

    if "asst_" in assitant_id:
        logger.info("Openai client created")
        openai.api_key = api_key
        OPENAI_CLIENT = openai.Client(api_key=api_key)
        logger.info(f"Message received: {user_input}")
        # Ensure the message is not empty
        if user_input:
            try:
                thread_id = thread_store_get(message.channel.id)
                print("Pulled thread id", thread_id)
                if not thread_id:
                    thread = OPENAI_CLIENT.beta.threads.create()
                    thread_id = thread.id
                    thread_store_put(message.channel.id, thread_id)
                # Call the chat functionality with the extracted user input
                await chat_functionality(OPENAI_CLIENT, message.channel, user_input, thread_id, assitant_id)
            except Exception as e:
                logger.exception(e)
                await message.channel.send(f"Failed to start chat: {str(e)}")
    else:
        await chat_functionality_gemini(user_input, message.channel, api_key, assitant_id)





async def chat_functionality_gemini(user_input, channel, api_key, assistant_id):
    """Perform chat functionality using OpenAI API."""
  
    import os
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')

    prompt = user_input
    response = model.generate_content(prompt)

    print(response.text) 

    # Send the assistant's response to the channel
    await channel.send(response.text)


async def chat_functionality(OPENAI_CLIENT, channel, user_input, thread_id, assitant_id):
    """ Perform chat functionality using OpenAI API."""
    # Configure OpenAI API
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
    await channel.send(assistant_message)



client.run(DISCORD_BOT_TOKEN)
