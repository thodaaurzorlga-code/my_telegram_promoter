import logging
import asyncio
import yaml
from pathlib import Path
from .core import (
    GroupManager, PhaseDetector, ScheduleChecker, MessageSelector,
    ActionRandomizer, TrustBuilder, MessagePoster
)


class GroupPromotionService:
    """Main service for group promotion and trust building"""
    
    def __init__(self, client_manager):
        self.logger = logging.getLogger(__name__)
        self.client_manager = client_manager
        
        self.group_manager = GroupManager()
        self.phase_detector = PhaseDetector()
        self.schedule_checker = ScheduleChecker()
        self.message_selector = MessageSelector(self.group_manager)
        self.action_randomizer = ActionRandomizer()
        self.trust_builder = TrustBuilder(client_manager, self.group_manager, self.message_selector)
        self.message_poster = MessagePoster(client_manager, self.group_manager, self.message_selector)
        
        self._load_config()
    
    def _load_config(self):
        """Load promotion groups config"""
        config_path = Path(__file__).parent / "config" / "promotion_groups.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.config = {'groups': []}
    
    async def run(self):
        """Main execution loop"""
        self.logger.info("Starting Group Promotion Service")
        
        # Load all groups from config
        groups = self.config.get('groups', [])
        
        if not groups:
            self.logger.info("No groups configured")
            return
        
        for group_cfg in groups:
            username = group_cfg.get('username')
            group_name = group_cfg.get('name')
            
            if not username:
                continue
            
            try:
                # Add group if not exists
                if not self.group_manager.get_group(username):
                    time_ranges_str = str(group_cfg.get('time_ranges', []))
                    self.group_manager.add_group(
                        username, group_name,
                        time_ranges_str,
                        group_cfg.get('link_enabled', False)
                    )
                
                # Check if group should be processed now
                if not self.schedule_checker.is_in_schedule(group_cfg.get('time_ranges', [])):
                    self.logger.info(f"Group {group_name} not in schedule now")
                    continue
                
                # Get group data and detect phase
                group = self.group_manager.get_group(username)
                phase = self.phase_detector.get_phase(group['join_date'])
                
                # Update phase if changed
                if phase != group['current_phase']:
                    self.group_manager.update_phase(username, phase)
                
                # Execute actions based on phase
                await self._execute_phase_actions(
                    username, phase,
                    group_cfg.get('max_reactions_per_day', 10),
                    group_cfg.get('max_replies_per_day', 5)
                )
                
            except Exception as e:
                self.logger.error(f"Error processing group {group_name}: {e}")
            
            await asyncio.sleep(2)
        
        self.logger.info("Group Promotion Service completed")
    
    async def _execute_phase_actions(self, username: str, phase: int, max_reactions: int, max_replies: int):
        """Execute randomized actions based on group phase"""
        try:
            # Get random action distribution for this phase
            actions = self.action_randomizer.get_random_actions(
                phase, max_reactions, max_replies, 2
            )
            
            self.logger.info(
                f"Phase {phase} random actions for {username}: {actions['reactions']} reactions, "
                f"{actions['replies']} replies, {actions['posts']} posts, "
                f"{actions['link_posts']} link_posts"
            )
            
            # Execute reactions
            for _ in range(actions['reactions']):
                await self.trust_builder.phase_1_react(username, max_reactions=1)
                await asyncio.sleep(1)
            
            # Execute replies
            for _ in range(actions['replies']):
                await self.trust_builder.phase_2_reply(username, max_replies=1)
                await asyncio.sleep(1)
            
            # Execute posts (promotional text)
            for _ in range(actions['posts']):
                await self.message_poster.phase_3_post(username)
                await asyncio.sleep(2)
            
            # Execute link posts
            for _ in range(actions['link_posts']):
                await self.message_poster.phase_4_post(username)
                await asyncio.sleep(2)
        
        except Exception as e:
            self.logger.error(f"Error executing phase {phase} for group {username}: {e}")
