import asyncio
import json
from telethon import TelegramClient, events
from subprocess import run

CONFIG_FILE = "config.json"
BOT_FILE = "bot.json"

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Load config and bot token separately
config = load_json(CONFIG_FILE)
bot_info = load_json(BOT_FILE)

bot = TelegramClient("bot", config["api_id"], config["api_hash"]).start(bot_token=bot_info["bot_token"])
anon = TelegramClient("anon", config["api_id"], config["api_hash"])

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond("🤖 Welcome! Use /set_source, /set_target, or /start_clone")

@bot.on(events.NewMessage(pattern="/set_source (.+)"))
async def set_source(event):
    username = event.pattern_match.group(1)
    await anon.start()
    try:
        entity = await anon.get_entity(username)
        config["source_channel_id"] = entity.id
        save_json(config, CONFIG_FILE)
        await event.respond(f"✅ Source channel set to: `{username}` (ID: {entity.id})")
    except Exception as e:
        await event.respond(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern="/set_target (.+)"))
async def set_target(event):
    username = event.pattern_match.group(1)
    await anon.start()
    try:
        entity = await anon.get_entity(username)
        config["target_channel_id"] = entity.id
        save_json(config, CONFIG_FILE)
        await event.respond(f"✅ Target channel set to: `{username}` (ID: {entity.id})")
    except Exception as e:
        await event.respond(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern="/start_clone"))
async def start_clone(event):
    await event.respond("🚀 Cloning started. Please wait...")
    result = run(["python", "clone.py"])
    if result.returncode == 0:
        await event.respond("✅ Cloning completed successfully.")
    else:
        await event.respond("❌ Cloning failed. Check logs or try again.")

print("🤖 Telegram bot running...")
bot.run_until_disconnected()
