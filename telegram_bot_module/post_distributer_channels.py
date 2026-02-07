"""Compact Post Distributor"""
import logging
import asyncio
import random
from typing import List, Dict, Any
from .post_fetcher import Post


class PostDistributorChannels:
    """Distribute posts to destinations"""

    def __init__(self, client_manager, config):
        self.logger = logging.getLogger(__name__)
        self.client = client_manager
        self.config = config._config

    async def send_posts(self):
        """Send posts to all destinations"""
        posts=self.config["messages"]["fresher_jobs"]
        if not posts:
            return {"sent": 0, "failed": 0}

        # config = self.config.get_promotion_config()
        delay = 2
        
        stats = {"sent": 0, "failed": 0}
        
        for post in posts:
            for dest in self.config['sources']:
                if await self._send(post, dest['username']):
                    stats["sent"] += 1
                else:
                    stats["failed"] += 1
            delay=random.choice([0,0.5, 1.0, 1.5, 2.0])
            await asyncio.sleep(delay)
        
        self.logger.info(f"Distribution: {stats['sent']} sent, {stats['failed']} failed")
        return stats

    async def _send(self, post, dest: str, retries: int = 2) -> bool:
        for attempt in range(retries):
            try:
                await self.client.get_client().send_file(
                    dest,
                    post["path"],
                    caption=post["text"],
                    parse_mode="markdown"
                )
                self.logger.info(f"Sent to {dest}")
                return True

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1}: {e}")
                await asyncio.sleep(2)

        return False


