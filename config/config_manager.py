import json
import os
from utils.path_utils import replace_username_in_path
from utils.resource_utils import CONFIG_PATH, RESOURCE_DIR
import uuid

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
                    
                # MIGRASI: Jika format lama (berbasis game_title), migrasikan ke format baru (berbasis id)
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
                # Pastikan semua entry punya id dan game_title
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
        """Add or update game configuration by id. If game_id is None, create new."""
        if game_id is None:
            game_id = self.generate_game_id()
        self.config["games"][game_id] = {
            "id": game_id,
            "game_title": game_title,
            "savegame_location": savegame_location,
            "backup_location": backup_location
        }
        return game_id
    
    def update_last_used(self, game_title, savegame_location, backup_location):
        """Update last used configuration"""
        self.config["last_used"] = {
            "game_title": game_title,
            "savegame_location": savegame_location,
            "backup_location": backup_location
        }
    
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