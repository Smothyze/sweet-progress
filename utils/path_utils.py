import os
import getpass
from pathlib import Path

def get_current_username():
    """Get current system username"""
    return getpass.getuser()

def normalize_path(path):
    """Normalize path to use system-specific separator"""
    if not path:
        return path
    return str(Path(path))

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
    
    is_inside_game, game_dir, relative_path = detect_game_directory(savegame_path)
    
    if preference == "Game Path" or (preference == "Auto" and is_inside_game and relative_path):
        # Return path with consistent placeholder
        return f"(path-to-game)/{relative_path}"
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