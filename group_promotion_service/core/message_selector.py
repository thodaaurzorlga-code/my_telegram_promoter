import logging
import random
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional


class MessageSelector:
    """Handle message rotation and selection"""
    
    def __init__(self, group_manager=None):
        self.logger = logging.getLogger(__name__)
        self.group_manager = group_manager
        
        config_path = Path(__file__).parent.parent / "config" / "message_bank.yaml"
        with open(config_path, 'r',encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        self.message_history = {}  # Track last 7 days of messages per group
    
    def select_reply_message(self, entity: str) -> str:
        """Select random reply message with no-repeat policy"""
        available = self.config.get('reply_messages', [])
        
        if not available:
            return "thanks for sharing"
        
        # Use only session history for filtering
        all_used = list(set(self.message_history.get(entity, {}).get('replies', [])))
        
        # Filter messages not used in last k days
        candidates = [msg for msg in available if msg not in all_used]
        
        if not candidates:
            candidates = available
        
        selected = random.choice(candidates)
        self._record_message(entity, 'replies', selected)
        
        return selected
    
    def select_phase_3_post(self, entity: str) -> str:
        """Select random phase 3 post"""
        available = self.config.get('phase_3_posts', [])
        
        if not available:
            return "Check our community for daily job updates!"
        
        # Use only session history for filtering
        all_used = list(set(self.message_history.get(entity, {}).get('phase_3', [])))
        
        candidates = [msg for msg in available if msg not in all_used]
        
        if not candidates:
            candidates = available
        
        selected = random.choice(candidates)
        self._record_message(entity, 'phase_3', selected)
        
        return selected
    
    def select_phase_4_post(self, entity: str) -> str:
        """Select random phase 4 post (with links)"""
        available = self.config.get('phase_4_posts', [])
        
        if not available:
            return "Join our community for daily updates: https://t.me/Jobs_Lelo"
        
        # Use only session history for filtering
        all_used = list(set(self.message_history.get(entity, {}).get('phase_4', [])))
        
        candidates = [msg for msg in available if msg not in all_used]
        
        if not candidates:
            candidates = available
        
        selected = random.choice(candidates)
        self._record_message(entity, 'phase_4', selected)
        
        return selected
    
    def select_reaction_emoji(self) -> str:
        """Select random reaction emoji"""
        emojis = self.config.get('message_rotation', {}).get('reaction_emojis', ['👍'])
        return random.choice(emojis)
    
    def _record_message(self, entity: str, msg_type: str, message: str):
        """Record message sent to group (session only)"""
        # Session-level tracking
        if entity not in self.message_history:
            self.message_history[entity] = {
                'replies': [],
                'phase_3': [],
                'phase_4': [],
                'timestamps': []
            }
        
        if message not in self.message_history[entity][msg_type]:
            self.message_history[entity][msg_type].append(message)
        
        # Keep only last 20 in session
        if len(self.message_history[entity][msg_type]) > 20:
            self.message_history[entity][msg_type].pop(0)
        
        # persistent tracking removed; session-only history maintained
