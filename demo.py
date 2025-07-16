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

DEFAULT_CONFIG = {
    "api_id": 0,
    "api_hash": "your_api_hash",
    "phone": "+91xxxxxxxxxx",
    "source_channel_id": -1001234567890,
    "target_channel_id": -1009876543210
}

def ensure_config_exists():
    if not os.path.exists(CONFIG_FILE):
        print("⚙️ config.json not found. Creating default one...")
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print("⚠️ Please edit 'config.json' and fill in your API credentials and channel IDs.")
        exit(1)

# Ensure logs exist
open(SENT_LOG, "a").close()
open(ERROR_LOG, "a").close()

def load_json():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("❌ config.json not found. Please create it with api_id, api_hash, phone, source_channel_id, target_channel_id.")
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_json(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_error(msg):
    with open(ERROR_LOG, "a") as f:
        f.write(msg + "\n")

async def main():
    config = load_json()
    required_keys = ["api_id", "api_hash", "phone", "source_channel_id", "target_channel_id"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"❌ Missing '{key}' in config.json. Please fill it manually before running.")

    client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])

    source = await client.get_entity(config["source_channel_id"])
    target = await client.get_entity(config["target_channel_id"])

    sent_ids = set()
    with open(SENT_LOG, "r") as f:
        for line in f:
            sent_ids.add(int(line.strip()))

    total = 0
    all_msgs = []
    last_id = 0
    print("📥 Fetching messages from source...")
    while True:
        history = await client(GetHistoryRequest(
            peer=source,
            limit=100,
            offset_id=last_id,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))
        messages = history.messages
        if not messages:
            break
        all_msgs.extend(messages)
        last_id = messages[-1].id
        if len(messages) < 100:
            break

    all_msgs = [m for m in all_msgs if isinstance(m, Message) and m.id not in sent_ids]
    all_msgs.sort(key=lambda m: m.id)
    print(f"🔁 Cloning {len(all_msgs)} new messages...")

    for msg in tqdm(all_msgs, desc="📤 Copying Messages", unit="msg"):
        try:
            if msg.media:
                file_path = await client.download_media(msg, file=bytes, progress_callback=lambda c, t: tqdm.update(c))
                sent = await client.send_file(target, file_path, caption=msg.message or "", reply_to=None, progress_callback=lambda c, t: tqdm.update(c))
            else:
                sent = await client.send_message(target, msg.text or "", reply_to=None)

            with open(SENT_LOG, "a") as f:
                f.write(f"{msg.id}\n")

            if msg.pinned:
                await client(UpdatePinnedMessageRequest(peer=target, id=sent.id, silent=True))

        except Exception as e:
            log_error(f"❌ Failed to copy msg {msg.id}: {str(e)}")

    print("✅ Done copying all messages.")

if __name__ == "__main__":
    ensure_config_exists()
    asyncio.run(main())

