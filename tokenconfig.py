import json
import os

# File path
config_file = "bot.json"

# Load existing config if it exists
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        try:
            config = json.load(f)
            print("🔄 Existing configuration loaded.")
        except json.JSONDecodeError:
            print("⚠️ Existing bot.json is invalid. Starting fresh.")
            config = {}
else:
    config = {}

# Prompt for bot token (default to existing)
existing_token = config.get("bot_token", "")
bot_token = input(f"Enter bot token [{existing_token}]: ").strip()
if not bot_token:
    bot_token = existing_token

# Prompt for allowed user IDs (append to existing if present)
existing_users = set(config.get("allowed_users", []))
user_input = input("Enter allowed user IDs to add (comma-separated): ").strip()
try:
    new_users = {int(uid.strip()) for uid in user_input.split(",") if uid.strip()}
except ValueError:
    print("❌ Invalid user ID(s). Must be numeric.")
    exit(1)

# Merge users
allowed_users = sorted(existing_users.union(new_users))

# Update config
config["bot_token"] = bot_token
config["allowed_users"] = allowed_users

# Save updated config
with open(config_file, "w") as f:
    json.dump(config, f, indent=2)

print("✅ bot.json updated successfully.")
