import os
import json
import asyncio
from telethon import TelegramClient

CONFIG_FILE = "config.json"
SESSION_FILE = "anon"

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

async def update_channels_only():
    config = load_json()
    
    if not all(k in config for k in ("api_id", "api_hash", "phone")):
        print("❌ Missing required API credentials in config.json.")
        return

    client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])

    source = await get_channel_selection(client, "Source Channel")
    target = await get_channel_selection(client, "Target Channel")

    config["source_channel_id"] = source.id
    config["target_channel_id"] = target.id
    save_json(config)

    print("✅ Channels updated in config.json")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(update_channels_only())
