import os
import shutil
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import getpass

def get_current_username():
    return getpass.getuser()

def replace_username_in_path(path):
    if not path:
        return path
    
    current_username = get_current_username()
    
    parts = path.split('\\')
    if len(parts) > 2 and parts[1] == 'Users':
        parts[2] = current_username
        return '\\'.join(parts)
    return path

def mask_username_in_path(path):
    if not path:
        return path
    try:
        user_profile = os.environ.get('USERPROFILE')
        if user_profile and path.lower().startswith(user_profile.lower()):
            users_folder = os.path.dirname(user_profile)
            rest_of_path = path[len(user_profile):]
            return os.path.join(users_folder, '(pc-name)') + rest_of_path
    except Exception:
        pass

    parts = path.replace('/', '\\').split('\\')
    if len(parts) > 2 and parts[1].lower() == 'users':
        parts[2] = '(pc-name)'
        return '\\'.join(parts)
    return path

def mask_steamid_in_path(path):
    if not path:
        return path
    norm_path = path.replace('/', '\\')
    parts = norm_path.split('\\')
    for i in range(len(parts) - 2):
        if parts[i].lower() == 'steam' and parts[i+1].lower() == 'userdata':
            if parts[i+2].isdigit():
                parts[i+2] = '(steam-id)'
                return '\\'.join(parts)
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

RESOURCE_DIR = resource_path("Resource")
ICON_PATH = os.path.join(RESOURCE_DIR, "icon.ico")
CONFIG_PATH = os.path.join(RESOURCE_DIR, "savegame_config.json")

if not os.path.exists(ICON_PATH):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"The icon file not detected on: {ICON_PATH}\nThe application will be closed.")
    sys.exit(1)

class SaveGameBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sweet Progress")
        self.root.geometry("600x400")
        self.root.minsize(600, 400)
        try:
            self.root.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        self.config_file = CONFIG_PATH
        self.config = self.load_config()
        
        self.create_widgets()
        
    def load_config(self):
        default_config = {
            "games": {},
            "last_used": {}
        }
        
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding='utf-8') as f:
                    config = json.load(f)
                    
                for game in config["games"]:
                    game_config = config["games"][game]
                    game_config["savegame_location"] = replace_username_in_path(game_config["savegame_location"])
                    game_config["backup_location"] = replace_username_in_path(game_config["backup_location"])
                
                if "last_used" in config:
                    last_used = config["last_used"]
                    last_used["savegame_location"] = replace_username_in_path(last_used["savegame_location"])
                    last_used["backup_location"] = replace_username_in_path(last_used["backup_location"])
                
                return config
            else:
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
        all_games = list(self.config["games"].keys())
        recent_games = []
        if "last_used" in self.config and self.config["last_used"].get("game_title"):
            last = self.config["last_used"]
            if last["game_title"] in all_games:
                recent_games.append(last["game_title"])
        for g in all_games:
            if g not in recent_games:
                recent_games.append(g)
            if len(recent_games) == 3:
                break
        self.game_title_combo['values'] = recent_games
        self.game_title_combo.bind("<<ComboboxSelected>>", self.on_game_selected)
        self.game_title_combo.bind("<Return>", self.on_game_manual_entry)
        ttk.Button(main_frame, text="List", command=self.show_game_list_window).grid(row=0, column=2, padx=5)
        
        ttk.Label(main_frame, text="Savegame Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.savegame_location = tk.StringVar()
        savegame_entry = ttk.Entry(main_frame, textvariable=self.savegame_location, width=50)
        savegame_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_savegame).grid(row=1, column=2, padx=5)
        
        ttk.Label(main_frame, text="Backup Location:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.backup_location = tk.StringVar()
        backup_entry = ttk.Entry(main_frame, textvariable=self.backup_location, width=50)
        backup_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_backup).grid(row=2, column=2, padx=5)
        
        ttk.Label(main_frame, text="Timestamp:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.timestamp_option = tk.StringVar(value="Disable")
        timestamp_frame = ttk.Frame(main_frame)
        timestamp_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(timestamp_frame, text="Disable", variable=self.timestamp_option, value="Disable").pack(side=tk.LEFT)
        ttk.Radiobutton(timestamp_frame, text="Enable", variable=self.timestamp_option, value="Enable").pack(side=tk.LEFT, padx=10)
        
        ttk.Label(main_frame, text="Author:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.author_name = tk.StringVar()
        author_entry = ttk.Entry(main_frame, textvariable=self.author_name, width=50)
        author_entry.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(main_frame, text="Create Backup", command=self.create_backup).grid(row=5, column=1, pady=20)
        
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
            self.author_name.set(last.get("author", ""))
    
    def on_game_selected(self, event):
        game = self.game_title.get()
        if game in self.config["games"]:
            paths = self.config["games"][game]
            self.savegame_location.set(paths.get("savegame_location", ""))
            self.backup_location.set(paths.get("backup_location", ""))
    
    def on_game_manual_entry(self, event):
        game = self.game_title.get()
        if game in self.config["games"]:
            paths = self.config["games"][game]
            self.savegame_location.set(paths.get("savegame_location", ""))
            self.backup_location.set(paths.get("backup_location", ""))
    
    def browse_savegame(self):
        folder = filedialog.askdirectory()
        if folder:
            self.savegame_location.set(folder)
    
    def browse_backup(self):
        folder = filedialog.askdirectory()
        if folder:
            self.backup_location.set(folder)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def create_backup(self):
        game_title = self.game_title.get().strip()
        savegame_location = self.savegame_location.get().strip()
        backup_location = self.backup_location.get().strip()
        author_name = self.author_name.get().strip()
        timestamp_option = self.timestamp_option.get()
        
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
            self.config["games"][game_title] = {
                "savegame_location": savegame_location,
                "backup_location": backup_location
            }
            
            self.config["last_used"] = {
                "game_title": game_title,
                "savegame_location": savegame_location,
                "backup_location": backup_location,
                "author": author_name
            }
            
            self.save_config()
            
            self.log(f"Starting backup for {game_title}...")
            self.backup_savegame_with_credit(savegame_location, backup_location, game_title, author_name, timestamp_option)
            messagebox.showinfo("Success", "Backup completed successfully!")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def backup_savegame_with_credit(self, source_folder, backup_directory, game_name, author_name, timestamp_option):
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
            if timestamp_option == "Enable":
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_base_folder = os.path.join(game_folder, timestamp)
                os.makedirs(backup_base_folder)
                self.log(f"Created timestamped folder: {backup_base_folder}")
            
            source_folder_name = os.path.basename(source_folder.rstrip("/\\"))

            destination_folder = os.path.join(backup_base_folder, source_folder_name)

            if os.path.exists(destination_folder):
                shutil.rmtree(destination_folder)
                self.log(f"Removed existing backup at: {destination_folder}")
                
            shutil.copytree(source_folder, destination_folder)
            self.log(f"Backup successful! Savegame copied to: {destination_folder}")

            credit_file_path = os.path.join(backup_base_folder, "Readme.txt")
            backup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(credit_file_path, "w") as credit_file:
                credit_file.write(f"Backup savegame for {game_name}.\n")
                credit_file.write(f"\n")
                credit_file.write(f"Author:\n")
                credit_file.write(f"{author_name or 'Smothy'}\n")
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
            raise e

    def show_game_list_window(self):
        win = tk.Toplevel(self.root)
        win.title("Game Title List")
        win.geometry("350x300")
        win.transient(self.root)
        win.grab_set()
        try:
            win.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon for list window: {e}")
        win.resizable(False, False)

        listbox = tk.Listbox(win, exportselection=False)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        sorted_games = sorted(self.config["games"].keys(), key=lambda x: x.lower())
        for game in sorted_games:
            listbox.insert(tk.END, game)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        def select_game():
            sel = listbox.curselection()
            if sel:
                game = listbox.get(sel[0])
                self.game_title.set(game)
                self.on_game_selected(None)
                win.destroy()

        def delete_game():
            sel = listbox.curselection()
            if sel:
                game = listbox.get(sel[0])
                if messagebox.askyesno("Confirmation", f"Delete game title '{game}' from the list?"):
                    del self.config["games"][game]
                    self.save_config()
                    listbox.delete(sel[0])
                    self.game_title_combo['values'] = list(self.config["games"].keys())
                    if self.game_title.get() == game:
                        self.game_title.set("")
                        self.savegame_location.set("")
                        self.backup_location.set("")
                    self.log(f"Game '{game}' has been deleted from the list.")

        ttk.Button(btn_frame, text="Select", command=select_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=delete_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=5)

def main():
    root = tk.Tk()
    app = SaveGameBackupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
