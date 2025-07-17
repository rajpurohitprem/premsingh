@bot.on(events.NewMessage)
async def handler(event):
    if not is_authorized(event):
        await event.reply("🚫 You are not authorized to use this bot.")
        return

    message = event.raw_text.strip()

    # Update API ID
    if message.startswith("/api"):
        try:
            new_api_id = int(message.split(" ")[1])
            main_config["api_id"] = new_api_id
            save_json("config.json", main_config)
            await event.reply(f"✅ API ID updated to `{new_api_id}`")
        except Exception as e:
            await event.reply(f"⚠️ Failed to update API ID: {str(e)}")

    # Update API Hash
    elif message.startswith("/hash"):
        try:
            new_api_hash = message.split(" ")[1]
            main_config["api_hash"] = new_api_hash
            save_json("config.json", main_config)
            await event.reply(f"✅ API Hash updated to `{new_api_hash}`")
        except Exception as e:
            await event.reply(f"⚠️ Failed to update API Hash: {str(e)}")

    # Set Source Channel ID
    elif message.startswith("/set_source"):
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
            "/api `<new_api_id>` – Update API ID\n"
            "/hash `<new_api_hash>` – Update API Hash\n"
            "/set_source `-100xxxxxxxxx`\n"
            "/set_target `-100yyyyyyyyy`\n"
            "/run_clone – Run the cloner script\n\n"
            "_Only authorized users can use these commands._",
            parse_mode="markdown"
        )
