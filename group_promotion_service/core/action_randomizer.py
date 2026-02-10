import logging
import random
from typing import Dict


class ActionRandomizer:
    """Generate random action distributions per phase with constrained ranges"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_random_actions(self, phase: int, max_reactions: int = 10, max_replies: int = 5, max_posts: int = 2) -> Dict[str, int]:
        """
        Generate random action distribution for phase
        Returns: {"reactions": N, "replies": M, "posts": K, "link_posts": L}
        All values stay within defined ranges
        """
        
        if phase == 1:
            # Phase 1: Only reactions (0-10, but respect max)
            reactions = random.randint(0, min(10, max_reactions))
            return {
                "reactions": reactions,
                "replies": 0,
                "posts": 0,
                "link_posts": 0
            }
        
        elif phase == 2:
            # Phase 2: Reactions (0-8) + Replies (0-5)
            reactions = random.randint(0, min(8, max_reactions))
            replies = random.randint(0, min(5, max_replies))
            return {
                "reactions": reactions,
                "replies": replies,
                "posts": 0,
                "link_posts": 0
            }
        
        elif phase == 3:
            # Phase 3: Reactions (0-5) + Replies (0-3) + Posts (0-2)
            reactions = random.randint(0, min(5, max_reactions))
            replies = random.randint(0, min(3, max_replies))
            posts = random.randint(0, min(2, max_posts))
            return {
                "reactions": reactions,
                "replies": replies,
                "posts": posts,
                "link_posts": 0
            }
        
        elif phase >= 4:
            # Phase 4: Reactions (0-3) + Replies (0-2) + Posts (0-2) + Link Posts (0-1)
            reactions = random.randint(0, min(3, max_reactions))
            replies = random.randint(0, min(2, max_replies))
            posts = random.randint(0, min(2, max_posts))
            link_posts = random.randint(0, 1)  # 0 or 1
            return {
                "reactions": reactions,
                "replies": replies,
                "posts": posts,
                "link_posts": link_posts
            }
        
        else:
            # Fallback
            return {
                "reactions": 0,
                "replies": 0,
                "posts": 0,
                "link_posts": 0
            }
