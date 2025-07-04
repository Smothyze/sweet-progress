import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import webbrowser

from config.config_manager import ConfigManager
from backup.backup_manager import BackupManager
from utils.path_utils import validate_path, validate_game_title, detect_game_directory
from utils.resource_utils import ICON_PATH
from ui.windows import GameListWindow, CreditSettingWindow, PathPreviewWindow

class SaveGameBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sweet Progress")
        self.root.geometry("600x500")
        self.root.minsize(600, 500)
        
        # Tambahkan menu bar
        self.menu_bar = tk.Menu(self.root)
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_all_inputs)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        # About menu
        about_menu = tk.Menu(self.menu_bar, tearoff=0)
        about_menu.add_command(label="Info", command=self.show_about)
        about_menu.add_separator()
        about_menu.add_command(label="GitHub", command=lambda: webbrowser.open_new("https://github.com/Smothyze/sweet-progress"))
        self.menu_bar.add_cascade(label="About", menu=about_menu)
        self.root.config(menu=self.menu_bar)
        
        # Check icon file existence safely
        if os.path.exists(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Error loading icon: {e}")
        else:
            print(f"Warning: Icon file not found at {ICON_PATH}")
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.backup_manager = BackupManager(
            self.config_manager,
            progress_callback=self.update_progress,
            log_callback=self.log
        )
        
        self._credit_note = ""
        
        # Initialize log line counter
        self.log_line_count = 0
        self.max_log_lines = 1000
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Game Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.game_title = tk.StringVar()
        self.game_title_combo = ttk.Combobox(main_frame, textvariable=self.game_title)
        self.game_title_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Get recent games ordered by last backup time (limit to 5 items)
        recent_games = self.config_manager.get_recent_games(5)
        self.game_title_combo['values'] = recent_games
        
        self.game_title_combo.bind("<<ComboboxSelected>>", self.on_game_selected)
        self.game_title_combo.bind("<Return>", self.on_game_manual_entry)
        self.list_btn = ttk.Button(main_frame, text="List", command=self.show_game_list_window)
        self.list_btn.grid(row=0, column=2, padx=5)
        
        # Savegame Location
        ttk.Label(main_frame, text="Savegame Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.savegame_location = tk.StringVar()
        savegame_entry = ttk.Entry(main_frame, textvariable=self.savegame_location, width=50)
        savegame_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        savegame_entry.bind('<FocusOut>', lambda e: self.log(f"Savegame location updated: {self.savegame_location.get()}"))
        savegame_entry.bind('<Return>', lambda e: self.log(f"Savegame location updated: {self.savegame_location.get()}"))
        ttk.Button(main_frame, text="Browse...", command=self.browse_savegame).grid(row=1, column=2, padx=5)
        
        # Game directory detection info - moved to separate row
        self.game_dir_info = tk.StringVar()
        self.game_dir_label = ttk.Label(main_frame, textvariable=self.game_dir_info, foreground="blue", font=("Segoe UI", 8))
        self.game_dir_label.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=(0, 5))
        
        # Game directory action info - second line
        self.game_dir_action = tk.StringVar()
        self.game_dir_action_label = ttk.Label(main_frame, textvariable=self.game_dir_action, foreground="green", font=("Segoe UI", 8))
        self.game_dir_action_label.grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=5, pady=(0, 5))
        
        # Path Display & Preview in one row - positioned below Savegame Location
        ttk.Label(main_frame, text="Path Display:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.path_display_option = tk.StringVar(value="Auto")
        path_display_frame = ttk.Frame(main_frame)
        path_display_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(path_display_frame, text="Auto", variable=self.path_display_option, value="Auto").pack(side=tk.LEFT)
        ttk.Radiobutton(path_display_frame, text="Game Path", variable=self.path_display_option, value="Game Path").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(path_display_frame, text="Standard", variable=self.path_display_option, value="Standard").pack(side=tk.LEFT, padx=10)
        self.preview_btn = ttk.Button(main_frame, text="Preview", command=self.show_path_preview)
        self.preview_btn.grid(row=4, column=2, padx=5)
        
        # Help text for Path Display
        help_text = "Auto: Smart detection | Game Path: Use (path-to-game) | Standard: Use full path with masking"
        help_label = ttk.Label(main_frame, text=help_text, foreground="gray", font=("Segoe UI", 7))
        help_label.grid(row=5, column=1, columnspan=3, sticky=tk.W, padx=5, pady=(0, 5))
        
        # Backup Location
        ttk.Label(main_frame, text="Backup Location:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.backup_location = tk.StringVar()
        backup_entry = ttk.Entry(main_frame, textvariable=self.backup_location, width=50)
        backup_entry.grid(row=6, column=1, sticky=tk.EW, padx=5, pady=5)
        backup_entry.bind('<FocusOut>', lambda e: self.log(f"Backup location updated: {self.backup_location.get()}"))
        backup_entry.bind('<Return>', lambda e: self.log(f"Backup location updated: {self.backup_location.get()}"))
        ttk.Button(main_frame, text="Browse...", command=self.browse_backup).grid(row=6, column=2, padx=5)
        
        # Timestamp
        ttk.Label(main_frame, text="Timestamp:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.timestamp_option = tk.StringVar(value="Disable")
        timestamp_frame = ttk.Frame(main_frame)
        timestamp_frame.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(timestamp_frame, text="Disable", variable=self.timestamp_option, value="Disable").pack(side=tk.LEFT)
        ttk.Radiobutton(timestamp_frame, text="Enable", variable=self.timestamp_option, value="Enable").pack(side=tk.LEFT, padx=10)
        
        ttk.Button(main_frame, text="Credit Setting", command=self.open_credit_setting).grid(row=8, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.progress_bar.grid_remove()  # Hidden by default
        
        ttk.Label(main_frame, text="Log:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.log_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=11, column=0, columnspan=3, sticky=tk.NSEW, pady=5)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(11, weight=1)
        
        # Load last used values
        if "last_used" in self.config_manager.config:
            last = self.config_manager.config["last_used"]
            self.game_title.set(last.get("game_title", ""))
            self.savegame_location.set(last.get("savegame_location", ""))
            self.backup_location.set(last.get("backup_location", ""))
        
        # Load preferences
        self.load_preferences()
        
        # Tombol Create Backup
        self.create_backup_btn = ttk.Button(main_frame, text="Create Backup", command=self.create_backup)
        self.create_backup_btn.grid(row=12, column=1, pady=20)
        self.validate_inputs()  # Set initial state
        self.validate_list_button()  # Set initial state for List button
        
        # Update game directory info initially
        self.update_game_directory_info()
        
        # Pasang trace pada input
        self.game_title.trace_add('write', lambda *args: self.validate_inputs())
        self.savegame_location.trace_add('write', lambda *args: self.validate_inputs())
        self.savegame_location.trace_add('write', lambda *args: self.update_game_directory_info())
        self.backup_location.trace_add('write', lambda *args: self.validate_inputs())
        
        # Save preferences when changed
        self.path_display_option.trace_add('write', lambda *args: self.save_preferences())
        self.path_display_option.trace_add('write', lambda *args: self.update_game_directory_info())
        self.timestamp_option.trace_add('write', lambda *args: self.save_preferences())
    
    def on_game_selected(self, event):
        game = self.game_title.get()
        if game in self.config_manager.config["games"]:
            paths = self.config_manager.config["games"][game]
            self.savegame_location.set(paths.get("savegame_location", ""))
            self.backup_location.set(paths.get("backup_location", ""))
            self.log(f"Game selected: {game}")
    
    def on_game_manual_entry(self, event):
        game = self.game_title.get()
        if game in self.config_manager.config["games"]:
            paths = self.config_manager.config["games"][game]
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
    
    def update_progress(self, progress):
        """Update progress bar"""
        self.progress_var.set(progress)
        self.root.update()
    
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
            # Update configuration
            self.config_manager.add_game(game_title, savegame_location, backup_location)
            self.config_manager.update_last_used(game_title, savegame_location, backup_location)
            
            # Update backup history with current timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.config_manager.update_backup_history(game_title, current_time)
            
            self.config_manager.save_config()
            
            self.log(f"Starting backup for {game_title}...")
            
            # Show progress bar
            self.progress_bar.grid()
            self.progress_var.set(0)
            self.root.update()
            
            # Get author from config
            author = self.config_manager.config.get("last_used", {}).get("author", "").strip() or "Smothy"
            
            # Create backup
            self.backup_manager.create_backup(
                game_title, savegame_location, backup_location,
                self.timestamp_option.get(), self.path_display_option.get(),
                author, self._credit_note
            )
            
            # Hide progress bar
            self.progress_bar.grid_remove()
            self.progress_var.set(0)
            
            # Update dropdown values after successful backup
            self.update_dropdown_values()
            
            messagebox.showinfo("Success", "Backup completed successfully!")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
            # Hide progress bar on error
            self.progress_bar.grid_remove()
            self.progress_var.set(0)
    
    def show_game_list_window(self):
        """Show game list window"""
        GameListWindow(
            self.root,
            self.config_manager,
            self.on_game_selected_from_list,
            self.on_game_deleted_from_list
        )
    
    def on_game_selected_from_list(self, game_name):
        """Callback when game is selected from list"""
        self.game_title.set(game_name)
        self.on_game_selected(None)
        self.log(f"Game selected from list: {game_name}")
    
    def on_game_deleted_from_list(self, game_name):
        """Callback when game is deleted from list"""
        self.update_dropdown_values()
        if self.game_title.get() == game_name:
            self.game_title.set("")
            self.savegame_location.set("")
            self.backup_location.set("")
        self.log(f"Game '{game_name}' has been deleted from the list.")
    
    def open_credit_setting(self):
        """Open credit setting window"""
        CreditSettingWindow(
            self.root,
            self.config_manager,
            self.on_credit_saved
        )
    
    def on_credit_saved(self, author, note):
        """Callback when credit is saved"""
        self._credit_note = note
        self.log("Credit setting saved (Author dan Note).")
    
    def show_path_preview(self):
        """Show path preview window"""
        savegame_location = self.savegame_location.get().strip()
        if not savegame_location:
            messagebox.showinfo("Preview", "Please enter a savegame location first.")
            return
        
        PathPreviewWindow(
            self.root,
            savegame_location,
            self.path_display_option.get()
        )
    
    def validate_inputs(self):
        """Validate input fields and enable/disable create backup button and preview button"""
        game_title = self.game_title.get().strip()
        savegame_location = self.savegame_location.get().strip()
        backup_location = self.backup_location.get().strip()
        if game_title and savegame_location and backup_location:
            self.create_backup_btn.state(["!disabled"])
        else:
            self.create_backup_btn.state(["disabled"])
        # Enable/disable preview button
        if savegame_location:
            self.preview_btn.state(["!disabled"])
        else:
            self.preview_btn.state(["disabled"])

    def validate_list_button(self):
        """Validate list button state"""
        if self.config_manager.config["games"]:
            self.list_btn.state(["!disabled"])
        else:
            self.list_btn.state(["disabled"])

    def update_dropdown_values(self):
        """Update dropdown values with recent games (limit to 5 items)"""
        recent_games = self.config_manager.get_recent_games(5)
        self.game_title_combo['values'] = recent_games

    def update_game_directory_info(self):
        """Update the game directory detection info display"""
        savegame_location = self.savegame_location.get().strip()
        if savegame_location:
            # Tampilkan label jika ada input
            self.game_dir_label.grid()
            self.game_dir_action_label.grid()
            is_inside_game, game_dir, relative_path = detect_game_directory(savegame_location)
            preference = self.path_display_option.get()
            if is_inside_game and relative_path:
                game_name = os.path.basename(game_dir)
                self.game_dir_info.set(f"✓ Game detected: {game_name}")
                if preference == "Game Path":
                    self.game_dir_action.set(f"Will use: (path-to-game)/{relative_path}")
                elif preference == "Standard":
                    self.game_dir_action.set(f"Will use: Standard masking")
                else:  # Auto
                    self.game_dir_action.set(f"Will use: (path-to-game)/{relative_path}")
            else:
                self.game_dir_info.set(f"ℹ Standard savegame location")
                if preference == "Game Path":
                    self.game_dir_action.set(f"Will use: Standard masking (Game Path not applicable)")
                else:
                    self.game_dir_action.set(f"Will use: Standard masking")
        else:
            # Sembunyikan label jika kosong
            self.game_dir_label.grid_remove()
            self.game_dir_action_label.grid_remove()
            self.game_dir_info.set("")
            self.game_dir_action.set("")

    def load_preferences(self):
        """Load user preferences from config"""
        try:
            preferences = self.config_manager.get_preferences()
            self.path_display_option.set(preferences.get("path_display", "Auto"))
            self.timestamp_option.set(preferences.get("timestamp_option", "Disable"))
        except Exception as e:
            print(f"Error loading preferences: {e}")
    
    def save_preferences(self):
        """Save user preferences to config"""
        try:
            preferences = {
                "path_display": self.path_display_option.get(),
                "timestamp_option": self.timestamp_option.get()
            }
            self.config_manager.save_preferences(preferences)
            self.config_manager.save_config()
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def clear_all_inputs(self):
        """Membersihkan seluruh input di form utama."""
        self.game_title.set("")
        self.savegame_location.set("")
        self.backup_location.set("")
        self.path_display_option.set("Auto")
        self.timestamp_option.set("Disable")
        self.log("All inputs cleared for new entry.")

    def show_about(self):
        """Menampilkan informasi aplikasi dengan hyperlink pada 'Smothy'."""
        about_window = tk.Toplevel(self.root)
        about_window.title("Info")
        about_window.geometry("430x200")
        about_window.resizable(False, False)

        # Terapkan icon pada jendela info
        if os.path.exists(ICON_PATH):
            try:
                about_window.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Error loading icon for about window: {e}")
        else:
            print(f"Warning: Icon file not found at {ICON_PATH}")

        # Judul bold dan rata tengah
        title_label = tk.Label(about_window, text="Sweet Progress", font=("Segoe UI", 12, "bold"), anchor="center")
        title_label.pack(fill="x", pady=(18, 0))

        # Separator garis
        sep = ttk.Separator(about_window, orient="horizontal")
        sep.pack(fill="x", padx=20, pady=(8, 10))

        # Info text
        info_text = "Making game save backups simple, reliable, and maintainable!\nCreated by "
        label = tk.Label(about_window, text=info_text, font=("Segoe UI", 10), justify=tk.LEFT, anchor="w")
        label.pack(anchor="w", padx=28, pady=(0, 0))

        # Hyperlink label
        link = tk.Label(about_window, text="Smothy", font=("Segoe UI", 10, "underline"), fg="blue", cursor="hand2")
        link.pack(anchor="w", padx=28)
        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://guns.lol/smothyze"))

        # Tombol close
        close_btn = ttk.Button(about_window, text="Close", command=about_window.destroy)
        close_btn.pack(pady=15) 