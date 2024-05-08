from dotenv import load_dotenv
import os
import dacite
import yaml
from typing import Dict, List, Literal
import sqlite3
from base import Config

load_dotenv()


def fetch_llm_credentials():
    conn = sqlite3.connect('db connection file')
    cursor = conn.cursor()

    # Execute the SQL query to retrieve the most recent record from llm_bot_discordbotconfig table
    cursor.execute("SELECT * FROM llm_bot_discordbotconfig ORDER BY created_at DESC LIMIT 1")
    most_recent_record = cursor.fetchone()

    # Check if there's any record returned
    if most_recent_record:
        llm_config_id = most_recent_record[4]
        llm_agent_id = most_recent_record[5]

        # Execute SQL queries to fetch api_key and assistant_id
        cursor.execute("SELECT api_key FROM llm_bot_llmconfig WHERE page_ptr_id = ?", (llm_config_id,))
        api_key = cursor.fetchone()[0]  # Assuming api_key is in the first column

        cursor.execute("SELECT assistant_id FROM llm_bot_llmagent WHERE id = ?", (llm_agent_id,))
        assistant_id = cursor.fetchone()[0]  # Assuming assistant_id is in the first column

        # Now you have both api_key and assistant_id
        print("API Key:", api_key)
        print("Assistant ID:", assistant_id)

    else:
        print("No records found.")

    # Close cursor and connection
    cursor.close()
    conn.close()

    return api_key, assistant_id

def fetch_telegram_credentials():
    conn = sqlite3.connect('db connection file')
    cursor = conn.cursor()

    # Execute the SQL query to retrieve the most recent record from llm_bot_discordbotconfig table
    cursor.execute("SELECT * FROM llm_bot_telegrambotconfig ORDER BY created_at DESC LIMIT 1")
    most_recent_record = cursor.fetchone()
    telegram_bot_token = most_recent_record[1]

    # Check if there's any record returned
    if most_recent_record:
        print("Here is most_recent_record", most_recent_record)
        llm_config_id = most_recent_record[3]
        llm_agent_id = most_recent_record[4]

        # Execute SQL queries to fetch api_key and assistant_id
        cursor.execute("SELECT api_key FROM llm_bot_llmconfig WHERE page_ptr_id = ?", (llm_config_id,))
        api_key = cursor.fetchone()[0]  # Assuming api_key is in the first column

        cursor.execute("SELECT assistant_id FROM llm_bot_llmagent WHERE id = ?", (llm_agent_id,))
        assistant_id = cursor.fetchone()[0]  # Assuming assistant_id is in the first column

        # Now you have both api_key and assistant_id
        print("API Key:", api_key)
        print("Assistant ID:", assistant_id)

    else:
        print("No records found.")

    # Close cursor and connection
    cursor.close()
    conn.close()

    return api_key, assistant_id, telegram_bot_token




# load config.yaml
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG: Config = dacite.from_dict(
    Config, yaml.safe_load(open(os.path.join(SCRIPT_DIR, "config.yaml"), "r"))
)

BOT_NAME = CONFIG.name
BOT_INSTRUCTIONS = CONFIG.instructions
EXAMPLE_CONVOS = CONFIG.example_conversations



DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")



SERVER_TO_MODERATION_CHANNEL: Dict[int, int] = {}


# Send Messages, Create Public Threads, Send Messages in Threads, Manage Messages, Manage Threads, Read Message History, Use Slash Command
BOT_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=328565073920&scope=bot"

MODERATION_VALUES_FOR_BLOCKED = {
    "harassment": 0.5,
    "harassment/threatening": 0.1,
    "hate": 0.5,
    "hate/threatening": 0.1,
    "self-harm": 0.2,
    "self-harm/instructions": 0.5,
    "self-harm/intent": 0.7,
    "sexual": 0.5,
    "sexual/minors": 0.2,
    "violence": 0.7,
    "violence/graphic": 0.8,
}

MODERATION_VALUES_FOR_FLAGGED = {
    "harassment": 0.5,
    "harassment/threatening": 0.1,
    "hate": 0.4,
    "hate/threatening": 0.05,
    "self-harm": 0.1,
    "self-harm/instructions": 0.5,
    "self-harm/intent": 0.7,
    "sexual": 0.3,
    "sexual/minors": 0.1,
    "violence": 0.1,
    "violence/graphic": 0.1,
}

SECONDS_DELAY_RECEIVING_MSG = (
    3  # give a delay for the bot to respond so it can catch multiple messages
)
MAX_THREAD_MESSAGES = 200
ACTIVATE_THREAD_PREFX = "💬✅"
INACTIVATE_THREAD_PREFIX = "💬❌"
MAX_CHARS_PER_REPLY_MSG = (
    1500  # discord has a 2k limit, we just break message into 1.5k
)

AVAILABLE_MODELS = Literal["gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview", "gpt-4-32k"]
