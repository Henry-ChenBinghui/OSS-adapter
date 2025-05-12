from abc import ABC, abstractmethod
from typing import List, Dict, Optional, BinaryIO, Union
from datetime import datetime, timedelta

class CloudStorage(ABC):
    """Abstract base class for cloud storage operations."""
    
    @abstractmethod
    def upload_file(self, local_file_path: str, remote_file_path: str) -> None:
        """Upload a file to cloud storage.
        
        Args:
            local_file_path: Path to the local file
            remote_file_path: Path where the file will be stored in cloud
        """
        pass

    @abstractmethod
    def upload_fileobj(self, file_obj: BinaryIO, remote_file_path: str) -> None:
        """Upload a file-like object to cloud storage.
        
        Args:
            file_obj: File-like object to upload
            remote_file_path: Path where the file will be stored in cloud
        """
        pass

    @abstractmethod
    def download_file(self, remote_file_path: str, local_file_path: str) -> None:
        """Download a file from cloud storage.
        
        Args:
            remote_file_path: Path of the file in cloud storage
            local_file_path: Path where the file will be saved locally
        """
        pass

    @abstractmethod
    def download_fileobj(self, remote_file_path: str, file_obj: BinaryIO) -> None:
        """Download a file from cloud storage to a file-like object.
        
        Args:
            remote_file_path: Path of the file in cloud storage
            file_obj: File-like object to write the downloaded data to
        """
        pass

    @abstractmethod
    def delete_file(self, remote_file_path: str) -> None:
        """Delete a file from cloud storage.
        
        Args:
            remote_file_path: Path of the file to delete in cloud storage
        """
        pass

    @abstractmethod
    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """List files in the bucket.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file paths
        """
        pass

    @abstractmethod
    def file_exists(self, remote_file_path: str) -> bool:
        """Check if a file exists in cloud storage.
        
        Args:
            remote_file_path: Path of the file to check
            
        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def get_file_url(self, remote_file_path: str, expires_in: Optional[timedelta] = None) -> str:
        """Get a URL for the file.
        
        Args:
            remote_file_path: Path of the file in cloud storage
            expires_in: Optional time delta for URL expiration
            
        Returns:
            URL string
        """
        pass

    @abstractmethod
    def get_file_metadata(self, remote_file_path: str) -> Dict:
        """Get metadata for a file.
        
        Args:
            remote_file_path: Path of the file in cloud storage
            
        Returns:
            Dictionary containing file metadata
        """
        pass 