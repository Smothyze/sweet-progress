import os
import shutil
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import getpass
import re
from pathlib import Path

def get_current_username():
    return getpass.getuser()

def normalize_path(path):
    """Normalize path to use system-specific separator"""
    if not path:
        return path
    return str(Path(path))

def replace_username_in_path(path):
    if not path:
        return path
    
    current_username = get_current_username()
    normalized_path = normalize_path(path)
    
    # Handle both Windows and Unix paths
    if os.name == 'nt':  # Windows
        parts = normalized_path.split('\\')
        if len(parts) > 2 and parts[1].lower() == 'users':
            parts[2] = current_username
            return '\\'.join(parts)
    else:  # Unix/Linux
        parts = normalized_path.split('/')
        if len(parts) > 2 and parts[1] == 'home':
            parts[2] = current_username
            return '/'.join(parts)
    return path

def mask_username_in_path(path):
    if not path:
        return path
    try:
        user_profile = os.environ.get('USERPROFILE') or os.environ.get('HOME')
        if user_profile and path.lower().startswith(user_profile.lower()):
            users_folder = os.path.dirname(user_profile)
            rest_of_path = path[len(user_profile):]
            return os.path.join(users_folder, '(pc-name)') + rest_of_path
    except Exception:
        pass

    normalized_path = normalize_path(path)
    if os.name == 'nt':  # Windows
        parts = normalized_path.split('\\')
        if len(parts) > 2 and parts[1].lower() == 'users':
            parts[2] = '(pc-name)'
            return '\\'.join(parts)
    else:  # Unix/Linux
        parts = normalized_path.split('/')
        if len(parts) > 2 and parts[1] == 'home':
            parts[2] = '(pc-name)'
            return '/'.join(parts)
    return path

def mask_steamid_in_path(path):
    if not path:
        return path
    norm_path = normalize_path(path)
    parts = norm_path.split(os.sep)
    for i in range(len(parts) - 2):
        if parts[i].lower() == 'steam' and parts[i+1].lower() == 'userdata':
            if parts[i+2].isdigit():
                parts[i+2] = '(steam-id)'
                return os.sep.join(parts)
    return path

def resource_path(relative_path):
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")

        full_path = os.path.join(base_path, relative_path)
        
        if os.path.dirname(full_path) and not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
            
        return full_path
    except Exception as e:
        print(f"Error in resource_path: {e}")
        return os.path.abspath(relative_path)

def validate_path(path):
    """Validate if path is accessible and writable"""
    if not path:
        return False, "Path is empty"
    
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return False, f"Path does not exist: {path}"
        
        # Check if readable
        if not os.access(path, os.R_OK):
            return False, f"Path is not readable: {path}"
            
        return True, "Path is valid"
    except Exception as e:
        return False, f"Invalid path: {str(e)}"

def validate_game_title(title):
    """Validate game title for invalid characters"""
    if not title or not title.strip():
        return False, "Game title cannot be empty"
    
    # Check for invalid characters in filename
    invalid_chars = '<>:"/\\|?*'
    if any(char in title for char in invalid_chars):
        return False, f"Game title contains invalid characters: {invalid_chars}"
    
    return True, "Game title is valid"

RESOURCE_DIR = resource_path("Resource")
ICON_PATH = os.path.join(RESOURCE_DIR, "icon.ico")
CONFIG_PATH = os.path.join(RESOURCE_DIR, "savegame_config.json")

class SaveGameBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sweet Progress")
        self.root.geometry("600x400")
        self.root.minsize(600, 400)
        
        # Check icon file existence safely
        if os.path.exists(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Error loading icon: {e}")
        else:
            print(f"Warning: Icon file not found at {ICON_PATH}")
        
        self.config_file = CONFIG_PATH
        self.config = self.load_config()
        self._credit_note = ""
        
        # Initialize log line counter
        self.log_line_count = 0
        self.max_log_lines = 1000
        
        self.create_widgets()
        
    def load_config(self):
        default_config = {
            "games": {},
            "last_used": {},
            "backup_history": {}  # Add backup history to track timestamps
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
        try:
            if not os.path.exists(RESOURCE_DIR):
                os.makedirs(RESOURCE_DIR)
                print(f"Created Resource directory at: {RESOURCE_DIR}")
                
            with open(CONFIG_PATH, "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            print(f"Config saved successfully to: {CONFIG_PATH}")
            self.validate_list_button()  # Update List button state after saving config
        except Exception as e:
            print(f"Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Game Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.game_title = tk.StringVar()
        self.game_title_combo = ttk.Combobox(main_frame, textvariable=self.game_title)
        self.game_title_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Get recent games ordered by last backup time (limit to 5 items)
        recent_games = self.get_recent_games(5)
        self.game_title_combo['values'] = recent_games
        
        self.game_title_combo.bind("<<ComboboxSelected>>", self.on_game_selected)
        self.game_title_combo.bind("<Return>", self.on_game_manual_entry)
        self.list_btn = ttk.Button(main_frame, text="List", command=self.show_game_list_window)
        self.list_btn.grid(row=0, column=2, padx=5)
        
        ttk.Label(main_frame, text="Savegame Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.savegame_location = tk.StringVar()
        savegame_entry = ttk.Entry(main_frame, textvariable=self.savegame_location, width=50)
        savegame_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        savegame_entry.bind('<FocusOut>', lambda e: self.log(f"Savegame location updated: {self.savegame_location.get()}"))
        savegame_entry.bind('<Return>', lambda e: self.log(f"Savegame location updated: {self.savegame_location.get()}"))
        ttk.Button(main_frame, text="Browse...", command=self.browse_savegame).grid(row=1, column=2, padx=5)
        
        ttk.Label(main_frame, text="Backup Location:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.backup_location = tk.StringVar()
        backup_entry = ttk.Entry(main_frame, textvariable=self.backup_location, width=50)
        backup_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        backup_entry.bind('<FocusOut>', lambda e: self.log(f"Backup location updated: {self.backup_location.get()}"))
        backup_entry.bind('<Return>', lambda e: self.log(f"Backup location updated: {self.backup_location.get()}"))
        ttk.Button(main_frame, text="Browse...", command=self.browse_backup).grid(row=2, column=2, padx=5)
        
        ttk.Label(main_frame, text="Timestamp:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.timestamp_option = tk.StringVar(value="Disable")
        timestamp_frame = ttk.Frame(main_frame)
        timestamp_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(timestamp_frame, text="Disable", variable=self.timestamp_option, value="Disable").pack(side=tk.LEFT)
        ttk.Radiobutton(timestamp_frame, text="Enable", variable=self.timestamp_option, value="Enable").pack(side=tk.LEFT, padx=10)
        
        ttk.Button(main_frame, text="Credit Setting", command=self.open_credit_setting).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.progress_bar.grid_remove()  # Hidden by default
        
        ttk.Label(main_frame, text="Log:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.log_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=7, column=0, columnspan=3, sticky=tk.NSEW, pady=5)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        if "last_used" in self.config:
            last = self.config["last_used"]
            self.game_title.set(last.get("game_title", ""))
            self.savegame_location.set(last.get("savegame_location", ""))
            self.backup_location.set(last.get("backup_location", ""))
        
        # Tombol Create Backup
        self.create_backup_btn = ttk.Button(main_frame, text="Create Backup", command=self.create_backup)
        self.create_backup_btn.grid(row=8, column=1, pady=20)
        self.validate_inputs()  # Set initial state
        self.validate_list_button()  # Set initial state for List button
        # Pasang trace pada input
        self.game_title.trace_add('write', lambda *args: self.validate_inputs())
        self.savegame_location.trace_add('write', lambda *args: self.validate_inputs())
        self.backup_location.trace_add('write', lambda *args: self.validate_inputs())
    
    def on_game_selected(self, event):
        game = self.game_title.get()
        if game in self.config["games"]:
            paths = self.config["games"][game]
            self.savegame_location.set(paths.get("savegame_location", ""))
            self.backup_location.set(paths.get("backup_location", ""))
            self.log(f"Game selected: {game}")
    
    def on_game_manual_entry(self, event):
        game = self.game_title.get()
        if game in self.config["games"]:
            paths = self.config["games"][game]
            self.savegame_location.set(paths.get("savegame_location", ""))
            self.backup_location.set(paths.get("backup_location", ""))
    
    def browse_savegame(self):
        folder = filedialog.askdirectory()
        if folder:
            # Validate the selected folder
            is_valid, message = validate_path(folder)
            if is_valid:
                self.savegame_location.set(folder)
                self.log(f"Savegame location updated: {folder}")
            else:
                messagebox.showerror("Invalid Path", message)
    
    def browse_backup(self):
        folder = filedialog.askdirectory()
        if folder:
            # Check if folder is writable
            try:
                test_file = os.path.join(folder, "test_write.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                self.backup_location.set(folder)
                self.log(f"Backup location updated: {folder}")
            except Exception as e:
                messagebox.showerror("Error", f"Selected folder is not writable: {str(e)}")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Limit log lines to prevent memory issues
        self.log_line_count += 1
        if self.log_line_count > self.max_log_lines:
            # Remove first 100 lines when limit is exceeded
            self.log_text.delete("1.0", "101.0")
            self.log_line_count -= 100
        
        self.root.update()
    
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

    def create_backup(self):
        game_title = self.game_title.get().strip()
        savegame_location = self.savegame_location.get().strip()
        backup_location = self.backup_location.get().strip()
        
        # Validate inputs
        is_valid_title, title_message = validate_game_title(game_title)
        if not is_valid_title:
            messagebox.showerror("Error", title_message)
            return
            
        is_valid_source, source_message = validate_path(savegame_location)
        if not is_valid_source:
            messagebox.showerror("Error", source_message)
            return
            
        is_valid_backup, backup_message = validate_path(backup_location)
        if not is_valid_backup:
            messagebox.showerror("Error", backup_message)
            return
        
        # Check if backup location is writable
        try:
            test_file = os.path.join(backup_location, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            messagebox.showerror("Error", f"Backup location is not writable: {str(e)}")
            return
            
        try:
            self.config["games"][game_title] = {
                "savegame_location": savegame_location,
                "backup_location": backup_location
            }
            
            self.config["last_used"] = {
                "game_title": game_title,
                "savegame_location": savegame_location,
                "backup_location": backup_location
            }
            
            # Update backup history with current timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "backup_history" not in self.config:
                self.config["backup_history"] = {}
            self.config["backup_history"][game_title] = current_time
            
            self.save_config()
            
            self.log(f"Starting backup for {game_title}...")
            self.backup_savegame_with_credit(savegame_location, backup_location, game_title)
            
            # Update dropdown values after successful backup
            self.update_dropdown_values()
            
            messagebox.showinfo("Success", "Backup completed successfully!")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def backup_savegame_with_credit(self, source_folder, backup_directory, game_name):
        try:
            if not os.path.exists(source_folder):
                raise FileNotFoundError(f"Source savegame folder not found: {source_folder}")

            if not os.path.exists(backup_directory):
                os.makedirs(backup_directory)
                self.log(f"Created backup directory: {backup_directory}")

            game_folder = os.path.join(backup_directory, game_name)
            
            if not os.path.exists(game_folder):
                os.makedirs(game_folder)
                self.log(f"Created game folder: {game_folder}")

            backup_base_folder = game_folder
            if self.timestamp_option.get() == "Enable":
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_base_folder = os.path.join(game_folder, timestamp)
                os.makedirs(backup_base_folder)
                self.log(f"Created timestamped folder: {backup_base_folder}")
            
            source_folder_name = os.path.basename(source_folder.rstrip("/\\"))

            destination_folder = os.path.join(backup_base_folder, source_folder_name)

            if os.path.exists(destination_folder):
                shutil.rmtree(destination_folder)
                self.log(f"Removed existing backup at: {destination_folder}")
            
            # Show progress bar
            self.progress_bar.grid()
            self.progress_var.set(0)
            self.root.update()
            
            # Copy with progress
            self.copy_with_progress(source_folder, destination_folder)
            
            self.log(f"Backup successful! Savegame copied to: {destination_folder}")

            credit_file_path = os.path.join(backup_base_folder, "Readme.txt")
            backup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            author = self.config.get("last_used", {}).get("author", "").strip() or "Smothy"
            note = getattr(self, '_credit_note', '').strip()
            
            try:
                with open(credit_file_path, "w", encoding='utf-8') as credit_file:
                    credit_file.write(f"Backup savegame for {game_name}.\n")
                    credit_file.write(f"\n")
                    credit_file.write(f"Author:\n")
                    credit_file.write(f"{author}\n")
                    if note:
                        credit_file.write(f"\nNote:\n{note}\n")
                    credit_file.write(f"\n")
                    credit_file.write(f"Update on:\n")
                    credit_file.write(f"{backup_time}\n")
                    credit_file.write(f"\n")
                    credit_file.write(f"Savegame Location:\n")
                    masked_path = mask_steamid_in_path(source_folder)
                    masked_path = mask_username_in_path(masked_path)
                    credit_file.write(f"{masked_path}\n")
                self.log(f"Credit file added: {credit_file_path}")
            except Exception as e:
                self.log(f"Warning: Could not create credit file: {str(e)}")

        except Exception as e:
            raise Exception(f"Backup failed: {str(e)}")
        finally:
            # Hide progress bar
            self.progress_bar.grid_remove()
            self.progress_var.set(0)
    
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
                    self.progress_var.set(progress)
                    self.root.update()
            
            copy_progress(src, dst)
            
        except Exception as e:
            raise Exception(f"Copy operation failed: {str(e)}")

    def show_game_list_window(self):
        win = tk.Toplevel(self.root)
        win.title("Game Title List")
        win.geometry("500x450")
        win.transient(self.root)
        win.grab_set()
        try:
            if os.path.exists(ICON_PATH):
                win.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon for list window: {e}")
        win.resizable(False, False)

        # Create sort options frame
        sort_frame = ttk.Frame(win)
        sort_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=(0, 10))
        
        sort_var = tk.StringVar(value="Last Used")
        sort_combo = ttk.Combobox(sort_frame, textvariable=sort_var, values=["Last Used", "Alphabetical"], 
                                 state="readonly", width=15)
        sort_combo.pack(side=tk.LEFT)

        # Create frame for treeview and scrollbar
        table_frame = ttk.Frame(win)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview with columns
        columns = ("Game Title", "Last Used")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings
        tree.heading("Game Title", text="Game Title")
        tree.heading("Last Used", text="Last Used")
        
        # Configure column widths
        tree.column("Game Title", width=250, anchor="w")
        tree.column("Last Used", width=200, anchor="w")
        
        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars to avoid overlap
        tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        # Configure grid weights so treeview expands
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        def refresh_table():
            """Refresh the table based on current sort option"""
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            # Get games with their last backup time
            games_with_time = []
            for game_name in self.config["games"].keys():
                last_backup_time = self.config.get("backup_history", {}).get(game_name, "Never")
                games_with_time.append((game_name, last_backup_time))
            
            # Sort based on selected option
            if sort_var.get() == "Alphabetical":
                # Sort alphabetically by game name
                games_with_time.sort(key=lambda x: x[0].lower())
            else:
                # Sort by last backup time (newest first)
                games_with_time.sort(key=lambda x: x[1] if x[1] != "Never" else "1970-01-01 00:00:00", reverse=True)
            
            # Insert games into treeview
            for game_name, last_backup in games_with_time:
                tree.insert("", tk.END, values=(game_name, last_backup))

        # Initial load
        refresh_table()
        
        # Bind sort change event
        sort_combo.bind("<<ComboboxSelected>>", lambda e: refresh_table())

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        def select_game():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                game_name = item['values'][0]  # First column is game name
                self.game_title.set(game_name)
                self.on_game_selected(None)
                self.log(f"Game selected from list: {game_name}")
                # Use after() to ensure window destruction happens after current operation
                win.after(100, win.destroy)

        def delete_game():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                game_name = item['values'][0]  # First column is game name
                if messagebox.askyesno("Confirmation", f"Delete game title '{game_name}' from the list?"):
                    try:
                        del self.config["games"][game_name]
                        if "backup_history" in self.config and game_name in self.config["backup_history"]:
                            del self.config["backup_history"][game_name]
                        self.save_config()
                        tree.delete(selection[0])
                        self.update_dropdown_values()
                        if self.game_title.get() == game_name:
                            self.game_title.set("")
                            self.savegame_location.set("")
                            self.backup_location.set("")
                        self.log(f"Game '{game_name}' has been deleted from the list.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete game: {str(e)}")

        select_btn = ttk.Button(btn_frame, text="Select", command=select_game, state=tk.DISABLED)
        delete_btn = ttk.Button(btn_frame, text="Delete", command=delete_game, state=tk.DISABLED)
        select_btn.pack(side=tk.LEFT, padx=5)
        delete_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)

        def update_buttons_state(event=None):
            selection = tree.selection()
            if selection:
                select_btn.state(["!disabled"])
                delete_btn.state(["!disabled"])
            else:
                select_btn.state(["disabled"])
                delete_btn.state(["disabled"])

        tree.bind("<<TreeviewSelect>>", update_buttons_state)
        # Pastikan tombol dalam keadaan benar saat awal
        update_buttons_state()

    def open_credit_setting(self):
        credit_win = tk.Toplevel(self.root)
        credit_win.title("Credit Setting")
        credit_win.geometry("400x220")
        credit_win.transient(self.root)
        credit_win.grab_set()
        try:
            if os.path.exists(ICON_PATH):
                credit_win.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon for credit window: {e}")
        credit_win.resizable(False, False)

        # Title
        title_label = ttk.Label(credit_win, text="Credit Information", font=("Segoe UI", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(16, 4), padx=16, sticky="w")

        # Separator
        sep = ttk.Separator(credit_win, orient="horizontal")
        sep.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 10))

        # Author
        ttk.Label(credit_win, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=(0, 8), padx=16)
        author_var = tk.StringVar(value=self.config.get("last_used", {}).get("author", ""))
        author_entry = ttk.Entry(credit_win, textvariable=author_var, width=36)
        author_entry.grid(row=2, column=1, sticky=tk.EW, pady=(0, 8), padx=(0, 16))

        # Note (opsional, tidak disimpan di config)
        ttk.Label(credit_win, text="Note (optional):").grid(row=3, column=0, sticky=tk.NW, pady=(0, 8), padx=16)
        note_text = tk.Text(credit_win, width=36, height=5, wrap=tk.WORD)
        note_text.grid(row=3, column=1, sticky=tk.EW, pady=(0, 8), padx=(0, 16))
        if hasattr(self, '_credit_note'):
            note_text.insert(tk.END, self._credit_note)

        # Frame untuk tombol
        btn_frame = ttk.Frame(credit_win)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(8, 16), padx=16, sticky=tk.E)

        save_btn = ttk.Button(btn_frame, text="Save", state=tk.DISABLED)
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(btn_frame, text="Cancel", command=credit_win.destroy).pack(side=tk.RIGHT, padx=(0, 8))

        def validate_save_btn(*args):
            author = author_var.get().strip()
            note = note_text.get("1.0", tk.END).strip()
            if author or note:
                save_btn.state(["!disabled"])
            else:
                save_btn.state(["disabled"])

        author_var.trace_add("write", validate_save_btn)
        note_text.bind("<KeyRelease>", lambda e: validate_save_btn())

        def save_credit():
            try:
                author = author_var.get().strip()
                if "last_used" not in self.config:
                    self.config["last_used"] = {}
                self.config["last_used"]["author"] = author
                self.save_config()
                self._credit_note = note_text.get("1.0", tk.END).strip()
                self.log("Credit setting saved (Author dan Note).")
                credit_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save credit settings: {str(e)}")

        save_btn.config(command=save_credit)
        # Inisialisasi status tombol
        validate_save_btn()

        # Buat kolom 1 (input) bisa melebar
        credit_win.columnconfigure(1, weight=1)

    def validate_inputs(self):
        game_title = self.game_title.get().strip()
        savegame_location = self.savegame_location.get().strip()
        backup_location = self.backup_location.get().strip()
        if game_title and savegame_location and backup_location:
            self.create_backup_btn.state(["!disabled"])
        else:
            self.create_backup_btn.state(["disabled"])

    def validate_list_button(self):
        if self.config["games"]:
            self.list_btn.state(["!disabled"])
        else:
            self.list_btn.state(["disabled"])

    def update_dropdown_values(self):
        """Update dropdown values with recent games (limit to 5 items)"""
        recent_games = self.get_recent_games(5)
        self.game_title_combo['values'] = recent_games

def main():
    try:
        root = tk.Tk()
        app = SaveGameBackupApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
