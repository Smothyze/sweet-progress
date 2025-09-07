import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import webbrowser

from config.config_manager import ConfigManager
from backup.backup_manager import BackupManager
from utils.path_utils import validate_path, validate_game_title, detect_game_directory, normalize_path_for_display
from utils.resource_utils import ICON_PATH
from utils.logger import logger
from utils.exceptions import SweetProgressError
from utils.constants import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    MAX_LOG_LINES, MAX_RECENT_GAMES, DEFAULT_AUTHOR
)
from ui.windows import GameListWindow, CreditSettingWindow, PreferencesWindow

class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.enter)
        self.tipwindow = None

    def enter(self, event=None):
        self.show_tooltip()

    def leave(self, event=None):
        self.hide_tooltip()

    def show_tooltip(self):
        if self.tipwindow or not self.text:
            return
        try:
            x, y, cx, cy = self.widget.bbox("insert")
            x = x + self.widget.winfo_rootx() + 25
            y = y + cy + self.widget.winfo_rooty() + 25
        except:
            # For widgets that don't have bbox method (like Label)
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"), wraplength=300)
        label.pack(ipadx=1)

    def hide_tooltip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def update_text(self, new_text):
        self.text = new_text

class SaveGameBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Initialize backup option variables first (before menu creation)
        self.single_backup_var = tk.BooleanVar(value=True)  # Default checked
        
        # Add menu bar
        self.menu_bar = tk.Menu(self.root)
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_all_inputs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Option menu
        option_menu = tk.Menu(self.menu_bar, tearoff=0)
        # Backup submenu
        backup_submenu = tk.Menu(option_menu, tearoff=0)
        # Single Backup as a program indicator (always enabled, cannot be changed)
        backup_submenu.add_checkbutton(label="Single Backup", command=self.single_backup, variable=self.single_backup_var, state="disabled")
        backup_submenu.add_command(label="Batch Backup", command=self.batch_backup)
        option_menu.add_cascade(label="Backup", menu=backup_submenu)
        option_menu.add_separator()
        option_menu.add_command(label="Preferences", command=self.show_preferences)
        self.menu_bar.add_cascade(label="Option", menu=option_menu)
        
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
                logger.warning(f"Error loading icon: {e}")
        else:
            logger.warning(f"Icon file not found at {ICON_PATH}")
        
        # Initialize managers
        self.config_manager = ConfigManager()
        
        # Validate last_used after config is loaded
        self.config_manager.validate_last_used()
        
        self.backup_manager = BackupManager(
            self.config_manager,
            progress_callback=self.update_progress,
            log_callback=self.log
        )
        
        # Initialize windows
        self.preferences_window = PreferencesWindow(self.root, self.config_manager)
        # Ensure main window refreshes when preferences are saved
        self.preferences_window.on_saved = self.load_preferences
        
        self._credit_note = ""
        
        # Initialize log line counter
        self.log_line_count = 0
        self.max_log_lines = MAX_LOG_LINES
        
        self._selected_game_id = None
        
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
        self.game_title_combo['values'] = [title for _, title in recent_games]
        self._recent_game_ids = [gid for gid, _ in recent_games]
        
        self.game_title_combo.bind("<<ComboboxSelected>>", self.on_game_selected)
        self.game_title_combo.bind("<Return>", self.on_game_manual_entry)
        self.list_btn = ttk.Button(main_frame, text="List", command=self.show_game_list_window)
        self.list_btn.grid(row=0, column=2, padx=5)
        
        # Savegame Location
        # Centered section header above the input (middle column only)
        ttk.Label(main_frame, text="Savegame Location", anchor="center").grid(row=1, column=1, sticky=tk.EW, padx=5)
        # Location type dropdown (Folder/File) replaces the previous left label
        self.location_type = tk.StringVar(value="Folder")
        self.location_type_combo = ttk.Combobox(main_frame, textvariable=self.location_type, state="readonly", values=["Folder", "File"], width=10)
        self.location_type_combo.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.savegame_location = tk.StringVar()
        savegame_entry = ttk.Entry(main_frame, textvariable=self.savegame_location, width=50)
        savegame_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        savegame_entry.bind('<FocusOut>', lambda e: self.log(f"Savegame location updated: {self.savegame_location.get()}"))
        savegame_entry.bind('<Return>', lambda e: self.log(f"Savegame location updated: {self.savegame_location.get()}"))
        ttk.Button(main_frame, text="Browse...", command=self.browse_savegame).grid(row=2, column=2, padx=5)
        
        # Game directory info - single icon with combined tooltip (positioned below savegame field, aligned with the field)
        self.game_dir_info = tk.StringVar()
        self.game_dir_action = tk.StringVar()
        self.game_dir_info_icon = tk.Label(main_frame, text="ⓘ", foreground="blue", font=("Segoe UI", 12), cursor="hand2")
        self.game_dir_info_icon.grid(row=3, column=1, sticky=tk.E, padx=5, pady=(0, 5))  # Position below savegame field, aligned with the field
        self.game_dir_info_icon.grid_remove()  # Hide initially
        self.game_dir_info_tooltip = ToolTip(self.game_dir_info_icon, "")
        
        # Path display option is controlled via Preferences
        self.path_display_option = tk.StringVar(value=self.config_manager.get_preferences().get("path_display", "Auto"))
        
        # Help text removed (settings are now in Preferences)
        
        # Backup Location
        ttk.Label(main_frame, text="Backup Location:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.backup_location = tk.StringVar()
        backup_entry = ttk.Entry(main_frame, textvariable=self.backup_location, width=50)
        backup_entry.grid(row=6, column=1, sticky=tk.EW, padx=5, pady=5)
        backup_entry.bind('<FocusOut>', lambda e: self.log(f"Backup location updated: {self.backup_location.get()}"))
        backup_entry.bind('<Return>', lambda e: self.log(f"Backup location updated: {self.backup_location.get()}"))
        ttk.Button(main_frame, text="Browse...", command=self.browse_backup).grid(row=6, column=2, padx=5)
        
        # Timestamp controls moved to Preferences
        self.timestamp_option = tk.StringVar(value="Disable")
        
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
            game_id = last.get("game_id")
            
            # If game_id exists and the game still exists in the list, load the values
            if game_id and game_id in self.config_manager.config["games"]:
                self.game_title.set(last.get("game_title", ""))
                self.savegame_location.set(last.get("savegame_location", ""))
                self.backup_location.set(last.get("backup_location", ""))
                self._selected_game_id = game_id
            else:
                # Game no longer exists, clear last_used
                self.config_manager.config["last_used"] = {}
        
        # Load preferences
        self.load_preferences()
        
        # Create Backup Button
        self.create_backup_btn = ttk.Button(main_frame, text="Create Backup", command=self.create_backup)
        self.create_backup_btn.grid(row=12, column=1, pady=20)
        self.validate_inputs()  # Set initial state
        self.validate_list_button()  # Set initial state for List button
        
        # Update game directory info initially
        self.update_game_directory_info()
        
        # Attach trace to input fields
        self.game_title.trace_add('write', lambda *args: self.validate_inputs())
        self.savegame_location.trace_add('write', lambda *args: self.validate_inputs())
        self.savegame_location.trace_add('write', lambda *args: self.update_game_directory_info())
        if hasattr(self, 'location_type_combo'):
            self.location_type_combo.bind('<<ComboboxSelected>>', self.on_location_type_changed)
        self.backup_location.trace_add('write', lambda *args: self.validate_inputs())
        
        # React to path display changes locally; saving handled in Preferences window
        self.path_display_option.trace_add('write', lambda *args: self.update_game_directory_info())
        # Note: single_backup_var tidak perlu trace karena selalu aktif dan tidak bisa diubah
        
        # Initialize default backup directory if preferences are enabled
        self.initialize_default_backup_directory()
    
    def _get_default_backup_directory(self):
        """Helper method to get default backup directory if enabled"""
        preferences = self.config_manager.get_preferences()
        if preferences.get("save_output_directory", False):
            default_backup_dir = self.config_manager.config.get("default_backup_directory", "")
            if default_backup_dir and os.path.exists(default_backup_dir):
                return default_backup_dir
        return None
    
    def on_game_selected(self, event):
        title = self.game_title.get()
        gid = self.config_manager.get_game_id_by_title(title)
        if gid:
            game = self.config_manager.get_game_by_id(gid)
            self.savegame_location.set(game.get("savegame_location", ""))
            
            # Check if we should use default backup directory
            default_backup_dir = self._get_default_backup_directory()
            if default_backup_dir:
                self.backup_location.set(default_backup_dir)
                self.log(f"Using default backup directory: {default_backup_dir}")
            else:
                self.backup_location.set(game.get("backup_location", ""))
            
            self._selected_game_id = gid
            self.log(f"Game selected: {title}")
    
    def on_game_manual_entry(self, event):
        title = self.game_title.get()
        gid = self.config_manager.get_game_id_by_title(title)
        if gid:
            game = self.config_manager.get_game_by_id(gid)
            self.savegame_location.set(game.get("savegame_location", ""))
            
            # Check if we should use default backup directory
            default_backup_dir = self._get_default_backup_directory()
            if default_backup_dir:
                self.backup_location.set(default_backup_dir)
            else:
                self.backup_location.set(game.get("backup_location", ""))
            
            self._selected_game_id = gid
    
    def browse_savegame(self):
        mode = self.location_type.get() if hasattr(self, 'location_type') else "Folder"
        if mode == "File":
            path = filedialog.askopenfilename(title="Select savegame file")
        else:
            path = filedialog.askdirectory(title="Select savegame folder")
        if path:
            # Validate the selected path
            is_valid, message = validate_path(path)
            if is_valid:
                self.savegame_location.set(path)
                self.log(f"Savegame {mode.lower()} selected: {path}")
            else:
                self.show_error_dialog("Invalid Path", message)
    
    def browse_backup(self):
        # Check if we should use default backup directory
        default_backup_dir = self._get_default_backup_directory()
        if default_backup_dir:
            self.show_info_dialog("Info", f"Using default backup directory: {default_backup_dir}\n\nYou can change this in Options > Preferences.")
            return
        
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
                self.show_error_dialog("Error", f"Selected folder is not writable: {str(e)}")
    
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
    
    def on_location_type_changed(self, event=None):
        """Reset path when switching between Folder/File to avoid mismatch in Readme."""
        # Clear current path to force user to re-pick correct type
        self.savegame_location.set("")
        # Update tooltip/info display
        self.update_game_directory_info()
    
    def create_backup(self):
        game_title = self.game_title.get().strip()
        savegame_location = self.savegame_location.get().strip()
        backup_location = self.backup_location.get().strip()
        
        # Validate inputs
        is_valid_title, title_message = validate_game_title(game_title)
        if not is_valid_title:
            self.show_error_dialog("Error", title_message)
            return
            
        is_valid_source, source_message = validate_path(savegame_location)
        if not is_valid_source:
            self.show_error_dialog("Error", source_message)
            return
        
        # Check if we should use default backup directory
        default_backup_dir = self._get_default_backup_directory()
        if default_backup_dir:
            backup_location = default_backup_dir
            self.log(f"Using default backup directory: {backup_location}")
            # Update the backup location field to show the user
            self.backup_location.set(backup_location)
        
        is_valid_backup, backup_message = validate_path(backup_location)
        if not is_valid_backup:
            self.show_error_dialog("Error", backup_message)
            return
        
        # Check if backup location is writable
        try:
            test_file = os.path.join(backup_location, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            self.show_error_dialog("Error", f"Backup location is not writable: {str(e)}")
            return
            
        try:
            # Update configuration (add or update by id)
            gid = self._selected_game_id
            # Additional: if gid is None, check if the title already exists
            if gid is None:
                gid = self.config_manager.get_game_id_by_title(game_title)
            gid = self.config_manager.add_game(game_title, savegame_location, backup_location, game_id=gid)
            self._selected_game_id = gid
            self.config_manager.update_last_used(game_title, savegame_location, backup_location, game_id=gid)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.config_manager.update_backup_history(gid, current_time)
            self.config_manager.save_config()
            self.log(f"Starting backup for {game_title}...")
            
            # Show progress bar
            self.progress_bar.grid()
            self.progress_var.set(0)
            self.root.update()
            
            # Get author from config or use default
            author = self.config_manager.config.get("last_used", {}).get("author", "").strip()
            if not author:
                # Check if author was explicitly reset (empty string in config means reset)
                if "last_used" in self.config_manager.config and "author" in self.config_manager.config["last_used"]:
                    # Author was explicitly reset, use empty string
                    author = ""
                else:
                    # Author was never set, use default
                    author = DEFAULT_AUTHOR
            
            # Create backup
            # Determine backup mode based on selection (Folder/File)
            backup_mode = self.location_type.get() if hasattr(self, 'location_type') else "Folder"

            # Extra validation: ensure path type matches selected mode
            if backup_mode == "Folder" and not os.path.isdir(savegame_location):
                self.show_error_dialog("Error", "Selected path is not a folder. Please select a folder or switch to File mode.")
                return
            if backup_mode == "File" and not os.path.isfile(savegame_location):
                self.show_error_dialog("Error", "Selected path is not a file. Please select a file or switch to Folder mode.")
                return

            self.backup_manager.create_backup(
                game_title, savegame_location, backup_location,
                self.timestamp_option.get(), self.path_display_option.get(),
                author, self._credit_note, backup_mode
            )
            
            # Hide progress bar
            self.progress_bar.grid_remove()
            self.progress_var.set(0)
            
            # Update dropdown values after successful backup
            self.update_dropdown_values()
            # Enable list button if backup was successful
            self.validate_list_button()
            
            # Show custom success dialog with "Open Folder" button
            self.show_backup_success_dialog(backup_location)
        except Exception as e:
            self.log(f"Error: {str(e)}")
            # Show custom error dialog with consistent design
            self.show_backup_error_dialog(str(e))
            # Hide progress bar on error
            self.progress_bar.grid_remove()
            self.progress_var.set(0)
    
    def show_game_list_window(self):
        """Show game list window"""
        GameListWindow(
            self.root,
            self.config_manager,
            self.on_game_selected_from_list,
            self.on_game_deleted_from_list,
            self.on_game_renamed_from_list
        )
    
    def on_game_selected_from_list(self, gid):
        """Callback when game is selected from list"""
        game = self.config_manager.get_game_by_id(gid)
        if game:
            self._selected_game_id = gid
            self.game_title.set(game.get("game_title", ""))
            self.savegame_location.set(game.get("savegame_location", ""))
            
            # Check if we should use default backup directory
            default_backup_dir = self._get_default_backup_directory()
            if default_backup_dir:
                self.backup_location.set(default_backup_dir)
                self.log(f"Using default backup directory: {default_backup_dir}")
            else:
                self.backup_location.set(game.get("backup_location", ""))
            
            self.log(f"Game selected from list: {game.get('game_title', '')}")
    
    def on_game_deleted_from_list(self, gid):
        """Callback when game is deleted from list"""
        self.update_dropdown_values()
        if self._selected_game_id == gid:
            self._selected_game_id = None
            self.game_title.set("")
            self.savegame_location.set("")
            
            # Check if we should use default backup directory
            default_backup_dir = self._get_default_backup_directory()
            if default_backup_dir:
                self.backup_location.set(default_backup_dir)
            else:
                self.backup_location.set("")
        
        game = self.config_manager.get_game_by_id(gid)
        self.log(f"Game '{game.get('game_title', gid) if game else gid}' has been deleted from the list.")
        
        # Update list button state after game deletion
        self.validate_list_button()
    
    def on_game_renamed_from_list(self, gid, old_title, new_title):
        """Callback when game is renamed from list"""
        self.update_dropdown_values()
        if self._selected_game_id == gid:
            self.game_title.set(new_title)
        self.log(f"Game title renamed from '{old_title}' to '{new_title}'")
        
        # Update list button state after game rename
        self.validate_list_button()
    
    def open_credit_setting(self):
        """Open credit setting window"""
        CreditSettingWindow(
            self.root,
            self.config_manager,
            self.on_credit_saved,
            self.on_credit_reset
        )
    
    def on_credit_saved(self, author, note):
        """Callback when credit is saved"""
        self._credit_note = note
        self.log("Credit setting saved (Author dan Note).")
    
    def on_credit_reset(self):
        """Callback when credit is reset"""
        self._credit_note = ""
        self.log("Credit setting reset - Author cleared.")
    
    def validate_inputs(self):
        """Validate input fields and enable/disable create backup button and preview button"""
        game_title = self.game_title.get().strip()
        savegame_location = self.savegame_location.get().strip()
        backup_location = self.backup_location.get().strip()
        
        # Check if we should use default backup directory
        default_backup_dir = self._get_default_backup_directory()
        if default_backup_dir:
            backup_location = default_backup_dir
        
        if game_title and savegame_location and backup_location:
            self.create_backup_btn.state(["!disabled"])
        else:
            self.create_backup_btn.state(["disabled"])

    def validate_list_button(self):
        """Validate list button state"""
        if self.config_manager.config["games"]:
            self.list_btn.state(["!disabled"])
        else:
            self.list_btn.state(["disabled"])

    def update_dropdown_values(self):
        """Update dropdown values with recent games (limit to 5 items)"""
        recent_games = self.config_manager.get_recent_games(5)
        self.game_title_combo['values'] = [title for _, title in recent_games]
        self._recent_game_ids = [gid for gid, _ in recent_games]

    def update_game_directory_info(self):
        """Update the game directory detection info display"""
        savegame_location = self.savegame_location.get().strip()
        if savegame_location:
            # Show icon if there is input
            self.game_dir_info_icon.grid()
            is_inside_game, game_dir, relative_path = detect_game_directory(savegame_location)
            preference = self.path_display_option.get()
            
            if is_inside_game and relative_path:
                game_name = os.path.basename(game_dir)
                display_relative_path = normalize_path_for_display(relative_path)
                info_text = f"✓ Game detected: {game_name}"
                if preference == "Game Path":
                    action_text = f"Will use: (path-to-game)/{display_relative_path}"
                elif preference == "Standard":
                    action_text = f"Will use: Standard masking"
                else:  # Auto
                    action_text = f"Will use: (path-to-game)/{display_relative_path}"
            else:
                info_text = f"ℹ Standard savegame location"
                if preference == "Game Path":
                    action_text = f"Will use: Standard masking (Game Path not applicable)"
                else:
                    action_text = f"Will use: Standard masking"
            
            # Combine both info and action into single tooltip
            combined_tooltip = f"{info_text}\n{action_text}"
            self.game_dir_info.set(info_text)
            self.game_dir_action.set(action_text)
            self.game_dir_info_tooltip.update_text(combined_tooltip)
        else:
            # Hide icon if there is no input
            self.game_dir_info_icon.grid_remove()
            self.game_dir_info.set("")
            self.game_dir_action.set("")
            self.game_dir_info_tooltip.update_text("")

    def load_preferences(self):
        """Load user preferences from config"""
        try:
            preferences = self.config_manager.get_preferences()
            self.path_display_option.set(preferences.get("path_display", "Auto"))
            self.timestamp_option.set(preferences.get("timestamp_option", "Disable"))
            # Folder Backup selalu aktif, tidak perlu load dari config
            
            # Load save_output_directory preference
            save_output_dir = preferences.get("save_output_directory", False)
            if save_output_dir:
                default_backup_dir = self.config_manager.config.get("default_backup_directory", "")
                if default_backup_dir and os.path.exists(default_backup_dir):
                    # Only set if backup_location is empty
                    if not self.backup_location.get().strip():
                        self.backup_location.set(default_backup_dir)
        except Exception as e:
            print(f"Error loading preferences: {e}")
    
    def save_preferences(self):
        """Save user preferences to config"""
        try:
            preferences = {
                "path_display": self.path_display_option.get(),
                "timestamp_option": self.timestamp_option.get(),
                "save_output_directory": False  # Default to disabled
                # Folder Backup tidak perlu disimpan karena selalu aktif
            }
            self.config_manager.save_preferences(preferences)
            self.config_manager.save_config()
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def clear_all_inputs(self):
        """Clear all inputs in the main form."""
        self.game_title.set("")
        self.savegame_location.set("")
        
        # Check if we should use default backup directory
        default_backup_dir = self._get_default_backup_directory()
        if default_backup_dir:
            self.backup_location.set(default_backup_dir)
        else:
            self.backup_location.set("")
        
        self.path_display_option.set("Auto")
        self.timestamp_option.set("Disable")
        self.log("All inputs cleared for new entry.")

    def show_backup_success_dialog(self, backup_location):
        """Show custom success dialog with option to open backup folder"""
        # Create custom dialog
        success_dialog = tk.Toplevel(self.root)
        success_dialog.title("Backup Success")
        success_dialog.geometry("400x150")
        success_dialog.resizable(False, False)
        success_dialog.transient(self.root)
        success_dialog.grab_set()
        
        # Apply icon to success dialog
        if os.path.exists(ICON_PATH):
            try:
                success_dialog.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Error loading icon for success dialog: {e}")
        
        # Center the dialog
        success_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        # Main frame
        main_frame = ttk.Frame(success_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success icon and message
        success_frame = ttk.Frame(main_frame)
        success_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Success icon (using text symbol)
        success_icon = tk.Label(success_frame, text="✓", font=("Segoe UI", 24, "bold"), fg="green")
        success_icon.pack(side=tk.LEFT, padx=(0, 15))
        
        # Success message
        message_frame = ttk.Frame(success_frame)
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(message_frame, text="Backup Completed!", font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(message_frame, text="Your save game has been backed up successfully.", font=("Segoe UI", 9))
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Open Folder button
        open_folder_btn = ttk.Button(
            button_frame, 
            text="Open Folder", 
            command=lambda: self.open_backup_folder(backup_location, success_dialog)
        )
        open_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(button_frame, text="Close", command=success_dialog.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key to open folder and Escape to close
        success_dialog.bind("<Return>", lambda e: self.open_backup_folder(backup_location, success_dialog))
        success_dialog.bind("<Escape>", lambda e: success_dialog.destroy)
        
        # Focus on the dialog
        success_dialog.focus_set()
    
    def show_backup_error_dialog(self, error_message):
        """Show custom error dialog with consistent design"""
        self.show_error_dialog("Backup Failed", error_message)
    
    def show_error_dialog(self, title, error_message):
        """Show generic custom error dialog with consistent design"""
        # Create custom dialog
        error_dialog = tk.Toplevel(self.root)
        error_dialog.title(title)
        error_dialog.resizable(False, False)
        error_dialog.transient(self.root)
        error_dialog.grab_set()
        
        # Apply icon to error dialog
        if os.path.exists(ICON_PATH):
            try:
                error_dialog.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Error loading icon for error dialog: {e}")
        
        # Main frame
        main_frame = ttk.Frame(error_dialog, padding=(15, 10, 15, 10))  # (left, top, right, bottom) - reduced bottom padding
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon and message
        error_frame = ttk.Frame(main_frame)
        error_frame.pack(fill=tk.X, pady=(0, 12))  # Further reduced bottom padding
        
        # Error icon (using text symbol)
        error_icon = tk.Label(error_frame, text="✗", font=("Segoe UI", 24, "bold"), fg="red")
        error_icon.pack(side=tk.LEFT, padx=(0, 15))
        
        # Error message
        message_frame = ttk.Frame(error_frame)
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(message_frame, text=f"{title}!", font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor=tk.W)
        
        # Calculate optimal width for error message
        error_text = f"Error: {error_message}"
        # Estimate width based on text length (approximate 8 pixels per character for Segoe UI 9pt)
        estimated_width = min(max(len(error_text) * 8 + 100, 300), 600)  # Min 300, Max 600
        
        subtitle_label = tk.Label(message_frame, text=error_text, font=("Segoe UI", 9), 
                                wraplength=estimated_width-120, justify=tk.LEFT)
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Button frame with compact spacing
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(12, 5))  # Reduced top and bottom padding for more compact layout
        
        # Close button (centered)
        close_btn = ttk.Button(button_frame, text="Close", command=error_dialog.destroy)
        close_btn.pack(expand=True)
        
        # Bind Escape key to close
        error_dialog.bind("<Escape>", lambda e: error_dialog.destroy)
        
        # Calculate optimal dialog size based on content with dynamic height calculation
        error_dialog.update_idletasks()
        content_width = estimated_width + 80  # Add padding for icon and margins
        
        # Dynamic height calculation based on actual content
        base_height = 90  # Further reduced base height for title, icon, and basic layout
        text_lines = max(1, len(error_text) // (estimated_width // 8))  # Estimate text lines
        line_height = 16  # Reduced height per text line for more compact display
        button_area = 45  # Further reduced height for button area
        extra_padding = 10  # Further reduced extra padding
        
        content_height = base_height + (text_lines * line_height) + button_area + extra_padding
        
        # Set minimum and maximum sizes with more reasonable limits
        content_width = max(350, min(content_width, 700))
        content_height = max(130, min(content_height, 250))  # Further reduced height limits for more compact proportions
        
        # Set geometry and center the dialog
        error_dialog.geometry(f"{content_width}x{content_height}")
        error_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (content_width // 2),
            self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (content_height // 2)
        ))
        
        # Focus on the dialog
        error_dialog.focus_set()
    
    def show_info_dialog(self, title, message):
        """Show generic custom info dialog with consistent design"""
        # Create custom dialog
        info_dialog = tk.Toplevel(self.root)
        info_dialog.title(title)
        info_dialog.resizable(False, False)
        info_dialog.transient(self.root)
        info_dialog.grab_set()
        
        # Apply icon to info dialog
        if os.path.exists(ICON_PATH):
            try:
                info_dialog.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Error loading icon for info dialog: {e}")
        
        # Main frame
        main_frame = ttk.Frame(info_dialog, padding=(15, 10, 15, 10))  # (left, top, right, bottom) - reduced bottom padding
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info icon and message
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 12))  # Further reduced bottom padding
        
        # Info icon (using text symbol)
        info_icon = tk.Label(info_frame, text="ℹ", font=("Segoe UI", 24, "bold"), fg="blue")
        info_icon.pack(side=tk.LEFT, padx=(0, 15))
        
        # Info message
        message_frame = ttk.Frame(info_frame)
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(message_frame, text=f"{title}", font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor=tk.W)
        
        # Calculate optimal width for info message
        # Estimate width based on text length (approximate 8 pixels per character for Segoe UI 9pt)
        estimated_width = min(max(len(message) * 8 + 100, 300), 600)  # Min 300, Max 600
        
        subtitle_label = tk.Label(message_frame, text=message, font=("Segoe UI", 9), 
                                wraplength=estimated_width-120, justify=tk.LEFT)
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Button frame with compact spacing
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(12, 5))  # Reduced top and bottom padding for more compact layout
        
        # Close button (centered)
        close_btn = ttk.Button(button_frame, text="Close", command=info_dialog.destroy)
        close_btn.pack(expand=True)
        
        # Bind Escape key to close
        info_dialog.bind("<Escape>", lambda e: info_dialog.destroy)
        
        # Calculate optimal dialog size based on content with dynamic height calculation
        info_dialog.update_idletasks()
        content_width = estimated_width + 80  # Add padding for icon and margins
        
        # Dynamic height calculation based on actual content
        base_height = 90  # Further reduced base height for title, icon, and basic layout
        text_lines = max(1, len(message) // (estimated_width // 8))  # Estimate text lines
        line_height = 16  # Reduced height per text line for more compact display
        button_area = 45  # Further reduced height for button area
        extra_padding = 10  # Further reduced extra padding
        
        content_height = base_height + (text_lines * line_height) + button_area + extra_padding
        
        # Set minimum and maximum sizes with more reasonable limits
        content_width = max(350, min(content_width, 700))
        content_height = max(130, min(content_height, 250))  # Further reduced height limits for more compact proportions
        
        # Set geometry and center the dialog
        info_dialog.geometry(f"{content_width}x{content_height}")
        info_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (content_width // 2),
            self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (content_height // 2)
        ))
        
        # Focus on the dialog
        info_dialog.focus_set()
    
    def open_backup_folder(self, backup_location, dialog):
        """Open backup folder in file explorer and close dialog"""
        try:
            # Open folder in file explorer
            if os.name == 'nt':  # Windows
                os.startfile(backup_location)
            elif os.name == 'posix':  # macOS and Linux
                import subprocess
                subprocess.run(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', backup_location])
            
            # Close the dialog
            dialog.destroy()
            
            # Log the action
            self.log(f"Opened backup folder: {backup_location}")
            
        except Exception as e:
            # If opening folder fails, show error but keep dialog open
            self.show_error_dialog("Error", f"Failed to open folder: {str(e)}")
            self.log(f"Error opening backup folder: {str(e)}")

    def show_about(self):
        """Show application information with consistent styling and clickable author link."""
        # Create custom info-styled dialog
        info_dialog = tk.Toplevel(self.root)
        info_dialog.title("About")
        info_dialog.resizable(False, False)
        info_dialog.transient(self.root)
        info_dialog.grab_set()
        
        # Apply icon to info dialog
        if os.path.exists(ICON_PATH):
            try:
                info_dialog.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"Error loading icon for info dialog: {e}")
        
        # Main frame (match show_info_dialog spacing)
        main_frame = ttk.Frame(info_dialog, padding=(15, 10, 15, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info icon and message container
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Info icon
        info_icon = tk.Label(info_frame, text="ℹ", font=("Segoe UI", 24, "bold"), fg="blue")
        info_icon.pack(side=tk.LEFT, padx=(0, 15))
        
        # Message section
        message_frame = ttk.Frame(info_frame)
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(message_frame, text="About Sweet Progress", font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor=tk.W)
        
        subtitle_text = "Making game save backups simple, reliable, and maintainable!"
        # Estimate width similar to show_info_dialog
        estimated_width = min(max(len(subtitle_text) * 8 + 100, 300), 600)
        subtitle_label = tk.Label(message_frame, text=subtitle_text, font=("Segoe UI", 9), wraplength=estimated_width-120, justify=tk.LEFT)
        subtitle_label.pack(anchor=tk.W, pady=(2, 6))
        
        # Created by + hyperlink line
        created_by_container = ttk.Frame(message_frame)
        created_by_container.pack(anchor=tk.W)
        created_by_label = tk.Label(created_by_container, text="Created by ", font=("Segoe UI", 9))
        created_by_label.pack(side=tk.LEFT)
        
        link = tk.Label(created_by_container, text="Smothy", font=("Segoe UI", 9, "underline"), fg="blue", cursor="hand2")
        link.pack(side=tk.LEFT)
        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://guns.lol/smothyze"))
        
        # Buttons area
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(12, 5))
        close_btn = ttk.Button(button_frame, text="Close", command=info_dialog.destroy)
        close_btn.pack(expand=True)
        
        # Bind Escape to close
        info_dialog.bind("<Escape>", lambda e: info_dialog.destroy())
        
        # Dynamic sizing and centering (match show_info_dialog approach)
        info_dialog.update_idletasks()
        content_width = estimated_width + 80
        base_height = 90
        text_lines = max(1, len(subtitle_text) // (estimated_width // 8))
        line_height = 16
        button_area = 45
        extra_padding = 10
        content_height = base_height + (text_lines * line_height) + button_area + extra_padding
        content_width = max(350, min(content_width, 700))
        content_height = max(130, min(content_height, 250))
        
        info_dialog.geometry(f"{content_width}x{content_height}")
        info_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (content_width // 2),
            self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (content_height // 2)
        ))
        
        info_dialog.focus_set()
    
    def single_backup(self):
        """Handle Single Backup menu selection - always active as program indicator"""
        # Single Backup selalu aktif sebagai indikator program backup folder save game
        self.log("Single Backup is always active - this is the core functionality of Sweet Progress")
        self.show_info_dialog("Single Backup", "Single Backup is always active and cannot be disabled. This is the core functionality of Sweet Progress - a program designed specifically for backing up game save folders.")
    
    def batch_backup(self):
        """Handle Batch Backup menu selection"""
        self.log("Batch Backup option selected from Option menu")
        # TODO: Implement batch backup functionality
        self.show_info_dialog("Batch Backup", "Batch Backup functionality will be implemented in future versions.")
    
    def show_preferences(self):
        """Show preferences window"""
        self.log("Opening preferences window")
        self.preferences_window.show()
    
    def initialize_default_backup_directory(self):
        """Initialize default backup directory if preferences are enabled"""
        default_backup_dir = self._get_default_backup_directory()
        if default_backup_dir:
            # Only set if backup_location is empty
            if not self.backup_location.get().strip():
                self.backup_location.set(default_backup_dir)
                self.log(f"Initialized with default backup directory: {default_backup_dir}")