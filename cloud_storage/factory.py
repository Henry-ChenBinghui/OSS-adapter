from enum import Enum
from typing import Optional, Dict, Any
from .base import CloudStorage
from .adapters.aws import S3Storage
from .adapters.azure import AzureBlobStorage
from .adapters.gcp import GCSStorage
from .exceptions import ConfigurationError

class CloudProvider(Enum):
    """Supported cloud storage providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class CloudStorageFactory:
    """Factory class for creating cloud storage instances."""
    
    @staticmethod
    def create_storage(
        provider: CloudProvider,
        bucket_name: str,
        **kwargs: Any
    ) -> CloudStorage:
        """Create a cloud storage instance.
        
        Args:
            provider: Cloud provider to use
            bucket_name: Name of the bucket/container
            **kwargs: Additional provider-specific configuration
            
        Returns:
            CloudStorage instance
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        if provider == CloudProvider.AWS:
            required_keys = ['aws_access_key_id', 'aws_secret_access_key', 'region_name']
            if not all(key in kwargs for key in required_keys):
                raise ConfigurationError(
                    f"Missing required AWS configuration. Required keys: {required_keys}"
                )
            return S3Storage(
                bucket_name=bucket_name,
                aws_access_key_id=kwargs['aws_access_key_id'],
                aws_secret_access_key=kwargs['aws_secret_access_key'],
                region_name=kwargs['region_name']
            )
            
        elif provider == CloudProvider.AZURE:
            if 'connection_string' not in kwargs:
                raise ConfigurationError("Missing required Azure connection string")
            return AzureBlobStorage(
                bucket_name=bucket_name,
                connection_string=kwargs['connection_string']
            )
            
        elif provider == CloudProvider.GCP:
            if 'credentials_path' not in kwargs:
                raise ConfigurationError("Missing required GCP credentials path")
            return GCSStorage(
                bucket_name=bucket_name,
                credentials_path=kwargs['credentials_path']
            )
            
        else:
            raise ConfigurationError(f"Unsupported cloud provider: {provider}") 