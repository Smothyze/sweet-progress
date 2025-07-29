class SweetProgressError(Exception):
    """Base exception for Sweet Progress application"""
    pass

class ConfigError(SweetProgressError):
    """Configuration related errors"""
    pass

class BackupError(SweetProgressError):
    """Backup operation errors"""
    pass

class PathError(SweetProgressError):
    """Path validation and processing errors"""
    pass

class ValidationError(SweetProgressError):
    """Input validation errors"""
    pass

class ResourceError(SweetProgressError):
    """Resource loading errors"""
    pass 