import os
import json
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest, UpdatePinnedMessageRequest
from telethon.tl.types import Message
from tqdm import tqdm

CONFIG_FILE = "config.json"
SESSION_FILE = "anon"
SENT_LOG = "sent_ids.txt"
ERROR_LOG = "errors.txt"

DEFAULT_CONFIG = {
    "api_id": '',
    "api_hash": "",
    "phone": "",
    "source_channel_id": ,
    "target_channel_id": 
}

def ensure_config_exists():
    if not os.path.exists(CONFIG_FILE):
        print("⚙️ config.json not found. Creating default one...")
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print("⚠️ Please edit 'config.json' and fill in your API credentials and channel IDs.")
        exit(1)

def load_json():
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
        if key not in config or not config[key]:
            raise KeyError(f"❌ Missing or invalid '{key}' in config.json. Please fill it correctly.")

    client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])

    source = await client.get_entity(config["source_channel_id"])
    target = await client.get_entity(config["target_channel_id"])

    open(SENT_LOG, "a").close()
    open(ERROR_LOG, "a").close()

    sent_ids = set()
    with open(SENT_LOG, "r") as f:
        for line in f:
            try:
                sent_ids.add(int(line.strip()))
            except:
                continue

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
                # Progress bars for media download/upload
                downloaded = []

                def download_cb(current, total):
                    if not downloaded:
                        downloaded.append(tqdm(total=total, desc="⬇️ Downloading", unit="B", unit_scale=True))
                    downloaded[0].n = current
                    downloaded[0].refresh()

                media = await client.download_media(msg, file=bytes, progress_callback=download_cb)

                if downloaded:
                    downloaded[0].close()

                uploaded = []

                def upload_cb(current, total):
                    if not uploaded:
                        uploaded.append(tqdm(total=total, desc="⬆️ Uploading", unit="B", unit_scale=True))
                    uploaded[0].n = current
                    uploaded[0].refresh()

                sent = await client.send_file(
                    target,
                    media,
                    caption=msg.message or "",
                    reply_to=None,
                    progress_callback=upload_cb
                )

                if uploaded:
                    uploaded[0].close()

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
