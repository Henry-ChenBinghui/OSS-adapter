from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential
from typing import List, Dict, Optional, BinaryIO
from datetime import datetime, timedelta
import os
from ..base import CloudStorage
from ..exceptions import OperationError, FileNotFoundError, ConfigurationError
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

class AzureBlobStorage(CloudStorage):
    """Azure Blob Storage implementation."""
    
    def __init__(self, bucket_name: str, account_url: str = None):
        """Initialize Azure Blob Storage.
        
        Args:
            bucket_name: Name of the container
            account_url: Azure Storage account URL (e.g., https://<account>.blob.core.windows.net)
                        If not provided, will try to get from AZURE_STORAGE_ACCOUNT_URL environment variable
        """
        self.container_name = bucket_name
        self.credential = DefaultAzureCredential()
        
        if not account_url:
            account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL')
            if not account_url:
                raise ConfigurationError("Missing Azure Storage account URL. Please provide it or set AZURE_STORAGE_ACCOUNT_URL environment variable")
        
        self.account_url = account_url
        self._blob_service_client = None
        self._container_client = None

    async def __aenter__(self):
        """Initialize clients when entering async context."""
        self._blob_service_client = BlobServiceClient(self.account_url, credential=self.credential)
        self._container_client = self._blob_service_client.get_container_client(self.container_name)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close clients when exiting async context."""
        if self._blob_service_client:
            await self._blob_service_client.close()
        if self._container_client:
            await self._container_client.close()

    async def upload_file(self, local_file_path: str, remote_file_path: str) -> None:
        try:
            blob_client = self._container_client.get_blob_client(remote_file_path)
            async with blob_client:
                with open(local_file_path, 'rb') as file:
                    await blob_client.upload_blob(file, overwrite=True)
        except Exception as e:
            raise OperationError(f"Failed to upload file to Azure Blob Storage: {str(e)}")

    async def upload_fileobj(self, file_obj: BinaryIO, remote_file_path: str) -> None:
        try:
            blob_client = self._container_client.get_blob_client(remote_file_path)
            async with blob_client:
                await blob_client.upload_blob(file_obj, overwrite=True)
        except Exception as e:
            raise OperationError(f"Failed to upload file object to Azure Blob Storage: {str(e)}")

    async def download_file(self, remote_file_path: str, local_file_path: str) -> None:
        try:
            blob_client = self._container_client.get_blob_client(remote_file_path)
            async with blob_client:
                download_stream = await blob_client.download_blob()
                with open(local_file_path, 'wb') as file:
                    await download_stream.readinto(file)
        except Exception as e:
            if 'BlobNotFound' in str(e):
                raise FileNotFoundError(f"File not found in Azure Blob Storage: {remote_file_path}")
            raise OperationError(f"Failed to download file from Azure Blob Storage: {str(e)}")

    async def download_fileobj(self, remote_file_path: str, file_obj: BinaryIO) -> None:
        try:
            blob_client = self._container_client.get_blob_client(remote_file_path)
            async with blob_client:
                download_stream = await blob_client.download_blob()
                await download_stream.readinto(file_obj)
        except Exception as e:
            if 'BlobNotFound' in str(e):
                raise FileNotFoundError(f"File not found in Azure Blob Storage: {remote_file_path}")
            raise OperationError(f"Failed to download file object from Azure Blob Storage: {str(e)}")

    async def delete_file(self, remote_file_path: str) -> None:
        try:
            blob_client = self._container_client.get_blob_client(remote_file_path)
            async with blob_client:
                await blob_client.delete_blob()
        except Exception as e:
            raise OperationError(f"Failed to delete file from Azure Blob Storage: {str(e)}")

    async def list_files(self, prefix: Optional[str] = None) -> List[str]:
        try:
            blobs = []
            async for blob in self._container_client.list_blobs(name_starts_with=prefix if prefix else ''):
                blobs.append(blob.name)
            return blobs
        except Exception as e:
            raise OperationError(f"Failed to list files in Azure Blob Storage: {str(e)}")

    async def file_exists(self, remote_file_path: str) -> bool:
        try:
            blob_client = self._container_client.get_blob_client(remote_file_path)
            async with blob_client:
                await blob_client.get_blob_properties()
                return True
        except Exception as e:
            if 'BlobNotFound' in str(e):
                return False
            raise OperationError(f"Failed to check file existence in Azure Blob Storage: {str(e)}")

    async def get_file_url(self, remote_file_path: str, expires_in: Optional[timedelta] = None) -> str:
        try:
            blob_client = self._container_client.get_blob_client(remote_file_path)
            async with blob_client:
                if expires_in:
                    # Get user delegation key
                    delegation_key = await self._blob_service_client.get_user_delegation_key(
                        key_start_time=datetime.utcnow(),
                        key_expiry_time=datetime.utcnow() + expires_in
                    )
                    # Generate SAS token using user delegation key
                    sas_token = generate_blob_sas(
                        account_name=self._blob_service_client.account_name,
                        container_name=self.container_name,
                        blob_name=remote_file_path,
                        user_delegation_key=delegation_key,
                        permission=BlobSasPermissions(read=True),
                        start=delegation_key.signed_start,
                        expiry=delegation_key.signed_expiry
                    )
                    return f"{blob_client.url}?{sas_token}"
                return blob_client.url
        except Exception as e:
            raise OperationError(f"Failed to generate URL for Azure Blob Storage: {str(e)}")

    async def get_file_metadata(self, remote_file_path: str) -> Dict:
        try:
            blob_client = self._container_client.get_blob_client(remote_file_path)
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