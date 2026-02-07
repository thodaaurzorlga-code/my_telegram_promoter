"""
Configuration Manager Module
Handles loading and managing configuration from YAML file
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional


class ConfigManager:
    """Manages configuration loading and access"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigManager

        Args:
            config_path: Path to config.yaml file. If None, looks in current directory
        """
        self.logger = logging.getLogger(__name__)
        
        # Determine config path
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        else:
            config_path = Path(__file__).parent / config_path

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        self.config_path = config_path
        self._config = self._load_config()
        self.logger.info(f"Configuration loaded from {config_path}")

    
    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            if config is None:
                raise ValueError("Config file is empty")
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

    def get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram API configuration"""
        return self.get("telegram", {})

    def get_sources(self) -> List[Dict[str, str]]:
        """Get list of source groups/channels"""
        return self.get("sources", [])

    def get_destinations(self) -> List[Dict[str, str]]:
        """Get list of destination groups/channels"""
        return self.get("destinations", [])

    def get_fetching_config(self) -> Dict[str, Any]:
        """Get fetching configuration"""
        return self.get("fetching", {})

    def get_posting_config(self) -> Dict[str, Any]:
        """Get posting configuration"""
        return self.get("posting", {})
    



    def validate(self) -> bool:
        """Validate configuration has required fields"""
        required = ["telegram", "sources", "destinations", "fetching", "posting"]
        for field in required:
            if field not in self._config:
                self.logger.error(f"Missing required config field: {field}")
                return False
        
        # Validate telegram config
        telegram = self.get_telegram_config()
        if not all(k in telegram for k in ["api_id", "api_hash", "session_name"]):
            self.logger.error("Missing required telegram credentials")
            return False

        # Validate sources and destinations
        if not self.get_sources():
            self.logger.error("No source groups/channels defined")
            return False
        
        if not self.get_destinations():
            self.logger.error("No destination groups/channels defined")
            return False

        self.logger.info("Configuration validation passed")
        return True

    def reload(self):
        self._config = self._load_config()
        self.logger.info("Configuration reloaded")
