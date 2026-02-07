from telethon import TelegramClient
from telethon.errors import (
    ChatWriteForbiddenError,
    PeerFloodError,
    UserPrivacyRestrictedError,
    FloodWaitError
)
from datetime import timedelta, timezone, datetime
from pathlib import Path
import asyncio
from Free_API_Load_balancer import generate
from .telegram_client import TelegramClientManager
from .prompts import SYSTEM_PROMPT
api_id = 39367448
api_hash = "4b9a7be7ded2eb99822fa7eef2f935c9"
channel = "deloitte_exam_answers"
# channel = "jobsuser"

DAYS = 1
cutoff_date = datetime.now(timezone.utc) - timedelta(days=DAYS)

session_name = "session"
client_mgr = TelegramClientManager(api_id, api_hash, session_name)

MESSAGE_TEXT = "Hey Hi are you looking for placements or internships?"
DELAY_SECONDS = 60  # do NOT reduce

from telethon.tl.functions.messages import GetHistoryRequest

async def has_previous_conversation(client, user_id) -> bool:
    try:
        history = await client(GetHistoryRequest(
            peer=user_id,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=5,   # small & efficient
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            return False

        # check if user ever sent a message
        for msg in history.messages:
            if not msg.out:
                return True

        return False

    except:
        return False


async def fetch_full_conversation(client, user_id):
    messages = []
    offset_id = 0
    limit = 100

    while True:
        history = await client(GetHistoryRequest(
            peer=user_id,
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
            messages.append({
                "sender": "me" if msg.out else "other",
                "text": msg.raw_text or "",
                "timestamp": msg.date.isoformat() if msg.date else None
            })

        offset_id = history.messages[-1].id

    return messages



async def dm_users():
    client = client_mgr.get_client()
    if not client:
        await client_mgr.initialize()
        client = client_mgr.get_client()

    await client.start()
    me = await client.get_me()
    my_user_id = me.id
    print(f"My user ID: {my_user_id}")

    user_ids = set()

    # collect users from channel
    conversation_start_context={}
    async for msg in client.iter_messages(channel):
        if not msg.date or msg.date < cutoff_date:
            break
        if msg.sender_id  and msg.sender_id != my_user_id:
            # user_ids.add(msg.sender_id)
            # print(msg.text)

            conversation_start_context[msg.sender_id]=msg.text
    user_ids = set(conversation_start_context.keys())

    print(f"Collected {len(user_ids)} users")

    for user_id in user_ids:
        try:
            # ✅ check previous conversation
            has_chat = await has_previous_conversation(client, user_id)

            if not has_chat:
                print(f"⏭️ No previous chat with {user_id}")
                print(f"💬 Starting context: {conversation_start_context[user_id]}")
                # Generate AI response based on conversation context
                user_message=conversation_start_context[user_id]
                final_prompt = SYSTEM_PROMPT + "\nUser: " + user_message
                ai_response = generate(prompt=final_prompt, max_output_tokens=150)
                print(f"🤖 AI response: {ai_response}")

            # ✅ fetch full conversation
            # conversation = await fetch_full_conversation(client, user_id)
            # print(conversation)
            # print(f"📜 Fetched {len(conversation)} messages with {user_id}")

            # ✅ send message
            # await client.send_message(user_id, MESSAGE_TEXT)
            print(f"✅ Messaged {user_id}")

            await asyncio.sleep(DELAY_SECONDS)

        except UserPrivacyRestrictedError:
            print(f"❌ Privacy blocked {user_id}")

        except ChatWriteForbiddenError:
            print(f"❌ Cannot write to {user_id}")

        except PeerFloodError:
            print("🚨 PeerFloodError — STOPPING")
            break

        except FloodWaitError as e:
            print(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print(f"⚠️ Skipped {user_id}: {e}")

asyncio.run(dm_users())



