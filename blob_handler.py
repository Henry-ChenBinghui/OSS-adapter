from typing import Optional, BinaryIO, List, Dict
from datetime import timedelta
from cloud_storage.base import CloudStorage

class BlobHandler:
    """A handler class for interacting with cloud storage blobs."""
    
    _instance = None
    
    def __new__(cls):
        """Create or get the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.storage = CloudStorage.create_storage()
        return cls._instance
    
    @classmethod
    def get(cls) -> 'BlobHandler':
        """Get the singleton instance.
        
        Returns:
            The singleton BlobHandler instance
        """
        return cls()
    
    async def upload_file(self, local_file_path: str, remote_file_path: str, container_name: str) -> None:
        """Upload a file to cloud storage.
        
        Args:
            local_file_path: Path to the local file
            remote_file_path: Path where the file should be stored in cloud storage
            container_name: Name of the container/bucket
        """
        async with self.storage:
            await self.storage.upload_file(local_file_path, remote_file_path, container_name)
    
    async def upload_fileobj(self, file_obj: BinaryIO, remote_file_path: str, container_name: str) -> None:
        """Upload a file object to cloud storage.
        
        Args:
            file_obj: File-like object to upload
            remote_file_path: Path where the file should be stored in cloud storage
            container_name: Name of the container/bucket
        """
        async with self.storage:
            await self.storage.upload_fileobj(file_obj, remote_file_path, container_name)
    
    async def download_file(self, remote_file_path: str, local_file_path: str, container_name: str) -> None:
        """Download a file from cloud storage.
        
        Args:
            remote_file_path: Path of the file in cloud storage
            local_file_path: Path where the file should be saved locally
            container_name: Name of the container/bucket
        """
        async with self.storage:
            await self.storage.download_file(remote_file_path, local_file_path, container_name)
    
    async def download_fileobj(self, remote_file_path: str, file_obj: BinaryIO, container_name: str) -> None:
        """Download a file from cloud storage to a file object.
        
        Args:
            remote_file_path: Path of the file in cloud storage
            file_obj: File-like object to write the downloaded data to
            container_name: Name of the container/bucket
        """
        async with self.storage:
            await self.storage.download_fileobj(remote_file_path, file_obj, container_name)
    
    async def delete_file(self, remote_file_path: str, container_name: str) -> None:
        """Delete a file from cloud storage.
        
        Args:
            remote_file_path: Path of the file to delete in cloud storage
            container_name: Name of the container/bucket
        """
        async with self.storage:
            await self.storage.delete_file(remote_file_path, container_name)
    
    async def list_files(self, container_name: str, prefix: Optional[str] = None) -> List[str]:
        """List files in cloud storage.
        
        Args:
            container_name: Name of the container/bucket
            prefix: Optional prefix to filter files by
            
        Returns:
            List of file paths in cloud storage
        """
        async with self.storage:
            return await self.storage.list_files(container_name, prefix)
    
    async def file_exists(self, remote_file_path: str, container_name: str) -> bool:
        """Check if a file exists in cloud storage.
        
        Args:
            remote_file_path: Path of the file to check
            container_name: Name of the container/bucket
            
        Returns:
            True if the file exists, False otherwise
        """
        async with self.storage:
            return await self.storage.file_exists(remote_file_path, container_name)
    
    async def get_file_url(self, remote_file_path: str, container_name: str, expires_in: Optional[timedelta] = None) -> str:
        """Get a URL for accessing a file.
        
        Args:
            remote_file_path: Path of the file in cloud storage
            container_name: Name of the container/bucket
            expires_in: Optional time period after which the URL should expire
            
        Returns:
            URL for accessing the file
        """
        async with self.storage:
            return await self.storage.get_file_url(remote_file_path, container_name, expires_in)
    
    async def get_file_metadata(self, remote_file_path: str, container_name: str) -> Dict:
        """Get metadata for a file in cloud storage.
        
        Args:
            remote_file_path: Path of the file in cloud storage
            container_name: Name of the container/bucket
            
        Returns:
            Dictionary containing file metadata
        """
        async with self.storage:
            return await self.storage.get_file_metadata(remote_file_path, container_name) 