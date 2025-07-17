import json

# Prompt for bot token
bot_token = input("Enter your bot token: ")

# Prompt for allowed user IDs (comma-separated)
user_input = input("Enter allowed user IDs (comma-separated): ")

# Convert string input to list of integers
try:
    allowed_users = [int(uid.strip()) for uid in user_input.split(',') if uid.strip()]
except ValueError:
    print("Invalid input. Please enter numeric user IDs separated by commas.")
    exit(1)

# Create config dictionary
config = {
    "bot_token": bot_token,
    "allowed_users": allowed_users
}

# Save to bot.json
with open("bot.json", "w") as f:
    json.dump(config, f, indent=2)

print("✅ bot.json file created successfully!")
