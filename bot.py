import json
import asyncio
from telethon import TelegramClient, events, Button
from telethon.tl.types import PeerChannel

# Load bot token and allowed users
with open("bot.json", "r") as f:
    bot_config = json.load(f)

BOT_TOKEN = bot_config["bot_token"]
ALLOWED_USERS = bot_config["allowed_users"]

API_ID = 123456  # Replace with your own
API_HASH = "your_api_hash_here"

CONFIG_FILE = "config.json"

bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def save_config(key, value):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    config[key] = value

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender_id not in ALLOWED_USERS:
        await event.respond("🚫 You are not authorized to use this bot.")
        return

    await event.respond(
        "👋 Welcome! Use the buttons below to set a channel:",
        buttons=[
            [Button.inline("Set Source Channel", b"set_source")],
            [Button.inline("Set Target Channel", b"set_target")]
        ]
    )

@bot.on(events.CallbackQuery(data=b"set_source"))
async def pick_source(event):
    await show_channel_picker(event, "source_channel_id")

@bot.on(events.CallbackQuery(data=b"set_target"))
async def pick_target(event):
    await show_channel_picker(event, "target_channel_id")

async def show_channel_picker(event, config_key):
    await event.answer("Please wait...")

    dialogs = await bot.get_dialogs()
    channels = [d for d in dialogs if d.is_channel and not d.is_user and d.entity.creator]

    if not channels:
        await event.respond("❌ No channels found where you're the creator/admin.")
        return

    buttons = []
    for ch in channels:
        buttons.append([Button.inline(f"{ch.name}", f"select_{config_key}_{ch.id}".encode())])

    await event.respond(f"📢 Choose a channel to set as `{config_key}`:", buttons=buttons)

@bot.on(events.CallbackQuery)
async def handle_channel_selection(event):
    data = event.data.decode()

    if data.startswith("select_source_channel_id_"):
        channel_id = data.replace("select_source_channel_id_", "")
        save_config("source_channel_id", int(channel_id))
        await event.edit(f"✅ Source Channel set: `{channel_id}`")

    elif data.startswith("select_target_channel_id_"):
        channel_id = data.replace("select_target_channel_id_", "")
        save_config("target_channel_id", int(channel_id))
        await event.edit(f"✅ Target Channel set: `{channel_id}`")

if __name__ == "__main__":
    print("🤖 Bot is running...")
    asyncio.run(bot.run_until_disconnected())
