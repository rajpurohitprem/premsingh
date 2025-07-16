import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, KeyboardButtonRequestChat
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Load bot token from bot.json
with open("bot.json") as f:
    bot_data = json.load(f)
BOT_TOKEN = bot_data["bot_token"]

CONFIG_FILE = "config.json"

def save_channel_id(key, chat_id):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    config[key] = chat_id
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Saved {key}: {chat_id}")

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
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text("Select source and target channels:", reply_markup=reply_markup)

async def chat_shared_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shared = update.message.chat_shared
    chat_id = shared.chat_id

    if shared.request_id == 1:
        save_channel_id("source_channel_id", chat_id)
        await update.message.reply_text(f"✅ Source channel saved: `{chat_id}`", parse_mode="Markdown")
    elif shared.request_id == 2:
        save_channel_id("target_channel_id", chat_id)
        await update.message.reply_text(f"✅ Target channel saved: `{chat_id}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Unknown request.")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatShared(), chat_shared_handler))  # ✅ FIXED
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
