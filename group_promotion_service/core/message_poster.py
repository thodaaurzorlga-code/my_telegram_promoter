import logging
import asyncio
import re
from pathlib import Path
from typing import Dict, Tuple
from .message_selector import MessageSelector


class MessagePoster:
    """Handle Phase 3-4 actions: posting promotional messages"""
    
    def __init__(self, client_manager, group_manager, message_selector: MessageSelector):
        self.logger = logging.getLogger(__name__)
        self.client_manager = client_manager
        self.group_manager = group_manager
        self.message_selector = message_selector
    
    async def phase_3_post(self, entity: str) -> Dict[str, int]:
        """Phase 3: Post promotional text (no links)"""
        stats = {"posted": 0, "failed": 0}
        
        try:
            message = self.message_selector.select_phase_3_post(entity)
            
            if await self._send_message(entity, message):
                self.group_manager.update_last_action(entity, 'post')
                stats['posted'] += 1
            else:
                stats['failed'] += 1
        
        except Exception as e:
            self.logger.error(f"Error in phase_3_post: {e}")
        
        self.logger.info(f"Phase 3 post: {stats['posted']} posted, {stats['failed']} failed")
        return stats
    
    async def phase_4_post(self, entity: str) -> Dict[str, int]:
        """Phase 4: Post with links + assets"""
        stats = {"posted": 0, "failed": 0, "assets_sent": 0}
        
        group = self.group_manager.get_group(entity)
        
        if not group or not group.get('link_enabled'):
            self.logger.info(f"Links disabled for group {entity}")
            return stats
        
        try:
            # Get promotional message with potential asset
            message = self.message_selector.select_phase_4_post(entity)
            
            # Parse message for asset
            clean_message, asset_filename = self._extract_asset(message)
            
            # Send message with asset (if present) or just message
            if asset_filename:
                if await self._send_message_with_asset(entity, clean_message, asset_filename):
                    self.group_manager.update_last_action(entity, 'post')
                    stats['posted'] += 1
                    stats['assets_sent'] += 1
                else:
                    stats['failed'] += 1
            else:
                if await self._send_message(entity, clean_message):
                    self.group_manager.update_last_action(entity, 'post')
                    stats['posted'] += 1
                else:
                    stats['failed'] += 1
        
        except Exception as e:
            self.logger.error(f"Error in phase_4_post: {e}")
        
        self.logger.info(f"Phase 4 post: {stats['posted']} posted, {stats['assets_sent']} assets sent, {stats['failed']} failed")
        return stats
    
    async def _send_message(self, entity: str, message: str) -> bool:
        """Send message to group"""
        client = self.client_manager.get_client()
        try:
            await client.send_message(entity, message)
            self.logger.info(f"Posted to {entity}: {message[:50]}...")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to post to {entity}: {e}")
            return False
    
    async def _send_message_with_asset(self, entity: str, message: str, asset_filename: str) -> bool:
        """Send message with asset file as caption"""
        client = self.client_manager.get_client()
        try:
            assets_root = Path(__file__).resolve().parents[2]
            asset_path = assets_root / "assets" / asset_filename
            
            if not asset_path.exists():
                self.logger.warning(f"Asset file not found: {asset_path}")
                return False
            
            await client.send_file(entity, str(asset_path), caption=message)
            self.logger.info(f"Posted to {entity} with asset {asset_filename}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send message with asset to {entity}: {e}")
            return False
    
    def _extract_asset(self, message: str) -> Tuple[str, str]:
        """Extract asset filename from message and clean the message
        Format: [ASSET: filename.ext]
        Returns: (clean_message, asset_filename)
        """
        pattern = r'\[ASSET:\s*([^\]]+)\]'
        match = re.search(pattern, message)
        
        if match:
            asset_filename = match.group(1).strip()
            clean_message = re.sub(pattern, '', message).strip()
            return clean_message, asset_filename
        
        return message, None
