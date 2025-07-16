import json
from telethon import TelegramClient, events

# Load bot token and allowed user IDs
with open("bot.json", "r") as f:
    bot_config = json.load(f)

bot = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_config["bot_token"])
allowed_users = bot_config.get("allowed_users", [])

# Access check
def is_authorized(event):
    return event.sender_id in allowed_users

@bot.on(events.NewMessage)
async def handler(event):
    if not is_authorized(event):
        await event.reply("❌ You are not authorized to use this bot.")
        return

    # Handle authorized commands
    if event.text.startswith("/set_source"):
        source_id = event.text.split(" ")[1].replace("-100", "")
        update_config("source_channel_id", source_id)
        await event.reply(f"✅ Source channel set to {source_id}")
    
    elif event.text.startswith("/set_target"):
        target_id = event.text.split(" ")[1].replace("-100", "")
        update_config("target_channel_id", target_id)
        await event.reply(f"✅ Target channel set to {target_id}")

    elif event.text.startswith("/run_clone"):
        import subprocess
        subprocess.Popen(["python", "clone.py"])
        await event.reply("▶️ Clone started...")

def update_config(key, value):
    with open("config.json", "r") as f:
        config = json.load(f)
    config[key] = value
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

print("🤖 Telegram bot running...")
bot.run_until_disconnected()
