class SweetProgressError(Exception):
    """Base exception for Sweet Progress application"""
    pass

class ConfigError(SweetProgressError):
    """Configuration related errors"""
    pass

class BackupError(SweetProgressError):
    """Backup operation errors"""
    pass
