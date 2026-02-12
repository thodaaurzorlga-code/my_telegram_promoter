import logging
from datetime import datetime, timezone


class PhaseDetector:
    """Detect group phase based on days since joining"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_phase(self, join_date_str: str) -> int:
        """Calculate phase (1-4) based on days since join"""
        try:
            join_date = datetime.fromisoformat(join_date_str)
            if join_date.tzinfo is None:
                join_date = join_date.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            days_active = (now - join_date).days
            
            if days_active <= 0:
                return 1
            elif days_active <= 10:
                return 2
            elif days_active <= 16:
                return 3
            else:
                return 4
        
        except Exception as e:
            self.logger.error(f"Error detecting phase: {e}")
            return 1
    
    def days_since_join(self, join_date_str: str) -> int:
        """Calculate days since joining"""
        try:
            join_date = datetime.fromisoformat(join_date_str)
            if join_date.tzinfo is None:
                join_date = join_date.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            return (now - join_date).days
        except:
            return 0
