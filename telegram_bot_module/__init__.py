"""
Telegram Bot Module - Complete End-to-End Solution
Fetches posts from source groups/channels and distributes them to destination groups/channels
"""

__version__ = "1.0.0"
__author__ = "Telegram Bot Team"

from .config_manager import ConfigManager
from .telegram_client import TelegramClientManager
from .post_fetcher import PostFetcher
from .post_distributor import PostDistributor

__all__ = [
    "ConfigManager",
    "TelegramClientManager",
    "PostFetcher",
    "PostDistributor"
]
