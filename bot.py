import json
import subprocess
from telethon import TelegramClient, events

# Load config from JSON
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Load bot config and Telegram API credentials
bot_config = load_json("bot.json")  # Must contain 'bot_token' and 'allowed_users'
main_config = load_json("config.json")  # Will be updated with source/target

# Your Telegram API ID and HASH (should already be in config.json)
api_id = main_config["api_id"]
api_hash = main_config["api_hash"]
bot_token = bot_config["bot_token"]
allowed_users = bot_config.get("allowed_users", [])

# Start the bot
bot = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)

# Access check
def is_authorized(event):
    return event.sender_id in allowed_users

# Handle messages
@bot.on(events.NewMessage)
async def handler(event):
    if not is_authorized(event):
        await event.reply("🚫 You are not authorized to use this bot.")
        return

    message = event.raw_text.strip()

    # Set Source Channel ID
    if message.startswith("/set_source"):
        try:
            source_id = message.split(" ")[1].replace("-100", "")
            main_config["source_channel_id"] = int(source_id)
            save_json("config.json", main_config)
            await event.reply(f"✅ Source channel set to: `{source_id}`")
        except Exception as e:
            await event.reply(f"⚠️ Error: {str(e)}")

    # Set Target Channel ID
    elif message.startswith("/set_target"):
        try:
            target_id = message.split(" ")[1].replace("-100", "")
            main_config["target_channel_id"] = int(target_id)
            save_json("config.json", main_config)
            await event.reply(f"✅ Target channel set to: `{target_id}`")
        except Exception as e:
            await event.reply(f"⚠️ Error: {str(e)}")

    # Run Cloner
    elif message.startswith("/run_clone"):
        await event.reply("▶️ Starting clone.py...")
        try:
            subprocess.Popen(["python", "clone.py"])
        except Exception as e:
            await event.reply(f"❌ Failed to run clone.py: {str(e)}")

    # Help
    elif message.startswith("/start") or message.startswith("/help"):
        await event.reply(
            "🤖 *Telegram Clone Bot*\n\n"
            "/set_source `-100xxxxxxxxx`\n"
            "/set_target `-100yyyyyyyyy`\n"
            "/run_clone – Run the cloner script\n\n"
            "_Only authorized users can use these commands._",
            parse_mode="markdown"
        )

# Run bot
print("🤖 Bot is running...")
bot.run_until_disconnected()
