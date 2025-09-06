import os
import getpass
from pathlib import Path
from utils.logger import logger

def get_current_username() -> str:
    """Get current system username"""
    try:
        return getpass.getuser()
    except Exception as e:
        logger.error(f"Failed to get username: {e}")
        return "unknown_user"

def normalize_path(path):
    """Normalize path to use system-specific separator"""
    if not path:
        return path
    return str(Path(path))

def normalize_path_for_display(path):
    """Normalize path for display purposes - always use forward slashes"""
    if not path:
        return path
    # Convert to forward slashes for consistent display
    return str(Path(path)).replace('\\', '/')

def replace_username_in_path(path):
    """Replace username in path with current username"""
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
    """Mask username in path for sharing"""
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
    """Mask Steam ID in path for sharing"""
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

def detect_steam_folder(path):
    """
    Detect if path contains Steam folder and return Steam folder info
    Returns: (is_steam_path, steam_folder, relative_path) or (False, None, None)
    """
    if not path:
        return False, None, None
    
    try:
        norm_path = normalize_path(path)
        parts = norm_path.split(os.sep)
        
        # Look for Steam folder in the path
        for i, part in enumerate(parts):
            if part.lower() == 'steam':
                steam_folder = os.sep.join(parts[:i+1])
                # Check if there are more parts after Steam folder
                if i + 1 < len(parts):
                    relative_path = os.sep.join(parts[i+1:])
                else:
                    relative_path = ""  # Path ends with Steam folder
                return True, steam_folder, relative_path
        
        return False, None, None
        
    except Exception:
        return False, None, None

def detect_game_directory(savegame_path):
    """
    Detect if savegame is inside a game directory and return game directory info
    Returns: (is_inside_game, game_dir, relative_path) or (False, None, None)
    """
    if not savegame_path:
        return False, None, None
    
    try:
        norm_path = normalize_path(savegame_path)
        parts = norm_path.split(os.sep)
        
        # Look for game directory from savegame path upwards
        for i in range(len(parts) - 1, 0, -1):
            potential_game_dir = os.sep.join(parts[:i+1])
            
            if os.path.exists(potential_game_dir):
                # Look for executable files in this directory
                try:
                    files = os.listdir(potential_game_dir)
                    for file in files:
                        if file.lower().endswith('.exe'):
                            # Found an executable, this is likely a game directory
                            game_dir = os.sep.join(parts[:i+1])
                            relative_path = os.sep.join(parts[i+1:])
                            return True, game_dir, relative_path
                except (PermissionError, OSError):
                    continue
                
                # Also check for common game files
                game_files = ['game.exe', 'launcher.exe', 'start.exe', 'game.py', 'main.py']
                for file in game_files:
                    if os.path.exists(os.path.join(potential_game_dir, file)):
                        game_dir = os.sep.join(parts[:i+1])
                        relative_path = os.sep.join(parts[i+1:])
                        return True, game_dir, relative_path
                
                # Check for common game directories that indicate this is a game folder
                game_dirs = ['game', 'data', 'assets', 'content', 'saves', 'save']
                for dir_name in game_dirs:
                    if os.path.exists(os.path.join(potential_game_dir, dir_name)):
                        # Additional check: if this directory contains an .exe file, it's likely a game
                        try:
                            sub_files = os.listdir(potential_game_dir)
                            for sub_file in sub_files:
                                if sub_file.lower().endswith('.exe'):
                                    game_dir = os.sep.join(parts[:i+1])
                                    relative_path = os.sep.join(parts[i+1:])
                                    return True, game_dir, relative_path
                        except (PermissionError, OSError):
                            continue
        
        return False, None, None
        
    except Exception:
        return False, None, None

def mask_game_path_in_savegame_location(savegame_path, preference="Auto"):
    """
    Mask game directory path in savegame location for sharing
    Returns masked path that can be used by other users
    
    Args:
        savegame_path: The savegame path to mask
        preference: "Auto", "Game Path", or "Standard"
    """
    if not savegame_path:
        return savegame_path
    
    # First check if this is a Steam path
    is_steam_path, steam_folder, steam_relative_path = detect_steam_folder(savegame_path)
    
    if is_steam_path:
        # This is a Steam path, first mask Steam ID on the full path, then mark with (steam-folder)
        if steam_relative_path:
            # Apply Steam ID masking to the full path first
            masked_full_path = mask_steamid_in_path(savegame_path)
            # Then extract the relative path from the masked full path
            masked_parts = masked_full_path.split(os.sep)
            steam_index = -1
            for i, part in enumerate(masked_parts):
                if part.lower() == 'steam':
                    steam_index = i
                    break
            
            if steam_index >= 0 and steam_index + 1 < len(masked_parts):
                masked_relative_path = os.sep.join(masked_parts[steam_index + 1:])
                return f"(steam-folder)/{normalize_path_for_display(masked_relative_path)}"
            else:
                # Fallback: use original relative path
                return f"(steam-folder)/{normalize_path_for_display(steam_relative_path)}"
        else:
            # Path ends with Steam folder
            return "(steam-folder)"
    
    # If not Steam, check for game directory detection
    is_inside_game, game_dir, relative_path = detect_game_directory(savegame_path)
    
    if preference == "Game Path" or (preference == "Auto" and is_inside_game and relative_path):
        # Return path with consistent placeholder
        return f"(path-to-game)/{normalize_path_for_display(relative_path)}"
    else:
        # Use existing masking for non-game paths or when Standard is selected
        masked_path = mask_steamid_in_path(savegame_path)
        masked_path = mask_username_in_path(masked_path)
        return masked_path

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