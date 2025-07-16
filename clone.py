import os
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest, UpdatePinnedMessageRequest
from telethon.tl.types import Message
from tqdm import tqdm

# File constants
CONFIG_FILE = "config.json"
SESSION_FILE = "anon"
SENT_LOG = "sent_ids.txt"
ERROR_LOG = "errors.txt"

# Ensure log files exist
open(SENT_LOG, "a").close()
open(ERROR_LOG, "a").close()

def log_error(msg):
    with open(ERROR_LOG, "a") as f:
        f.write(msg + "\n")

def load_json():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_json(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def load_or_prompt_config():
    config = load_json()
    required_keys = ("api_id", "api_hash", "phone", "source_channel_id", "target_channel_id")

    if not all(k in config for k in required_keys):
        raise ValueError(f"Missing required config keys in {CONFIG_FILE}. Required keys: {required_keys}")

    client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])
    return config, client

async def clone_messages():
    try:
        config, client = await load_or_prompt_config()
    except Exception as e:
        print(f"❌ Config Load Failed: {e}")
        return

    try:
        def normalize_channel_id(cid):
            """
            Ensures channel ID starts with -100
            """
            cid = str(cid)
            return int(cid) if cid.startswith("-100") else int("-100" + cid)

        src_entity = await client.get_entity(normalize_channel_id(config["source_channel_id"]))
        tgt_entity = await client.get_entity(normalize_channel_id(config["target_channel_id"]))

    except Exception as e:
        print(f"❌ Failed to fetch source/target: {e}")
        return

    try:
        with open(SENT_LOG, "r") as f:
            sent_ids = set(map(int, f.read().split()))
    except Exception:
        sent_ids = set()

    offset_id = 0
    limit = 100
    all_messages = []

    print("📥 Fetching messages from source...")
    while True:
        history = await client(GetHistoryRequest(
            peer=src_entity,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        all_messages.extend(history.messages)
        offset_id = history.messages[-1].id

    all_messages.reverse()
    message_pbar = tqdm(total=len(all_messages), desc="Cloning messages")
    total_sent = 0

    for msg in all_messages:
        message_pbar.update(1)
        if not isinstance(msg, Message) or msg.id in sent_ids:
            continue

        try:
            if msg.media:
                file_size = {"value": 0}

                def download_callback(cur, total):
                    file_size["value"] = total
                    print(f"\r📥 Downloading {cur / 1024:.1f} KB / {total / 1024:.1f} KB", end="")

                file_path = await client.download_media(msg, progress_callback=download_callback)
                print()  # newline after download

                upload_bar = tqdm(total=file_size["value"], unit='B', unit_scale=True, desc="📤 Uploading")

                def upload_callback(sent, total):
                    upload_bar.update(sent - upload_bar.n)

                await client.send_file(
                    tgt_entity,
                    file_path,
                    caption=msg.text or msg.message or "",
                    progress_callback=upload_callback
                )
                upload_bar.close()
                os.remove(file_path)

            elif msg.text or msg.message:
                await client.send_message(tgt_entity, msg.text or msg.message)

            if msg.pinned:
                try:
                    await client(UpdatePinnedMessageRequest(
                        peer=tgt_entity,
                        id=msg.id,
                        silent=True
                    ))
                except:
                    pass

            with open(SENT_LOG, "a") as f:
                f.write(f"{msg.id}\n")

            total_sent += 1
            await asyncio.sleep(1)

        except Exception as e:
            log_error(f"Message ID {msg.id} failed: {str(e)}")

    message_pbar.close()
    print(f"\n✅ Cloning complete. {total_sent} messages sent.")

if __name__ == "__main__":
    asyncio.run(clone_messages())
