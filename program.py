import sys
import tkinter as tk
from ui.main_window import SaveGameBackupApp

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
