"""Configuration management for Suna CLI."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages CLI configuration stored in ~/.suna/config.json"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".suna"
        self.config_file = self.config_dir / "config.json"
        self._config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    
    def _save(self):
        """Save configuration to file."""
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self._config[key] = value
        self._save()
    
    def delete(self, key: str):
        """Delete a configuration value."""
        if key in self._config:
            del self._config[key]
            self._save()
    
    def clear(self):
        """Clear all configuration."""
        self._config = {}
        self._save()
    
    def all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
    
    @property
    def api_key(self) -> Optional[str]:
        """Get API key from config or environment."""
        return self.get("api_key") or os.getenv("SUNA_API_KEY")
    
    @property
    def base_url(self) -> str:
        """Get base URL from config or use default."""
        return self.get("base_url", "http://localhost:8000")
    
    @property
    def default_workspace(self) -> Optional[str]:
        """Get default workspace."""
        return self.get("default_workspace")


# Global config instance
config = Config()
