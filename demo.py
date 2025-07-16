import os
import json
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest, UpdatePinnedMessageRequest
from telethon.tl.types import Message
from tqdm import tqdm

CONFIG_FILE = "config"
SESSION_FILE = "anon"
SENT_LOG = "sent_ids.txt"
ERROR_LOG = "errors.txt"

# Ensure logs exist
open(SENT_LOG, "a").close()
open(ERROR_LOG, "a").close()


def load_json():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_json(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_error(msg):
    with open(ERROR_LOG, "a") as f:
        f.write(msg + "\n")


def ensure_config_exists():
    if not os.path.exists(CONFIG_FILE):
        print("🔧 Enter your Telegram API config:")
        config["api_id"] = int(input("API ID: "))
        config["api_hash"] = input("API Hash: ")
        config["phone"] = input("Phone number (with +91...): ")
        save_json(config)

async def premsingh():
    client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])

    
    change_all = input("🔧 Do you want to change config? (y/n): ").lower()
    if change_all == "y":
        print("👉 Full config edit selected.")
        config["api_id"] = int(input("API ID: "))
        config["api_hash"] = input("API Hash: ")
        config["phone"] = input("Phone number (with +91...): ")
        save_json(config)

    change_channels = input("🌀 Do you want to change source and target channels? (y/n): ").lower()
    if change_channels == "y":
        config = await update_config_interactively(client)

    return config, client


async def load_or_prompt_config():
    config = load_json()
    print("➡️ Checking config keys...")
    if all(k in config for k in ("api_id", "api_hash", "phone")):
        print("✅ All required keys exist.")
    else:
        print("❌ Missing one or more keys.")
        print("🔧 Enter your Telegram API config:")
        config["api_id"] = int(input("API ID: "))
        config["api_hash"] = input("API Hash: ")
        config["phone"] = input("Phone number (with +91...): ")
        save_json(config)

    client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])

    change_all = input("🔧 Do you want to change config? (y/n): ").lower()
    if change_all == "y":
        print("👉 Full config edit selected.")
        config["api_id"] = int(input("API ID: "))
        config["api_hash"] = input("API Hash: ")
        config["phone"] = input("Phone number (with +91...): ")
        save_json(config)

    change_channels = input("🌀 Do you want to change source and target channels? (y/n): ").lower()
    if change_channels == "y":
        config = await update_config_interactively(client)

    return config, client

