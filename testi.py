post="""https://careers.wipro.com/job/INTERNSHIP_2026/134556-en_US/

2024&2025&2026 batches eligible 👆🏻

Share link 👇👇 
https://t.me/join_Daily_Jobs_Placement_Update"""

import re

def handle_source_6(text: str) -> str:
        if not text:
            return ""

        cleaned = text

        # ❌ Remove Telegram invite/channel links (including your specific one)
        cleaned = re.sub(
            r"https?://(t\.me|telegram\.me)/join_Daily_Jobs_Placement_Update\S*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        # ❌ Remove lines like "Telegram link 👇👇"
        cleaned = re.sub(
            r"Telegram\s*link\s*👇+",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        # Normalize spacing
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

        return cleaned

print(handle_source_6(post))