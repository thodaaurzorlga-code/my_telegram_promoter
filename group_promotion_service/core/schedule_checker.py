import logging
from datetime import datetime, timezone
import json


class ScheduleChecker:
    """Check if current time matches group's time ranges"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def is_in_schedule(self, time_ranges_str: str) -> bool:
        """Check if current UTC time is in any of the group's time ranges"""
        try:
            now_utc = datetime.now(timezone.utc)
            current_hour = now_utc.hour
            current_minute = now_utc.minute
            current_time = current_hour * 60 + current_minute  # Convert to minutes
            
            # Parse time_ranges (format: "HH:MM-HH:MM" or JSON list)
            time_ranges = self._parse_time_ranges(time_ranges_str)
            print(f"Current UTC time: {now_utc.strftime('%H:%M')}, Time ranges: {time_ranges}")
            
            for time_range in time_ranges:
                # time_range = time_range.replace(' UTC', '').strip()

                start_str, end_str = time_range.split('-')
                start_h, start_m = map(int, start_str.split(':'))
                end_h, end_m = map(int, end_str.split(':'))
                
                start_time = start_h * 60 + start_m
                end_time = end_h * 60 + end_m
                print(f"Checking range {start_str}-{end_str} against current time {now_utc.strftime('%H:%M')}")
                if start_time <= current_time < end_time:
                    return True
            
            return False
        
        except Exception as e:
            self.logger.warning(f"Error checking schedule: {e}")
            return False
    
    def _parse_time_ranges(self, time_ranges_str) -> list:
        """Parse time ranges from string, list, or JSON"""
        try:
            # Already a list
            if isinstance(time_ranges_str, list):
                return time_ranges_str
            
            # Try JSON format
            if isinstance(time_ranges_str, str) and time_ranges_str.startswith('['):
                return json.loads(time_ranges_str)
            
            # Single range string
            if isinstance(time_ranges_str, str) and '-' in time_ranges_str:
                return [time_ranges_str]
            
            return []
        except:
            return []
