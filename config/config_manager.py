import json
import os
from utils.path_utils import replace_username_in_path
from utils.resource_utils import CONFIG_PATH, RESOURCE_DIR

class ConfigManager:
    def __init__(self):
        self.config_file = CONFIG_PATH
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "games": {},
            "last_used": {},
            "backup_history": {},  # Add backup history to track timestamps
            "preferences": {
                "path_display": "Auto",
                "timestamp_option": "Disable"
            }
        }
        
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Validate config structure
                if not isinstance(config, dict):
                    raise ValueError("Invalid config format")
                
                if "games" not in config:
                    config["games"] = {}
                if "last_used" not in config:
                    config["last_used"] = {}
                if "backup_history" not in config:
                    config["backup_history"] = {}
                if "preferences" not in config:
                    config["preferences"] = {
                        "path_display": "Auto",
                        "timestamp_option": "Disable"
                    }
                    
                for game in config["games"]:
                    game_config = config["games"][game]
                    if isinstance(game_config, dict):
                        game_config["savegame_location"] = replace_username_in_path(game_config.get("savegame_location", ""))
                        game_config["backup_location"] = replace_username_in_path(game_config.get("backup_location", ""))
                
                if "last_used" in config and isinstance(config["last_used"], dict):
                    last_used = config["last_used"]
                    last_used["savegame_location"] = replace_username_in_path(last_used.get("savegame_location", ""))
                    last_used["backup_location"] = replace_username_in_path(last_used.get("backup_location", ""))
                
                return config
            else:
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
                with open(CONFIG_PATH, "w", encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
                print(f"Created new config file at: {CONFIG_PATH}")
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            if not os.path.exists(RESOURCE_DIR):
                os.makedirs(RESOURCE_DIR)
                print(f"Created Resource directory at: {RESOURCE_DIR}")
                
            with open(CONFIG_PATH, "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            print(f"Config saved successfully to: {CONFIG_PATH}")
        except Exception as e:
            print(f"Error saving config: {e}")
            raise Exception(f"Failed to save configuration: {str(e)}")
    
    def get_recent_games(self, max_count=10):
        """Get games ordered by last backup time"""
        if not self.config["games"]:
            return []
        
        # Get all games with their last backup time
        games_with_time = []
        for game_name in self.config["games"].keys():
            last_backup_time = self.config.get("backup_history", {}).get(game_name, "1970-01-01 00:00:00")
            games_with_time.append((game_name, last_backup_time))
        
        # Sort by backup time (newest first)
        games_with_time.sort(key=lambda x: x[1], reverse=True)
        
        # Return only game names, limited to max_count
        return [game[0] for game in games_with_time[:max_count]]
    
    def add_game(self, game_title, savegame_location, backup_location):
        """Add or update game configuration"""
        self.config["games"][game_title] = {
            "savegame_location": savegame_location,
            "backup_location": backup_location
        }
    
    def update_last_used(self, game_title, savegame_location, backup_location):
        """Update last used configuration"""
        self.config["last_used"] = {
            "game_title": game_title,
            "savegame_location": savegame_location,
            "backup_location": backup_location
        }
    
    def update_backup_history(self, game_title, timestamp):
        """Update backup history with timestamp"""
        if "backup_history" not in self.config:
            self.config["backup_history"] = {}
        self.config["backup_history"][game_title] = timestamp
    
    def get_game_config(self, game_title):
        """Get configuration for specific game"""
        return self.config["games"].get(game_title, {})
    
    def delete_game(self, game_title):
        """Delete game from configuration"""
        if game_title in self.config["games"]:
            del self.config["games"][game_title]
        if "backup_history" in self.config and game_title in self.config["backup_history"]:
            del self.config["backup_history"][game_title]
    
    def get_preferences(self):
        """Get user preferences"""
        return self.config.get("preferences", {
            "path_display": "Auto",
            "timestamp_option": "Disable"
        })
    
    def save_preferences(self, preferences):
        """Save user preferences"""
        if "preferences" not in self.config:
            self.config["preferences"] = {}
        self.config["preferences"].update(preferences) 