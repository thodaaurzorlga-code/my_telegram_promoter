from datetime import datetime
import logging
import asyncio
import random
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent      # telegram_bot_module
PROJECT_ROOT = BASE_DIR.parent                 # telegram

CONFIG_FILE = BASE_DIR / "message_config.xlsx"



class PostDistributorChannels:
    """Distribute promotional posts using Excel config"""

    def __init__(self, client_manager):
        self.logger = logging.getLogger(__name__)
        self.client = client_manager

        # Load Excel
        self.df = pd.read_excel(CONFIG_FILE)

    async def send_posts(self):
        if self.df.empty:
            return {"sent": 0, "failed": 0}

        stats = {"sent": 0, "failed": 0}

        # 🎯 Filter rows within time window
        valid_rows = []
        now = datetime.now().time()

        for _, row in self.df.iterrows():
            time_period = str(row["Time Period"])
            start_str, end_str = time_period.split("-")
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()

            if start <= now <= end:
                valid_rows.append(row)

        if not valid_rows:
            self.logger.info("No posts in valid time window")
            return stats

        # 🎲 Pick ONE row randomly (Random No column is informational)
        post = random.choice(valid_rows)

        success = await self._send(post)
        if success:
            stats["sent"] += 1
        else:
            stats["failed"] += 1

        return stats

    async def _send(self, post, retries: int = 2) -> bool:
        dest = post["Destination"]
        text = str(post.get("Message", "")).strip()
        image_path = str(post.get("Image_Path", "")).strip()

        for attempt in range(retries):
            try:
                client = self.client.get_client()

                # 🖼️ Image + text
                if image_path:
                    full_path = PROJECT_ROOT / image_path
                    print(full_path)
                    if full_path.exists():
                        await client.send_file(
                            dest,
                            str(full_path),
                            caption=text,
                            parse_mode="markdown"
                        )
                    else:
                        self.logger.warning(f"Image not found: {full_path}")
                        await client.send_message(dest, text)

                # ✉️ Text-only
                else:
                    await client.send_message(dest, text)

                self.logger.info(f"Sent to {dest}")
                await asyncio.sleep(random.choice([4, 5, 6]))
                return True

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2)

        return False
