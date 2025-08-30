import os
import shutil
from datetime import datetime
from typing import Optional, Callable
from utils.path_utils import mask_game_path_in_savegame_location
from utils.logger import logger
from utils.exceptions import BackupError
from utils.constants import BACKUP_TIMESTAMP_FORMAT, DISPLAY_TIMESTAMP_FORMAT

class BackupManager:
    def __init__(self, config_manager, progress_callback: Optional[Callable[[float], None]] = None, 
                 log_callback: Optional[Callable[[str], None]] = None):
        self.config_manager = config_manager
        self.progress_callback = progress_callback
        self.log_callback = log_callback
    
    def log(self, message):
        """Log message using callback if available"""
        if self.log_callback:
            self.log_callback(message)
    
    def update_progress(self, progress):
        """Update progress using callback if available"""
        if self.progress_callback:
            self.progress_callback(progress)
    
    def create_backup(self, game_title, savegame_location, backup_location, 
                     timestamp_option="Disable", path_display_option="Auto", 
                     author="Smothy", credit_note=""):
        """Create backup for the specified game"""
        try:
            if not os.path.exists(savegame_location):
                raise FileNotFoundError(f"Source savegame folder not found: {savegame_location}")

            # Check if we should use default backup directory
            preferences = self.config_manager.get_preferences()
            if preferences.get("save_output_directory", False):
                default_backup_dir = self.config_manager.config.get("default_backup_directory", "")
                if default_backup_dir and os.path.exists(default_backup_dir):
                    backup_location = default_backup_dir
                    self.log(f"Using default backup directory: {backup_location}")

            if not os.path.exists(backup_location):
                os.makedirs(backup_location)
                self.log(f"Created backup directory: {backup_location}")

            game_folder = os.path.join(backup_location, game_title)
            
            if not os.path.exists(game_folder):
                os.makedirs(game_folder)
                self.log(f"Created game folder: {game_folder}")

            backup_base_folder = game_folder
            if timestamp_option == "Enable":
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_base_folder = os.path.join(game_folder, timestamp)
                os.makedirs(backup_base_folder)
                self.log(f"Created timestamped folder: {backup_base_folder}")
            
            source_folder_name = os.path.basename(savegame_location.rstrip("/\\"))
            destination_folder = os.path.join(backup_base_folder, source_folder_name)

            if os.path.exists(destination_folder):
                shutil.rmtree(destination_folder)
                self.log(f"Removed existing backup at: {destination_folder}")
            
            # Copy with progress
            self.copy_with_progress(savegame_location, destination_folder)
            
            self.log(f"Backup successful! Savegame copied to: {destination_folder}")

            # Create credit file
            self.create_credit_file(backup_base_folder, game_title, savegame_location, 
                                  path_display_option, author, credit_note)

        except Exception as e:
            raise Exception(f"Backup failed: {str(e)}")
    
    def copy_with_progress(self, src, dst):
        """Copy directory with progress bar"""
        try:
            # Count total files for progress calculation
            total_files = sum([len(files) for _, _, files in os.walk(src)])
            copied_files = 0
            
            def copy_progress(src, dst):
                nonlocal copied_files
                if os.path.isdir(src):
                    if not os.path.exists(dst):
                        os.makedirs(dst)
                    for item in os.listdir(src):
                        s = os.path.join(src, item)
                        d = os.path.join(dst, item)
                        copy_progress(s, d)
                else:
                    shutil.copy2(src, dst)
                    copied_files += 1
                    progress = min(100, (copied_files / total_files) * 100)
                    self.update_progress(progress)
            
            copy_progress(src, dst)
            
        except Exception as e:
            raise Exception(f"Copy operation failed: {str(e)}")
    
    def create_credit_file(self, backup_base_folder, game_name, source_folder, 
                          path_display_option, author, credit_note):
        """Create credit file with backup information"""
        credit_file_path = os.path.join(backup_base_folder, "Readme.txt")
        backup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        separator = "=" * 60
        additional_info = (
            "**********************************************************\n"
            "* This savegame was backed up using \"Sweet Progress\"   *\n"
            "* Feel free for contribute and try this program,         *\n"
            "* Check on : https://github.com/Smothyze/sweet-progress  *\n"
            "**********************************************************\n"
        )
        try:
            with open(credit_file_path, "w", encoding='utf-8') as credit_file:
                credit_file.write(f"Backup savegame for {game_name}.\n")
                credit_file.write(f"{separator}\n")
                credit_file.write(f"\n")
                credit_file.write(f"Author:\n")
                if author:
                    credit_file.write(f"{author}\n")
                else:
                    # If author is empty, use system username as fallback for display
                    import getpass
                    try:
                        system_author = getpass.getuser()
                        credit_file.write(f"{system_author}\n")
                    except Exception:
                        credit_file.write(f"User\n")
                credit_file.write(f"\n")
                if credit_note:
                    credit_file.write(f"Note:\n{credit_note}\n\n")
                credit_file.write(f"Update on:\n")
                credit_file.write(f"{backup_time}\n")
                credit_file.write(f"\n")
                credit_file.write(f"Savegame Location:\n")
                masked_path = mask_game_path_in_savegame_location(source_folder, path_display_option)
                credit_file.write(f"{masked_path}\n\n")
                credit_file.write(additional_info)
            self.log(f"Credit file added: {credit_file_path}")
        except Exception as e:
            self.log(f"Warning: Could not create credit file: {str(e)}") 