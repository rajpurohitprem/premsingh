import json
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load bot token
with open("bot.json") as f:
    bot_data = json.load(f)
BOT_TOKEN = bot_data["bot_token"]
CONFIG_FILE = "config.json"

# Save channel ID
def save_channel_id(key, chat_id):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    config[key] = chat_id
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Saved {key}: {chat_id}")

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    source_btn = KeyboardButton(
        text="Select Source Channel",
        request_chat=KeyboardButtonRequestChat(
            request_id=1,
            chat_is_channel=True
        )
    )
    target_btn = KeyboardButton(
        text="Select Target Channel",
        request_chat=KeyboardButtonRequestChat(
            request_id=2,
            chat_is_channel=True
        )
    )
    keyboard = [[source_btn], [target_btn]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    

# Handle chat_shared
async def chat_shared_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.chat_shared:
        return

    shared = update.message.chat_shared
    chat_id = shared.chat_id

    if shared.request_id == 1:
        save_channel_id("source_channel_id", chat_id)
        await update.message.reply_text(f"✅ Source channel saved:\n`{chat_id}`", parse_mode="Markdown")
    elif shared.request_id == 2:
        save_channel_id("target_channel_id", chat_id)
        await update.message.reply_text(f"✅ Target channel saved:\n`{chat_id}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Unknown request ID received.")

# Main (SYNC, not async!)
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, chat_shared_handler))
    app.run_polling()  # <--- ✅ synchronous version

if __name__ == "__main__":
    main()
