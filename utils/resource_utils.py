import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
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

# Constants for resource paths
RESOURCE_DIR = resource_path("Resource")
ICON_PATH = os.path.join(RESOURCE_DIR, "icon.ico")
CONFIG_PATH = os.path.join(RESOURCE_DIR, "savegame_config.json") 