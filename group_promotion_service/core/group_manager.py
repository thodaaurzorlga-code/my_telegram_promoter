import logging
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List


class GroupManager:
    """Handle Excel-based group tracking and management"""
    
    def __init__(self, excel_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        
        if excel_path is None:
            excel_path = Path(__file__).parent.parent / "data" / "groups_progress.xlsx"
        
        self.excel_path = excel_path
        self._ensure_excel_exists()
        self.df = self._load_excel()
    
    def _ensure_excel_exists(self):
        """Create Excel if it doesn't exist"""
        if not self.excel_path.exists():
            self.excel_path.parent.mkdir(parents=True, exist_ok=True)
            
            df = pd.DataFrame(columns=[
                'username',
                'group_name',
                'join_date',
                'current_phase',
                'last_action_date',
                'time_ranges',
                'link_enabled',
                'reactions_count',
                'replies_count',
                'posts_count',
                'status',
                'reacted_message_ids',
                'replied_message_ids'
            ])
            df.to_excel(self.excel_path, index=False)
            self.logger.info(f"Created new Excel file: {self.excel_path}")
    
    def _load_excel(self) -> pd.DataFrame:
        """Load Excel into DataFrame"""
        try:
            dtype_spec = {
                'username': str,
                'group_name': str,
                'join_date': str,
                'current_phase': int,
                'last_action_date': str,
                'time_ranges': str,
                'link_enabled': bool,
                'reactions_count': int,
                'replies_count': int,
                'posts_count': int,
                'status': str,
                'reacted_message_ids': str,
                'replied_message_ids': str
            }
            df = pd.read_excel(self.excel_path, dtype=dtype_spec)
            return df
        except Exception as e:
            self.logger.error(f"Failed to load Excel: {e}")
            return pd.DataFrame()
    
    def _save_excel(self):
        """Save DataFrame to Excel"""
        try:
            self.df.to_excel(self.excel_path, index=False)
        except Exception as e:
            self.logger.error(f"Failed to save Excel: {e}")
    
    def add_group(self, username: str, group_name: str, time_ranges: str, link_enabled: bool = False) -> bool:
        """Add new group"""
        if self._group_exists(username):
            return False
        
        new_row = {
            'username': username,
            'group_name': group_name,
            'join_date': datetime.now(timezone.utc).isoformat(),
            'current_phase': 1,
            'last_action_date': None,
            'time_ranges': time_ranges,
            'link_enabled': link_enabled,
            'reactions_count': 0,
            'replies_count': 0,
            'posts_count': 0,
            'status': 'active',
            'reacted_message_ids': json.dumps([]),
            'replied_message_ids': json.dumps([])
        }
        
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self._save_excel()
        self.logger.info(f"Added group {group_name} ({username})")
        return True
    
    def _group_exists(self, username: str) -> bool:
        """Check if group already exists"""
        return (self.df['username'] == username).any()
    
    def get_all_groups(self) -> List[Dict]:
        """Get all active groups"""
        return self.df[self.df['status'] == 'active'].to_dict('records')
    
    def get_group(self, username: str) -> Optional[Dict]:
        """Get specific group by username"""
        groups = self.df[self.df['username'] == username].to_dict('records')
        return groups[0] if groups else None
    
    def update_last_action(self, username: str, action_type: str):
        """Update last action and increment counters"""
        mask = self.df['username'] == username
        self.df.loc[mask, 'last_action_date'] = datetime.now(timezone.utc).isoformat()
        
        if action_type == 'reaction':
            self.df.loc[mask, 'reactions_count'] = self.df.loc[mask, 'reactions_count'].astype(int) + 1
        elif action_type == 'reply':
            self.df.loc[mask, 'replies_count'] = self.df.loc[mask, 'replies_count'].astype(int) + 1
        elif action_type == 'post':
            self.df.loc[mask, 'posts_count'] = self.df.loc[mask, 'posts_count'].astype(int) + 1
        
        self._save_excel()
    
    def update_phase(self, username: str, phase: int):
        """Update group phase"""
        mask = self.df['username'] == username
        self.df.loc[mask, 'current_phase'] = phase
        self._save_excel()
    
    def reload(self):
        """Reload DataFrame from Excel"""
        self.df = self._load_excel()
    
    def add_reacted_message(self, username: str, message_id: int):
        """Track reacted message ID"""
        try:
            mask = self.df['username'] == username
            current = self.df.loc[mask, 'reacted_message_ids'].values[0] if mask.any() else '[]'
            
            if pd.isna(current) or current == '':
                ids = []
            else:
                ids = json.loads(current)
            
            if message_id not in ids:
                ids.append(message_id)
                self.df.loc[mask, 'reacted_message_ids'] = json.dumps(ids)
                self._save_excel()
        except Exception as e:
            self.logger.warning(f"Failed to track reacted message: {e}")
    
    def has_reacted_to_message(self, username: str, message_id: int) -> bool:
        """Check if already reacted to message"""
        try:
            mask = self.df['username'] == username
            if not mask.any():
                return False
            
            current = self.df.loc[mask, 'reacted_message_ids'].values[0]
            
            if pd.isna(current) or current == '':
                return False
            
            ids = json.loads(current)
            return message_id in ids
        except Exception as e:
            self.logger.warning(f"Failed to check reacted message: {e}")
            return False
    
    def add_replied_message(self, username: str, message_id: int):
        """Track replied message ID"""
        try:
            mask = self.df['username'] == username
            current = self.df.loc[mask, 'replied_message_ids'].values[0] if mask.any() else '[]'
            
            if pd.isna(current) or current == '':
                ids = []
            else:
                ids = json.loads(current)
            
            if message_id not in ids:
                ids.append(message_id)
                self.df.loc[mask, 'replied_message_ids'] = json.dumps(ids)
                self._save_excel()
        except Exception as e:
            self.logger.warning(f"Failed to track replied message: {e}")
    
    def has_replied_to_message(self, username: str, message_id: int) -> bool:
        """Check if already replied to message"""
        try:
            mask = self.df['username'] == username
            if not mask.any():
                return False
            
            current = self.df.loc[mask, 'replied_message_ids'].values[0]
            
            if pd.isna(current) or current == '':
                return False
            
            ids = json.loads(current)
            return message_id in ids
        except Exception as e:
            self.logger.warning(f"Failed to check replied message: {e}")
            return False
