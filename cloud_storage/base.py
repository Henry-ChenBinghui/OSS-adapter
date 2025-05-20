from abc import ABC, abstractmethod
from typing import List, Dict, Optional, BinaryIO, Union
from datetime import datetime, timedelta
import os

class CloudStorage(ABC):
    """Base class for cloud storage implementations."""
    
    @classmethod
    def create_storage(cls, bucket_name: str, **kwargs) -> 'CloudStorage':
        """Factory method to create appropriate storage client based on environment.
        
        Args:
            bucket_name: Name of the bucket/container
            **kwargs: Additional arguments for specific storage implementations
            
        Returns:
            An instance of appropriate CloudStorage implementation
            
        Raises:
            ConfigurationError: If storage type is not configured or invalid
        """
        storage_type = os.getenv('CLOUD_STORAGE_TYPE', 'azure').lower()
        
        if storage_type == 'azure':
            from .adapters.azure import AzureBlobStorage
            return AzureBlobStorage(bucket_name=bucket_name, **kwargs)
        elif storage_type == 's3':
            from .adapters.s3 import S3Storage
            return S3Storage(bucket_name=bucket_name, **kwargs)
        else:
            raise ConfigurationError(f"Unsupported storage type: {storage_type}")

    @abstractmethod
    async def upload_file(self, local_file_path: str, remote_file_path: str) -> None:
        """Upload a file from local path to remote storage."""
        pass

    @abstractmethod
    async def upload_fileobj(self, file_obj: BinaryIO, remote_file_path: str) -> None:
        """Upload a file object to remote storage."""
        pass

    @abstractmethod
    async def download_file(self, remote_file_path: str, local_file_path: str) -> None:
        """Download a file from remote storage to local path."""
        pass

    @abstractmethod
    async def download_fileobj(self, remote_file_path: str, file_obj: BinaryIO) -> None:
        """Download a file from remote storage to a file object."""
        pass

    @abstractmethod
    async def delete_file(self, remote_file_path: str) -> None:
        """Delete a file from remote storage."""
        pass

    @abstractmethod
    async def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """List files in remote storage with optional prefix."""
        pass

    @abstractmethod
    async def file_exists(self, remote_file_path: str) -> bool:
        """Check if a file exists in remote storage."""
        pass

    @abstractmethod
    async def get_file_url(self, remote_file_path: str, expires_in: Optional[timedelta] = None) -> str:
        """Get a URL for accessing a file, optionally with expiration."""
        pass

    @abstractmethod
    async def get_file_metadata(self, remote_file_path: str) -> Dict:
        """Get metadata for a file in remote storage."""
        pass

class ConfigurationError(Exception):
    """Raised when there is a configuration error."""
    pass

class OperationError(Exception):
    """Raised when an operation fails."""
    pass

class FileNotFoundError(Exception):
    """Raised when a file is not found."""
    pass 