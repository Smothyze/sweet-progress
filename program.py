import sys
import tkinter as tk
from typing import NoReturn
from ui.main_window import SaveGameBackupApp
from utils.logger import logger
from utils.exceptions import SweetProgressError

def main() -> None:
    """Main entry point for the Sweet Progress application"""
    try:
        root = tk.Tk()
        app = SaveGameBackupApp(root)
        root.mainloop()
    except SweetProgressError as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
