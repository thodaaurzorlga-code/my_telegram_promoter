from telethon import TelegramClient
from .telegram_client import TelegramClientManager
from telethon.tl.functions.messages import GetHistoryRequest
from pathlib import Path

api_id= 39367448
api_hash= "4b9a7be7ded2eb99822fa7eef2f935c9"
username = "harshitmishra1508"  # @username OR phone number

# command to run the script:
# (.venv) D:\Desktop_C\OPEN SOURCE\telegram>python -m telegram_bot_module.fetch_chats
# 140

module_dir = Path(__file__).parent
session_name = "session"
session_path = str(module_dir / session_name)

client_mgr = TelegramClientManager(api_id, api_hash,session_name)

async def fetch_chats():
    client = client_mgr.get_client()
    if not client:
        await client_mgr.initialize()
        client = client_mgr.get_client()
    
    await client.start()
    user = await client.get_entity(username)

    offset_id = 0
    limit = 100
    all_messages = []

    while True:
        history = await client(GetHistoryRequest(
            peer=user,
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

        for msg in history.messages:
            # Extract text using raw_text property
            text = msg.raw_text if hasattr(msg, 'raw_text') and msg.raw_text else ""
            
            # Add media type info if message has media
            if msg.media:
                media_type = type(msg.media).__name__
                text = f"[{media_type}]" if not text else f"{text} [{media_type}]"
            
            all_messages.append({
                "sender": "me" if msg.out else "other",
                "text": text,
                "timestamp": msg.date.isoformat()
            })

        offset_id = history.messages[-1].id

    return all_messages
import asyncio

async def main():
    chats = await fetch_chats()
    print(len(chats))

    with open("chats.txt", "w", encoding="utf-8") as f:
        for message in chats:
            f.write(f"{message['timestamp']} - {message['sender']}: {message['text']}\n")


asyncio.run(main())

    