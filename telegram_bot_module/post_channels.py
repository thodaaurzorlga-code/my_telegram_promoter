from telethon.tl.functions.messages import SendMessageRequest
from pathlib import Path
from .telegram_client import TelegramClientManager
import asyncio

# ---------- CONFIG ----------
api_id = 39367448
api_hash = "4b9a7be7ded2eb99822fa7eef2f935c9"

# List of target groups (username or invite link)
target_groups = [
    "GroupUsername1",
    "GroupUsername2",
    "https://t.me/joinchat/xxxxxxx"
]

# The message you want to send
message_text = "Hello everyone! This is an automated message."

# Optional session config
module_dir = Path(__file__).parent
session_name = "session"
session_path = str(module_dir / session_name)

# ---------- TELEGRAM CLIENT ----------
client_mgr = TelegramClientManager(api_id, api_hash, session_name)

async def post_to_groups(groups: list, message: str):
    # Get client, initialize if needed
    client = client_mgr.get_client()
    if not client:
        await client_mgr.initialize()
        client = client_mgr.get_client()

    await client.start()

    for group in groups:
        try:
            entity = await client.get_entity(group)  # Resolve username or invite link
            await client(SendMessageRequest(
                peer=entity,
                message=message,
                no_webpage=True
            ))
            print(f"Message sent to {group}")
        except Exception as e:
            print(f"Failed to send to {group}: {e}")






# ---------- ENTRY POINT ----------
async def main():
    await post_to_groups(target_groups, message_text)

if __name__ == "__main__":
    asyncio.run(main())
