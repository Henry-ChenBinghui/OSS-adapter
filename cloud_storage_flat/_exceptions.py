class CloudStorageError(Exception):
    """Base exception for cloud storage operations."""
    pass

class ConfigurationError(CloudStorageError):
    """Raised when there is an error in the configuration."""
    pass

class AuthenticationError(CloudStorageError):
    """Raised when authentication fails."""
    pass

class OperationError(CloudStorageError):
    """Raised when a storage operation fails."""
    pass

class FileNotFoundError(CloudStorageError):
    """Raised when a file is not found in the storage."""
    pass 