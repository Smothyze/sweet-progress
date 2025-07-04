import tkinter as tk
from tkinter import ttk, messagebox
import os
from utils.resource_utils import ICON_PATH
from utils.path_utils import detect_game_directory, mask_game_path_in_savegame_location

class GameListWindow:
    def __init__(self, parent, config_manager, on_game_selected_callback, on_game_deleted_callback):
        self.parent = parent
        self.config_manager = config_manager
        self.on_game_selected_callback = on_game_selected_callback
        self.on_game_deleted_callback = on_game_deleted_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Game Title List")
        self.window.geometry("500x450")
        self.window.transient(parent)
        self.window.grab_set()
        
        try:
            if os.path.exists(ICON_PATH):
                self.window.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon for list window: {e}")
        
        self.window.resizable(False, False)
        self.create_widgets()
    
    def create_widgets(self):
        # Create sort options frame
        sort_frame = ttk.Frame(self.window)
        sort_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.sort_var = tk.StringVar(value="Last Used")
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, values=["Last Used", "Alphabetical"], 
                                 state="readonly", width=15)
        sort_combo.pack(side=tk.LEFT)

        # Create frame for treeview and scrollbar
        table_frame = ttk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview with columns
        columns = ("Game Title", "Last Used")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings
        self.tree.heading("Game Title", text="Game Title")
        self.tree.heading("Last Used", text="Last Used")
        
        # Configure column widths
        self.tree.column("Game Title", width=250, anchor="w")
        self.tree.column("Last Used", width=200, anchor="w")
        
        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        self.select_btn = ttk.Button(btn_frame, text="Select", command=self.select_game, state=tk.DISABLED)
        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_game, state=tk.DISABLED)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.update_buttons_state)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        # Initial load
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
    
    def update_buttons_state(self, event=None):
        """Update button states based on selection"""
        selection = self.tree.selection()
        if selection:
            self.select_btn.state(["!disabled"])
            self.delete_btn.state(["!disabled"])
        else:
            self.select_btn.state(["disabled"])
            self.delete_btn.state(["disabled"])

class CreditSettingWindow:
    def __init__(self, parent, config_manager, on_save_callback):
        self.parent = parent
        self.config_manager = config_manager
        self.on_save_callback = on_save_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Credit Setting")
        self.window.geometry("400x220")
        self.window.transient(parent)
        self.window.grab_set()
        
        try:
            if os.path.exists(ICON_PATH):
                self.window.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon for credit window: {e}")
        
        self.window.resizable(False, False)
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.window, text="Credit Information", font=("Segoe UI", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(16, 4), padx=16, sticky="w")

        # Separator
        sep = ttk.Separator(self.window, orient="horizontal")
        sep.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 10))

        # Author
        ttk.Label(self.window, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=(0, 8), padx=16)
        self.author_var = tk.StringVar(value=self.config_manager.config.get("last_used", {}).get("author", ""))
        author_entry = ttk.Entry(self.window, textvariable=self.author_var, width=36)
        author_entry.grid(row=2, column=1, sticky=tk.EW, pady=(0, 8), padx=(0, 16))

        # Note
        ttk.Label(self.window, text="Note (optional):").grid(row=3, column=0, sticky=tk.NW, pady=(0, 8), padx=16)
        self.note_text = tk.Text(self.window, width=36, height=5, wrap=tk.WORD)
        self.note_text.grid(row=3, column=1, sticky=tk.EW, pady=(0, 8), padx=(0, 16))

        # Frame untuk tombol
        btn_frame = ttk.Frame(self.window)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(8, 16), padx=16, sticky=tk.E)

        self.save_btn = ttk.Button(btn_frame, text="Save", state=tk.DISABLED, command=self.save_credit)
        self.save_btn.pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=(0, 8))

        # Bind validation
        self.author_var.trace_add("write", self.validate_save_btn)
        self.note_text.bind("<KeyRelease>", lambda e: self.validate_save_btn())

        # Configure grid
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

class PathPreviewWindow:
    def __init__(self, parent, savegame_location, path_display_option):
        self.parent = parent
        self.savegame_location = savegame_location
        self.path_display_option = path_display_option
        
        self.window = tk.Toplevel(parent)
        self.window.title("Path Preview")
        self.window.geometry("650x450")
        self.window.transient(parent)
        self.window.grab_set()
        
        try:
            if os.path.exists(ICON_PATH):
                self.window.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon for preview window: {e}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.window, text="README.txt Path Preview", font=("Segoe UI", 12, "bold"))
        title_label.pack(pady=(16, 8))
        
        # Separator
        sep = ttk.Separator(self.window, orient="horizontal")
        sep.pack(fill=tk.X, padx=16, pady=(0, 16))
        
        # Content frame
        content_frame = ttk.Frame(self.window, padding="16")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        
        # Original path
        ttk.Label(content_frame, text="Original Path:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        original_text = tk.Text(content_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        original_text.pack(fill=tk.X, pady=(4, 12))
        
        # Masked path
        ttk.Label(content_frame, text="Path in README.txt:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        masked_text = tk.Text(content_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        masked_text.pack(fill=tk.X, pady=(4, 12))
        
        # Detection info
        detection_frame = ttk.LabelFrame(content_frame, text="Detection Info", padding="8")
        detection_frame.pack(fill=tk.X, pady=(8, 0))
        
        detection_info = tk.Text(detection_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        detection_info.pack(fill=tk.X)
        
        # Usage examples frame
        examples_frame = ttk.LabelFrame(content_frame, text="Usage Examples", padding="8")
        examples_frame.pack(fill=tk.X, pady=(8, 0))
        
        examples_text = tk.Text(examples_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        examples_text.pack(fill=tk.X)
        
        # Update content
        original_text.config(state=tk.NORMAL)
        original_text.delete("1.0", tk.END)
        original_text.insert("1.0", self.savegame_location)
        original_text.config(state=tk.DISABLED)
        
        masked_path = mask_game_path_in_savegame_location(self.savegame_location, self.path_display_option)
        masked_text.config(state=tk.NORMAL)
        masked_text.delete("1.0", tk.END)
        masked_text.insert("1.0", masked_path)
        masked_text.config(state=tk.DISABLED)
        
        is_inside_game, game_dir, relative_path = detect_game_directory(self.savegame_location)
        detection_info.config(state=tk.NORMAL)
        detection_info.delete("1.0", tk.END)
        
        # Add preference info
        detection_info.insert("1.0", f"Current preference: {self.path_display_option}\n\n")
        
        if is_inside_game and relative_path:
            game_name = os.path.basename(game_dir)
            detection_info.insert(tk.END, f"✓ Game directory detected\n")
            detection_info.insert(tk.END, f"Game directory: {game_dir}\n")
            detection_info.insert(tk.END, f"Relative path: {relative_path}\n")
            detection_info.insert(tk.END, f"Result: {masked_path}")
            
            if self.path_display_option == "Game Path":
                detection_info.insert(tk.END, f"\n\n💡 This will be shared as: (path-to-game)/{relative_path}")
                detection_info.insert(tk.END, f"\nOther users can replace (path-to-game) with their game folder")
            elif self.path_display_option == "Standard":
                detection_info.insert(tk.END, f"\n\n💡 This will use standard masking (username, Steam ID)")
            else:  # Auto
                detection_info.insert(tk.END, f"\n\n💡 Auto mode: Using Game Path for game directories")
        else:
            detection_info.insert(tk.END, f"ℹ Standard savegame location\n")
            detection_info.insert(tk.END, f"Using standard masking (username, Steam ID)\n")
            detection_info.insert(tk.END, f"Result: {masked_path}")
            
            if self.path_display_option == "Game Path":
                detection_info.insert(tk.END, f"\n\n💡 Game Path not applicable for this location")
            elif self.path_display_option == "Standard":
                detection_info.insert(tk.END, f"\n\n💡 This will use standard masking (username, Steam ID)")
            else:  # Auto
                detection_info.insert(tk.END, f"\n\n💡 Auto mode: Using Standard for non-game directories")
        detection_info.config(state=tk.DISABLED)
        
        # Update examples
        examples_text.config(state=tk.NORMAL)
        examples_text.delete("1.0", tk.END)
        if is_inside_game and relative_path:
            examples_text.insert("1.0", "Game Path: (path-to-game)/game/saves\n")
            examples_text.insert(tk.END, "Standard: C:/Users/(pc-name)/AppData/...\n")
            examples_text.insert(tk.END, "Auto: Uses Game Path for game directories\n")
            examples_text.insert(tk.END, "\nNote: (path-to-game) will be replaced with actual game folder")
        else:
            examples_text.insert("1.0", "Standard: C:/Users/(pc-name)/AppData/...\n")
            examples_text.insert(tk.END, "Game Path: Same as Standard (not applicable)\n")
            examples_text.insert(tk.END, "Auto: Uses Standard for non-game directories\n")
            examples_text.insert(tk.END, "\nNote: Standard masking hides username and Steam ID")
        examples_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=(0, 16)) 