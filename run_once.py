#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telegram_bot_module.main import TelegramBot

def run():
    asyncio.run(TelegramBot().run_once())

if __name__ == "__main__":
    run()
