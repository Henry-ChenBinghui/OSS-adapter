from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from azure.identity import DefaultAzureCredential
from typing import List, Dict, Optional, BinaryIO
from datetime import datetime, timedelta, timezone
import os
from ..base import CloudStorage
from ..exceptions import OperationError, FileNotFoundError, ConfigurationError
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

class AzureBlobStorage(CloudStorage):
    """Azure Blob Storage implementation."""
    
    def __init__(self, account_url: str = None):
        """Initialize Azure Blob Storage.
        
        Args:
            account_url: Azure Storage account URL (e.g., https://<account>.blob.core.windows.net)
                        If not provided, will try to get from AZURE_STORAGE_ACCOUNT_URL environment variable
        """
        self.credential = DefaultAzureCredential()
        
        if not account_url:
            account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL')
            if not account_url:
                raise ConfigurationError("Missing Azure Storage account URL. Please provide it or set AZURE_STORAGE_ACCOUNT_URL environment variable")
        
        self.account_url = account_url
        self._blob_service_client = None
        self._container_clients = {}
        self._delegation_key = None
        self._delegation_key_expiry = None

    async def __aenter__(self):
        """Initialize service client when entering async context."""
        self._blob_service_client = BlobServiceClient(self.account_url, credential=self.credential)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close clients when exiting async context."""
        if self._blob_service_client:
            await self._blob_service_client.close()
        for container_client in self._container_clients.values():
            await container_client.close()
        self._container_clients.clear()
        self._delegation_key = None
        self._delegation_key_expiry = None

    async def _get_user_delegation_key(self, expires_in: timedelta) -> tuple:
        """Get or create user delegation key with caching.
        
        Args:
            expires_in: How long the key should be valid for
            
        Returns:
            Tuple of (delegation_key, expiry_time)
        """
        now = datetime.now(timezone.utc)
        expiry_time = now + expires_in
        
        # Return cached key if it's still valid
        if (self._delegation_key and self._delegation_key_expiry and 
            self._delegation_key_expiry > now + timedelta(minutes=5)):  # 5 min buffer
            return self._delegation_key, self._delegation_key_expiry
            
        # Get new key
        delegation_key = await self._blob_service_client.get_user_delegation_key(
            key_start_time=now,
            key_expiry_time=expiry_time
        )
        
        # Cache the key
        self._delegation_key = delegation_key
        self._delegation_key_expiry = expiry_time
        
        return delegation_key, expiry_time

    async def _get_container_client(self, container_name: str) -> ContainerClient:
        """Get or create container client.
        
        Args:
            container_name: Name of the container
            
        Returns:
            ContainerClient instance
        """
        if container_name not in self._container_clients:
            self._container_clients[container_name] = self._blob_service_client.get_container_client(container_name)
        return self._container_clients[container_name]

    async def upload_file(self, local_file_path: str, remote_file_path: str, container_name: str) -> None:
        try:
            container_client = await self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(remote_file_path)
            async with blob_client:
                with open(local_file_path, 'rb') as file:
                    await blob_client.upload_blob(file, overwrite=True)
        except Exception as e:
            raise OperationError(f"Failed to upload file to Azure Blob Storage: {str(e)}")

    async def upload_fileobj(self, file_obj: BinaryIO, remote_file_path: str, container_name: str) -> None:
        try:
            container_client = await self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(remote_file_path)
            async with blob_client:
                await blob_client.upload_blob(file_obj, overwrite=True)
        except Exception as e:
            raise OperationError(f"Failed to upload file object to Azure Blob Storage: {str(e)}")

    async def download_file(self, remote_file_path: str, local_file_path: str, container_name: str) -> None:
        try:
            container_client = await self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(remote_file_path)
            async with blob_client:
                download_stream = await blob_client.download_blob()
                with open(local_file_path, 'wb') as file:
                    await download_stream.readinto(file)
        except Exception as e:
            if 'BlobNotFound' in str(e):
                raise FileNotFoundError(f"File not found in Azure Blob Storage: {remote_file_path}")
            raise OperationError(f"Failed to download file from Azure Blob Storage: {str(e)}")

    async def download_fileobj(self, remote_file_path: str, file_obj: BinaryIO, container_name: str) -> None:
        try:
            container_client = await self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(remote_file_path)
            async with blob_client:
                download_stream = await blob_client.download_blob()
                await download_stream.readinto(file_obj)
        except Exception as e:
            if 'BlobNotFound' in str(e):
                raise FileNotFoundError(f"File not found in Azure Blob Storage: {remote_file_path}")
            raise OperationError(f"Failed to download file object from Azure Blob Storage: {str(e)}")

    async def delete_file(self, remote_file_path: str, container_name: str) -> None:
        try:
            container_client = await self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(remote_file_path)
            async with blob_client:
                await blob_client.delete_blob()
        except Exception as e:
            raise OperationError(f"Failed to delete file from Azure Blob Storage: {str(e)}")

    async def list_files(self, container_name: str, prefix: Optional[str] = None) -> List[str]:
        try:
            container_client = await self._get_container_client(container_name)
            blobs = []
            async for blob in container_client.list_blobs(name_starts_with=prefix if prefix else ''):
                blobs.append(blob.name)
            return blobs
        except Exception as e:
            raise OperationError(f"Failed to list files in Azure Blob Storage: {str(e)}")

    async def file_exists(self, remote_file_path: str, container_name: str) -> bool:
        try:
            container_client = await self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(remote_file_path)
            async with blob_client:
                await blob_client.get_blob_properties()
                return True
        except Exception as e:
            if 'BlobNotFound' in str(e):
                return False
            raise OperationError(f"Failed to check file existence in Azure Blob Storage: {str(e)}")

    async def get_file_url(self, remote_file_path: str, container_name: str, expires_in: Optional[timedelta] = None) -> str:
        try:
            container_client = await self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(remote_file_path)
            async with blob_client:
                if expires_in:
                    # Get user delegation key
                    delegation_key, expiry_time = await self._get_user_delegation_key(expires_in)
                    # Generate SAS token using user delegation key
                    sas_token = generate_blob_sas(
                        account_name=self._blob_service_client.account_name,
                        container_name=container_name,
                        blob_name=remote_file_path,
                        user_delegation_key=delegation_key,
                        permission=BlobSasPermissions(read=True),
                        start=delegation_key.signed_start,
                        expiry=expiry_time
                    )
                    return f"{blob_client.url}?{sas_token}"
                return blob_client.url
        except Exception as e:
            raise OperationError(f"Failed to generate URL for Azure Blob Storage: {str(e)}")

    async def get_file_metadata(self, remote_file_path: str, container_name: str) -> Dict:
        try:
            container_client = await self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(remote_file_path)
            async with blob_client:
                properties = await blob_client.get_blob_properties()
                return {
                    'size': properties.size,
                    'last_modified': properties.last_modified,
                    'content_type': properties.content_settings.content_type,
                    'etag': properties.etag,
                    'metadata': properties.metadata
                }
        except Exception as e:
            if 'BlobNotFound' in str(e):
                raise FileNotFoundError(f"File not found in Azure Blob Storage: {remote_file_path}")
            raise OperationError(f"Failed to get file metadata from Azure Blob Storage: {str(e)}") 