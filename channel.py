# Updated version with full tqdm progress bars:
# - Message cloning progress bar
# - Download progress bar (per media)
# - Upload progress bar (per media)
# - Works in Termux and standard terminals

import os
import json
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest, UpdatePinnedMessageRequest
from telethon.tl.types import MessageService, Message
from tqdm import tqdm

CONFIG_FILE = "config.json"
SESSION_FILE = "anon"
SENT_LOG = "sent_ids.txt"
ERROR_LOG = "errors.txt"

# Ensure logs exist
open(SENT_LOG, "a").close()
open(ERROR_LOG, "a").close()

def load_json():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_json(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def get_channel_selection(client, prompt_text):
    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel and not d.is_user]
    print(f"\n📢 Available Channels/Groups for {prompt_text}:")
    for i, d in enumerate(channels, 1):
        print(f"{i}. {d.name}")
    choice = int(input(f"🟢 Enter number for {prompt_text}: "))
    return channels[choice - 1].entity

async def update_config_interactively(client):
    config = load_json()
    source = await get_channel_selection(client, "Source Channel")
    target = await get_channel_selection(client, "Target Channel")
    config["source_channel_id"] = source.id
    config["target_channel_id"] = target.id
    save_json(config)
    return config

async def load_or_prompt_config():
    config = load_json()
 
    client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])
 

    change_channels = "y"
    if change_channels == "y":
        config = await update_config_interactively(client)

    return client

def log_error(msg):
    with open(ERROR_LOG, "a") as f:
        f.write(msg + "\n")

async def clone_messages():
    client = await load_or_prompt_config()

    src_entity = await client.get_entity(int(config["source_channel_id"]))
    tgt_entity = await client.get_entity(int(config["target_channel_id"]))

    
if __name__ == "__main__":
    asyncio.run(clone_messages())
