import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from utils.resource_utils import ICON_PATH
from utils.path_utils import detect_game_directory, mask_game_path_in_savegame_location, normalize_path_for_display
from utils.constants import DEFAULT_AUTHOR

# Utility function for consistent toplevel window creation
def create_toplevel_window(parent, title, geometry, icon_path=ICON_PATH):
    window = tk.Toplevel(parent)
    window.title(title)
    window.geometry(geometry)
    window.transient(parent)
    window.grab_set()
    window.resizable(False, False)
    try:
        if os.path.exists(icon_path):
            window.iconbitmap(icon_path)
    except Exception as e:
        print(f"Error loading icon for {title} window: {e}")
    return window

class GameListWindow:
    def __init__(self, parent, config_manager, on_game_selected_callback, on_game_deleted_callback, on_game_renamed_callback=None):
        self.parent = parent
        self.config_manager = config_manager
        self.on_game_selected_callback = on_game_selected_callback
        self.on_game_deleted_callback = on_game_deleted_callback
        self.on_game_renamed_callback = on_game_renamed_callback

        self.window = create_toplevel_window(parent, "Game Title List", "500x500")
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ttk.Frame(self.window, padding=(16, 12, 16, 0))
        header.pack(fill=tk.X)
        ttk.Label(header, text="Game Title List", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Separator(self.window, orient="horizontal").pack(fill=tk.X, padx=16, pady=(0, 10))

        # Sort options frame
        sort_frame = ttk.Frame(self.window)
        sort_frame.pack(fill=tk.X, padx=16, pady=(0, 5))
        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=(0, 10))
        self.sort_var = tk.StringVar(value="Last Used")
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, values=["Last Used", "Alphabetical"], state="readonly", width=15)
        sort_combo.pack(side=tk.LEFT)

        # Table frame
        table_frame = ttk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=5)
        columns = ("Game Title", "Last Used")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Game Title", text="Game Title")
        self.tree.heading("Last Used", text="Last Used")
        self.tree.column("Game Title", width=250, anchor="w")
        self.tree.column("Last Used", width=200, anchor="w")
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Button frame
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=16, pady=(0, 12))
        self.select_btn = ttk.Button(btn_frame, text="Select", command=self.select_game, state=tk.DISABLED)
        self.rename_btn = ttk.Button(btn_frame, text="Rename", command=self.rename_game, state=tk.DISABLED)
        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_game, state=tk.DISABLED)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        self.rename_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.update_buttons_state)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        self.refresh_table()
        self.update_buttons_state()

    def refresh_table(self):
        """Refresh the table based on current sort option"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get games with their last backup time
        games_with_time = []
        for gid, game in self.config_manager.config["games"].items():
            game_title = game.get("game_title", gid)
            last_backup_time = self.config_manager.config.get("backup_history", {}).get(gid, "Never")
            games_with_time.append((gid, game_title, last_backup_time))
        
        # Sort based on selected option
        if self.sort_var.get() == "Alphabetical":
            games_with_time.sort(key=lambda x: x[1].lower())
        else:
            games_with_time.sort(key=lambda x: x[2] if x[2] != "Never" else "1970-01-01 00:00:00", reverse=True)
        
        # Insert games into treeview
        for gid, game_title, last_backup in games_with_time:
            self.tree.insert("", tk.END, iid=gid, values=(game_title, last_backup))
    
    def select_game(self):
        """Select game from list"""
        selection = self.tree.selection()
        if selection:
            gid = selection[0]
            game = self.config_manager.get_game_by_id(gid)
            if game and self.on_game_selected_callback:
                self.on_game_selected_callback(gid)
            self.window.after(100, self.window.destroy)
    
    def delete_game(self):
        """Delete game from list"""
        selection = self.tree.selection()
        if selection:
            gid = selection[0]
            game = self.config_manager.get_game_by_id(gid)
            if game and messagebox.askyesno("Confirmation", f"Delete game title '{game.get('game_title', gid)}' from the list?"):
                try:
                    self.config_manager.delete_game(gid)
                    self.config_manager.save_config()
                    self.tree.delete(gid)
                    if self.on_game_deleted_callback:
                        self.on_game_deleted_callback(gid)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete game: {str(e)}")
    
    def rename_game(self):
        """Rename game title"""
        selection = self.tree.selection()
        if selection:
            gid = selection[0]
            game = self.config_manager.get_game_by_id(gid)
            if game:
                current_title = game.get('game_title', gid)
                
                # Create rename dialog
                rename_dialog = create_toplevel_window(self.window, "Rename Game Title", "350x180")
                
                # Center the dialog
                rename_dialog.geometry("+%d+%d" % (
                    self.window.winfo_rootx() + 75,
                    self.window.winfo_rooty() + 75
                ))
                
                # Create widgets
                main_frame = ttk.Frame(rename_dialog, padding=16)
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Current title info
                ttk.Label(main_frame, text="Current Title:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
                current_label = ttk.Label(main_frame, text=current_title, foreground="gray")
                current_label.pack(anchor=tk.W, pady=(0, 12))
                
                # New title input
                ttk.Label(main_frame, text="New Title:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 8))
                title_var = tk.StringVar(value=current_title)
                title_entry = ttk.Entry(main_frame, textvariable=title_var, width=35)
                title_entry.pack(fill=tk.X, pady=(0, 16))
                title_entry.select_range(0, tk.END)
                title_entry.focus()
                
                # Button frame
                btn_frame = ttk.Frame(main_frame)
                btn_frame.pack(fill=tk.X)
                ttk.Button(btn_frame, text="Cancel", command=rename_dialog.destroy).pack(side=tk.RIGHT, padx=5)
                ttk.Button(btn_frame, text="Save", command=lambda: self._perform_rename(gid, title_var.get().strip(), rename_dialog)).pack(side=tk.RIGHT, padx=5)
                
                # Bind Enter key to rename
                title_entry.bind("<Return>", lambda e: self._perform_rename(gid, title_var.get().strip(), rename_dialog))
                title_entry.bind("<Escape>", lambda e: rename_dialog.destroy)
    
    def _perform_rename(self, gid, new_title, dialog):
        """Perform the actual rename operation"""
        if not new_title:
            messagebox.showerror("Error", "Game title cannot be empty")
            return
        
        try:
            self.config_manager.rename_game(gid, new_title)
            self.config_manager.save_config()
            
            # Update the tree view
            self.refresh_table()
            
            # Close the dialog
            dialog.destroy()
            
            # Call the callback if provided
            if self.on_game_renamed_callback:
                game = self.config_manager.get_game_by_id(gid)
                old_title = game.get('game_title', gid) if game else gid
                self.on_game_renamed_callback(gid, old_title, new_title)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename game: {str(e)}")
    
    def update_buttons_state(self, event=None):
        """Update button states based on selection"""
        selection = self.tree.selection()
        if selection:
            self.select_btn.state(["!disabled"])
            self.rename_btn.state(["!disabled"])
            self.delete_btn.state(["!disabled"])
        else:
            self.select_btn.state(["disabled"])
            self.rename_btn.state(["disabled"])
            self.delete_btn.state(["disabled"])

class CreditSettingWindow:
    def __init__(self, parent, config_manager, on_save_callback, on_reset_callback=None):
        self.parent = parent
        self.config_manager = config_manager
        self.on_save_callback = on_save_callback
        self.on_reset_callback = on_reset_callback
        self.window = create_toplevel_window(parent, "Credit Setting", "420x240")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)
        # Header
        ttk.Label(main_frame, text="Credit Information", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        ttk.Separator(main_frame, orient="horizontal").grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        # Author
        ttk.Label(main_frame, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
        # Get author from config or use default
        saved_author = self.config_manager.config.get("last_used", {}).get("author", "").strip()
        # Check if author was explicitly reset (empty string in config means reset)
        if "last_used" in self.config_manager.config and "author" in self.config_manager.config["last_used"]:
            # Author was explicitly reset, use empty string
            default_author = saved_author
        else:
            # Author was never set, use default
            default_author = saved_author if saved_author else DEFAULT_AUTHOR
        self.author_var = tk.StringVar(value=default_author)
        author_entry = ttk.Entry(main_frame, textvariable=self.author_var, width=36)
        author_entry.grid(row=2, column=1, sticky=tk.EW, pady=(0, 8))
        # Note
        ttk.Label(main_frame, text="Note (optional):").grid(row=3, column=0, sticky=tk.NW, pady=(0, 8))
        self.note_text = tk.Text(main_frame, width=36, height=5, wrap=tk.WORD)
        self.note_text.grid(row=3, column=1, sticky=tk.EW, pady=(0, 8))
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(8, 0))
        ttk.Button(btn_frame, text="Reset", command=self.reset_credit).pack(side=tk.LEFT, padx=5)
        self.save_btn = ttk.Button(btn_frame, text="Save", state=tk.DISABLED, command=self.save_credit)
        self.save_btn.pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        # Bind validation
        self.author_var.trace_add("write", self.validate_save_btn)
        self.note_text.bind("<KeyRelease>", lambda e: self.validate_save_btn())
        self.window.columnconfigure(1, weight=1)
        self.validate_save_btn()

    def validate_save_btn(self, *args):
        """Validate save button state"""
        author = self.author_var.get().strip()
        note = self.note_text.get("1.0", tk.END).strip()
        if author or note:
            self.save_btn.state(["!disabled"])
        else:
            self.save_btn.state(["disabled"])
    
    def save_credit(self):
        """Save credit settings"""
        try:
            author = self.author_var.get().strip()
            note = self.note_text.get("1.0", tk.END).strip()
            
            if "last_used" not in self.config_manager.config:
                self.config_manager.config["last_used"] = {}
            self.config_manager.config["last_used"]["author"] = author
            self.config_manager.save_config()
            
            if self.on_save_callback:
                self.on_save_callback(author, note)
            
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credit settings: {str(e)}")
    
    def reset_credit(self):
        """Reset credit settings - clear author and close window"""
        try:
            # Clear author from config
            if "last_used" in self.config_manager.config:
                self.config_manager.config["last_used"]["author"] = ""
                self.config_manager.save_config()
            
            # Clear the input fields
            self.author_var.set("")
            self.note_text.delete("1.0", tk.END)
            
            # Call reset callback if provided
            if self.on_reset_callback:
                self.on_reset_callback()
            
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset credit settings: {str(e)}")

class PathPreviewWindow:
    pass

class PreferencesWindow:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.window = None
        self.on_saved = None
        
    def show(self):
        if self.window:
            self.window.deiconify()
            self.window.focus_force()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Preferences")
        self.window.geometry("500x500")
        self.window.resizable(False, False)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        # Load current preferences
        self.load_preferences()
        
        # Adjust size to fit content so buttons are not cut off, then center
        self.window.update_idletasks()
        req_w = max(500, self.window.winfo_reqwidth())
        req_h = max(500, self.window.winfo_reqheight())
        x = (self.window.winfo_screenwidth() // 2) - (req_w // 2)
        y = (self.window.winfo_screenheight() // 2) - (req_h // 2)
        self.window.geometry(f"{req_w}x{req_h}+{x}+{y}")
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Preferences", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Backup Settings Section
        backup_frame = ttk.LabelFrame(main_frame, text="Backup Settings", padding="15")
        backup_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Save output directory option
        self.save_output_dir_var = tk.BooleanVar()
        save_output_check = ttk.Checkbutton(
            backup_frame, 
            text="Save output directory", 
            variable=self.save_output_dir_var,
            command=self.on_save_output_dir_changed
        )
        save_output_check.pack(anchor=tk.W, pady=5)
        
        # Removed help text under Save output directory for cleaner UI
        
        # Default backup directory
        ttk.Label(backup_frame, text="Default Backup Directory:").pack(anchor=tk.W, pady=(10, 5))
        
        dir_frame = ttk.Frame(backup_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.default_backup_dir = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.default_backup_dir, width=40)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_default_backup_dir)
        browse_btn.pack(side=tk.RIGHT)
        
        # Path Display Settings Section
        path_frame = ttk.LabelFrame(main_frame, text="Path Display Settings", padding="15")
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Path display option
        ttk.Label(path_frame, text="Default Path Display:").pack(anchor=tk.W, pady=(0, 5))
        
        self.path_display_var = tk.StringVar()
        path_display_frame = ttk.Frame(path_frame)
        path_display_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(path_display_frame, text="Auto", variable=self.path_display_var, value="Auto").pack(side=tk.LEFT)
        ttk.Radiobutton(path_display_frame, text="Game Path", variable=self.path_display_var, value="Game Path").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(path_display_frame, text="Standard", variable=self.path_display_var, value="Standard").pack(side=tk.LEFT, padx=10)
        
        # Timestamp Settings Section
        timestamp_frame = ttk.LabelFrame(main_frame, text="Timestamp Settings", padding="15")
        timestamp_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Timestamp option
        self.timestamp_var = tk.StringVar()
        timestamp_frame_inner = ttk.Frame(timestamp_frame)
        timestamp_frame_inner.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(timestamp_frame_inner, text="Enable", variable=self.timestamp_var, value="Enable").pack(side=tk.LEFT)
        ttk.Radiobutton(timestamp_frame_inner, text="Disable", variable=self.timestamp_var, value="Disable").pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        save_btn = ttk.Button(button_frame, text="Save", command=self.save_preferences)
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.close_window)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
    def load_preferences(self):
        """Load current preferences from config"""
        preferences = self.config_manager.get_preferences()
        
        self.save_output_dir_var.set(preferences.get("save_output_directory", True))
        self.path_display_var.set(preferences.get("path_display", "Auto"))
        self.timestamp_var.set(preferences.get("timestamp_option", "Disable"))
        
        # Load default backup directory from config
        default_backup = self.config_manager.config.get("default_backup_directory", "")
        self.default_backup_dir.set(default_backup)
        
    def save_preferences(self):
        """Save preferences to config"""
        try:
            preferences = {
                "save_output_directory": self.save_output_dir_var.get(),
                "path_display": self.path_display_var.get(),
                "timestamp_option": self.timestamp_var.get()
            }
            
            # Save preferences
            self.config_manager.save_preferences(preferences)
            
            # Save default backup directory
            if "default_backup_directory" not in self.config_manager.config:
                self.config_manager.config["default_backup_directory"] = ""
            self.config_manager.config["default_backup_directory"] = self.default_backup_dir.get()
            
            # Save config
            self.config_manager.save_config()
            
            # Notify parent about saved preferences
            if callable(self.on_saved):
                try:
                    self.on_saved()
                except Exception:
                    pass

            messagebox.showinfo("Success", "Preferences saved successfully!")
            self.close_window()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {str(e)}")
    
    def browse_default_backup_dir(self):
        """Browse for default backup directory"""
        directory = filedialog.askdirectory(
            title="Select Default Backup Directory",
            initialdir=self.default_backup_dir.get() if self.default_backup_dir.get() else os.path.expanduser("~")
        )
        if directory:
            self.default_backup_dir.set(directory)
    
    def on_save_output_dir_changed(self):
        """Handle save output directory checkbox change"""
        if self.save_output_dir_var.get():
            # Enable default backup directory field
            for child in self.window.winfo_children():
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.LabelFrame) and grandchild.cget("text") == "Backup Settings":
                            for great_grandchild in grandchild.winfo_children():
                                if isinstance(great_grandchild, ttk.Frame):
                                    for entry in great_grandchild.winfo_children():
                                        if isinstance(entry, ttk.Entry):
                                            entry.config(state="normal")
        else:
            # Disable default backup directory field
            for child in self.window.winfo_children():
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.LabelFrame) and grandchild.cget("text") == "Backup Settings":
                            for great_grandchild in grandchild.winfo_children():
                                if isinstance(great_grandchild, ttk.Frame):
                                    for entry in great_grandchild.winfo_children():
                                        if isinstance(entry, ttk.Entry):
                                            entry.config(state="disabled")
    
    def close_window(self):
        """Close preferences window"""
        if self.window:
            self.window.destroy()
            self.window = None 