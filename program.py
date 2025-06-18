import os
import shutil
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import io
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # Get the directory where the executable is located
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (exe)
            base_path = os.path.dirname(sys.executable)
        else:
            # If the application is run from a Python interpreter
            base_path = os.path.abspath(".")

        # Create the full path
        full_path = os.path.join(base_path, relative_path)
        
        # Create the directory if it doesn't exist
        if os.path.dirname(full_path) and not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
            
        return full_path
    except Exception as e:
        print(f"Error in resource_path: {e}")
        return os.path.abspath(relative_path)

# Path ke folder Resource
RESOURCE_DIR = resource_path("Resource")
ICON_PATH = os.path.join(RESOURCE_DIR, "icon.ico")
CONFIG_PATH = os.path.join(RESOURCE_DIR, "savegame_config.json")

# Validasi file icon
if not os.path.exists(ICON_PATH):
    root = tk.Tk()
    root.withdraw()  # Hide main window
    messagebox.showerror("Error", f"The icon file not detected on: {ICON_PATH}\nAplikasi akan ditutup.")
    sys.exit(1)

class SaveGameBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sweet Progress")
        self.root.geometry("600x400")
        try:
            self.root.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        # Load configuration
        self.config_file = CONFIG_PATH
        self.config = self.load_config()
        
        # Create GUI
        self.create_widgets()
        
    def load_config(self):
        """Load configuration from file or return default if not exists"""
        default_config = {
            "games": {},
            "last_used": {}
        }
        
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default config file if it doesn't exist
                with open(CONFIG_PATH, "w", encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
                print(f"Created new config file at: {CONFIG_PATH}")
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Ensure Resource directory exists
            if not os.path.exists(RESOURCE_DIR):
                os.makedirs(RESOURCE_DIR)
                print(f"Created Resource directory at: {RESOURCE_DIR}")
                
            with open(CONFIG_PATH, "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            print(f"Config saved successfully to: {CONFIG_PATH}")
        except Exception as e:
            print(f"Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game Title
        ttk.Label(main_frame, text="Game Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.game_title = tk.StringVar()
        self.game_title_combo = ttk.Combobox(main_frame, textvariable=self.game_title)
        self.game_title_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.game_title_combo['values'] = list(self.config["games"].keys())
        self.game_title_combo.bind("<<ComboboxSelected>>", self.on_game_selected)
        self.game_title_combo.bind("<Return>", self.on_game_manual_entry)
        
        # Savegame Location
        ttk.Label(main_frame, text="Savegame Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.savegame_location = tk.StringVar()
        savegame_entry = ttk.Entry(main_frame, textvariable=self.savegame_location, width=50)
        savegame_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_savegame).grid(row=1, column=2, padx=5)
        
        # Backup Location
        ttk.Label(main_frame, text="Backup Location:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.backup_location = tk.StringVar()
        backup_entry = ttk.Entry(main_frame, textvariable=self.backup_location, width=50)
        backup_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_backup).grid(row=2, column=2, padx=5)
        
        # Backup Button
        ttk.Button(main_frame, text="Create Backup", command=self.create_backup).grid(row=3, column=1, pady=20)
        
        # Log Area
        ttk.Label(main_frame, text="Log:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.log_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=5, column=0, columnspan=3, sticky=tk.NSEW, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Load last used values if any
        if "last_used" in self.config:
            last = self.config["last_used"]
            self.game_title.set(last.get("game_title", ""))
            self.savegame_location.set(last.get("savegame_location", ""))
            self.backup_location.set(last.get("backup_location", ""))
    
    def on_game_selected(self, event):
        """When a game is selected from dropdown, auto-fill paths"""
        game = self.game_title.get()
        if game in self.config["games"]:
            paths = self.config["games"][game]
            self.savegame_location.set(paths.get("savegame_location", ""))
            self.backup_location.set(paths.get("backup_location", ""))
    
    def on_game_manual_entry(self, event):
        """When user manually enters a game name, check if it exists in config"""
        game = self.game_title.get()
        if game in self.config["games"]:
            paths = self.config["games"][game]
            self.savegame_location.set(paths.get("savegame_location", ""))
            self.backup_location.set(paths.get("backup_location", ""))
    
    def browse_savegame(self):
        """Browse for savegame location"""
        folder = filedialog.askdirectory()
        if folder:
            self.savegame_location.set(folder)
    
    def browse_backup(self):
        """Browse for backup location"""
        folder = filedialog.askdirectory()
        if folder:
            self.backup_location.set(folder)
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def create_backup(self):
        """Create the backup"""
        game_title = self.game_title.get().strip()
        savegame_location = self.savegame_location.get().strip()
        backup_location = self.backup_location.get().strip()
        
        if not game_title:
            messagebox.showerror("Error", "Please enter a game title")
            return
            
        if not savegame_location:
            messagebox.showerror("Error", "Please select savegame location")
            return
            
        if not backup_location:
            messagebox.showerror("Error", "Please select backup location")
            return
            
        try:
            # Save current settings
            self.config["games"][game_title] = {
                "savegame_location": savegame_location,
                "backup_location": backup_location
            }
            
            self.config["last_used"] = {
                "game_title": game_title,
                "savegame_location": savegame_location,
                "backup_location": backup_location
            }
            
            self.save_config()
            
            # Perform backup
            self.log(f"Starting backup for {game_title}...")
            self.backup_savegame_with_credit(savegame_location, backup_location, game_title)
            messagebox.showinfo("Success", "Backup completed successfully!")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def backup_savegame_with_credit(self, source_folder, backup_directory, game_name):
        """
        Backup savegame with credit file containing backup time and date.

        Parameters:
        - source_folder: Location of the savegame folder to backup.
        - backup_directory: Destination folder for the backup.
        - game_name: Game name to create a folder in backup_directory.
        """
        try:
            # Validate source_folder exists
            if not os.path.exists(source_folder):
                raise FileNotFoundError(f"Source savegame folder not found: {source_folder}")

            # Create main backup folder if not exists
            if not os.path.exists(backup_directory):
                os.makedirs(backup_directory)
                self.log(f"Created backup directory: {backup_directory}")

            # Path for game folder inside backup_directory
            game_folder = os.path.join(backup_directory, game_name)
            
            # Create game folder if not exists
            if not os.path.exists(game_folder):
                os.makedirs(game_folder)
                self.log(f"Created game folder: {game_folder}")
            
            # Source folder name from original path
            source_folder_name = os.path.basename(source_folder.rstrip("/\\"))

            # Destination path for savegame copy
            destination_folder = os.path.join(game_folder, source_folder_name)

            # Copy source folder to destination
            if os.path.exists(destination_folder):
                shutil.rmtree(destination_folder)
                self.log(f"Removed existing backup at: {destination_folder}")
                
            shutil.copytree(source_folder, destination_folder)
            self.log(f"Backup successful! Savegame copied to: {destination_folder}")

            # Add credit file with backup time and date
            credit_file_path = os.path.join(game_folder, "Readme.txt")
            backup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(credit_file_path, "w") as credit_file:
                credit_file.write(f"Backup savegame for {game_name}.\n")
                credit_file.write(f"\n")
                credit_file.write(f"Credit By:\n")
                credit_file.write(f"Smothy\n")
                credit_file.write(f"\n")
                credit_file.write(f"Update on:\n")
                credit_file.write(f"{backup_time}\n")
                credit_file.write(f"\n")
                credit_file.write(f"Savegame Location:\n")
                credit_file.write(f"{source_folder}\n")
            self.log(f"Credit file added: {credit_file_path}")

        except Exception as e:
            raise e

def main():
    root = tk.Tk()
    app = SaveGameBackupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
