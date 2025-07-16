import json
from telethon import TelegramClient, events
import glob
import os

def cleanup_journals():
    for file in glob.glob("*.session*journal"):
        try:
            os.remove(file)
        except Exception as e:
            print(f"Could not delete {file}: {e}")

# Load bot token and allowed users
with open("bot.json", "r") as f:
    bot_data = json.load(f)

bot_token = bot_data["bot_token"]
allowed_users = bot_data["allowed_users"]

# Load API credentials
with open("config.json", "r") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
phone = config["phone"]

BOT_SESSION = "bot"
USER_SESSION = "anon"

bot = TelegramClient(BOT_SESSION, api_id, api_hash).start(bot_token=bot_token)
anon = TelegramClient(USER_SESSION, api_id, api_hash)

@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    await event.reply("👋 Use /login to receive OTP. Then send `/code 1 2 3 4 5` format to sign in.")

@bot.on(events.NewMessage(pattern="/login"))
async def login_handler(event):
    if event.sender_id not in allowed_users:
        return await event.reply("🚫 Not authorized.")
    try:
        await anon.connect()
        if await anon.is_user_authorized():
            return await event.reply("✅ Already logged in.")
        await anon.send_code_request(phone)
        await event.reply("📨 OTP sent. Send it in `/code 1 2 3 4 5` format.")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern=r"/code((\s\d){5})"))
async def code_handler(event):
    if event.sender_id not in allowed_users:
        return await event.reply("🚫 Not authorized.")

    try:
        # Extract digits from spaced input like: /code 1 2 3 4 5
        raw_text = event.message.message
        digits = "".join(filter(str.isdigit, raw_text))
        if len(digits) != 5:
            return await event.reply("❌ Invalid format. Send exactly 5 digits.")

        await anon.sign_in(phone, digits)
        await event.reply("✅ Logged in. `anon.session` saved.")
        cleanup_journals()
    except Exception as e:
        await event.reply(f"❌ Login failed: {e}")
        cleanup_journals()

@bot.on(events.NewMessage(pattern="/logout"))
async def logout_handler(event):
    if event.sender_id not in allowed_users:
        return await event.reply("🚫 Not authorized.")
        cleanup_journals()
    try:
        await anon.log_out()
        await event.reply("✅ Logged out.")
        for ext in [".session", ".session-journal"]:
            file = USER_SESSION
            if os.path.exists(file):
                os.remove(file)
    except Exception as e:
        await event.reply(f"❌ Logout error: {e}")
        cleanup_journals()

import os; os.remove("anon.session_journal") if os.path.exists("anon.session_journal") else None

print("🤖 Bot is running...")
bot.run_until_disconnected()
