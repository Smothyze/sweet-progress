import json
import os
from typing import Dict, List, Tuple, Optional, Any
from utils.path_utils import replace_username_in_path
from utils.resource_utils import CONFIG_PATH, RESOURCE_DIR
from utils.logger import logger
from utils.exceptions import ConfigError
from utils.constants import MAX_RECENT_GAMES
import uuid

class ConfigManager:
    def __init__(self):
        self.config_file = CONFIG_PATH
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "games": {},
            "last_used": {},
            "backup_history": {},  
            "preferences": {
                "path_display": "Auto",
                "timestamp_option": "Disable",
                "save_output_directory": False
            }
        }
        
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding='utf-8') as f:
                    config = json.load(f)
                    
                # MIGRATION: If using the old format (based on game_title), migrate to the new format (based on id)
                if config.get("games") and all(isinstance(v, dict) and "id" not in v for v in config["games"].values()):
                    migrated_games = {}
                    for game_title, game_data in config["games"].items():
                        new_id = str(uuid.uuid4())
                        migrated_games[new_id] = {
                            "id": new_id,
                            "game_title": game_title,
                            "savegame_location": game_data.get("savegame_location", ""),
                            "backup_location": game_data.get("backup_location", "")
                        }
                    config["games"] = migrated_games
                    self.save_config_migrated(config)
                
                # Ensure every entry has an id and game_title
                for gid, game in config["games"].items():
                    if "id" not in game:
                        game["id"] = gid
                    if "game_title" not in game:
                        game["game_title"] = gid
                
                for game in config["games"]:
                    game_config = config["games"][game]
                    if isinstance(game_config, dict):
                        game_config["savegame_location"] = replace_username_in_path(game_config.get("savegame_location", ""))
                        game_config["backup_location"] = replace_username_in_path(game_config.get("backup_location", ""))
                
                if "last_used" in config and isinstance(config["last_used"], dict):
                    last_used = config["last_used"]
                    last_used["savegame_location"] = replace_username_in_path(last_used.get("savegame_location", ""))
                    last_used["backup_location"] = replace_username_in_path(last_used.get("backup_location", ""))
                
                logger.info(f"Configuration loaded successfully from: {CONFIG_PATH}")
                return config
            else:
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
                with open(CONFIG_PATH, "w", encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
                logger.info(f"Created new config file at: {CONFIG_PATH}")
                return default_config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise ConfigError(f"Invalid configuration file format: {e}")
        except PermissionError as e:
            logger.error(f"Permission denied accessing config file: {e}")
            raise ConfigError(f"Cannot access configuration file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            raise ConfigError(f"Failed to load configuration: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            if not os.path.exists(RESOURCE_DIR):
                os.makedirs(RESOURCE_DIR)
                logger.info(f"Created Resource directory at: {RESOURCE_DIR}")
                
            with open(CONFIG_PATH, "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Config saved successfully to: {CONFIG_PATH}")
        except PermissionError as e:
            logger.error(f"Permission denied saving config: {e}")
            raise ConfigError(f"Cannot save configuration file: {e}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise ConfigError(f"Failed to save configuration: {str(e)}")
    
    def save_config_migrated(self, config):
        try:
            with open(CONFIG_PATH, "w", encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            print(f"Config migrated and saved to: {CONFIG_PATH}")
        except Exception as e:
            print(f"Error saving migrated config: {e}")
    
    def generate_game_id(self):
        return str(uuid.uuid4())
    
    def get_game_by_id(self, game_id):
        return self.config["games"].get(game_id)
    
    def get_game_id_by_title(self, game_title):
        for gid, game in self.config["games"].items():
            if game.get("game_title") == game_title:
                return gid
        return None
    
    def get_recent_games(self, max_count=10):
        """Get games ordered by last backup time"""
        if not self.config["games"]:
            return []
        
        games_with_time = []
        for gid, game in self.config["games"].items():
            last_backup_time = self.config.get("backup_history", {}).get(gid, "1970-01-01 00:00:00")
            games_with_time.append((gid, game.get("game_title", ""), last_backup_time))
        
        games_with_time.sort(key=lambda x: x[2], reverse=True)
        
        return [(gid, game_title) for gid, game_title, _ in games_with_time[:max_count]]
    
    def add_game(self, game_title, savegame_location, backup_location, game_id=None):
        """Add or update game configuration by id. If game_id is None, create new. Prevent duplicate game titles."""
        # Check if there is already a game with the same title
        if game_id is None:
            existing_id = self.get_game_id_by_title(game_title)
            if existing_id is not None:
                game_id = existing_id
            else:
                game_id = self.generate_game_id()
        self.config["games"][game_id] = {
            "id": game_id,
            "game_title": game_title,
            "savegame_location": savegame_location,
            "backup_location": backup_location
        }
        return game_id
    
    def update_last_used(self, game_title, savegame_location, backup_location):
        """Update last used configuration without removing other fields such as author"""
        if "last_used" not in self.config or not isinstance(self.config["last_used"], dict):
            self.config["last_used"] = {}
        self.config["last_used"]["game_title"] = game_title
        self.config["last_used"]["savegame_location"] = savegame_location
        self.config["last_used"]["backup_location"] = backup_location
    
    def update_backup_history(self, game_id, timestamp):
        """Update backup history with timestamp"""
        if "backup_history" not in self.config:
            self.config["backup_history"] = {}
        self.config["backup_history"][game_id] = timestamp
    
    def get_game_config(self, game_id):
        """Get configuration for specific game"""
        return self.config["games"].get(game_id, {})
    
    def delete_game(self, game_id):
        """Delete game from configuration"""
        if game_id in self.config["games"]:
            del self.config["games"][game_id]
        if "backup_history" in self.config and game_id in self.config["backup_history"]:
            del self.config["backup_history"][game_id]
    
    def rename_game(self, game_id, new_title):
        """Rename game title for existing game"""
        if game_id in self.config["games"]:
            # Check if new title already exists for different game
            existing_id = self.get_game_id_by_title(new_title)
            if existing_id and existing_id != game_id:
                raise ValueError(f"Game title '{new_title}' already exists")
            
            self.config["games"][game_id]["game_title"] = new_title
            return True
        return False
    
    def get_preferences(self):
        """Get user preferences"""
        return self.config.get("preferences", {
            "path_display": "Auto",
            "timestamp_option": "Disable",
            "save_output_directory": False
        })
    
    def save_preferences(self, preferences):
        """Save user preferences"""
        if "preferences" not in self.config:
            self.config["preferences"] = {}
        self.config["preferences"].update(preferences) 