import os
import json
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest, UpdatePinnedMessageRequest
from telethon.tl.types import Message
from tqdm import tqdm

CONFIG_FILE = "config.json"
SESSION_FILE = "anon"
SENT_LOG = "sent_ids.txt"
ERROR_LOG = "errors.txt"

DEFAULT_CONFIG = {
    "api_id": '',
    "api_hash": "",
    "phone": "",
    "source_channel_id": '',
    "target_channel_id":'' 
}

def ensure_config_exists():
    if not os.path.exists(CONFIG_FILE):
        print("⚙️ config.json not found. Creating default one...")
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print("⚠️ Please edit 'config.json' and fill in your API credentials and channel IDs.")
        exit(1)

def load_json():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_json(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_error(msg):
    with open(ERROR_LOG, "a") as f:
        f.write(msg + "\n")
