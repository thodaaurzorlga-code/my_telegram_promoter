from datetime import timedelta, timezone,datetime
from telethon import TelegramClient
from .telegram_client import TelegramClientManager
from telethon.tl.functions.messages import GetHistoryRequest
from pathlib import Path
import asyncio

api_id= 39367448
api_hash= "4b9a7be7ded2eb99822fa7eef2f935c9"
channel = "leetcode_answers"  # @username OR phone number

DAYS = 10
cutoff_date = datetime.now(timezone.utc) - timedelta(days=DAYS)
# command to run the script:
# (.venv) D:\Desktop_C\OPEN SOURCE\telegram>python -m telegram_bot_module.fetch_channel_chats
# 140

module_dir = Path(__file__).parent
session_name = "session"
session_path = str(module_dir / session_name)

client_mgr = TelegramClientManager(api_id, api_hash,session_name)

async def fetch_channel_messages():
    client = client_mgr.get_client()
    if not client:
        await client_mgr.initialize()
        client = client_mgr.get_client()
    
    await client.start()
    messages = []

    async for msg in client.iter_messages(channel):
        if not msg.date or msg.date < cutoff_date:
            break
        messages.append({
            "message_id": msg.id,
            "text": msg.text,
            "timestamp": msg.date.isoformat() if msg.date else None,
            "sender id": msg.sender_id,
            "sender_username": (
                msg.sender.username
                if msg.sender and msg.sender.username
                else None
            )
        })

    return messages


async def main():
    chats = await fetch_channel_messages()
    print(len(chats))

    with open("chats_channel.txt", "w", encoding="utf-8") as f:
        for message in chats:
            f.write(f"{message['timestamp']} - {message['sender_username']}: {message['text']} (Sender ID: {message['sender id']})\n")


asyncio.run(main())
