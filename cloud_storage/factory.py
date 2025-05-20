import os
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
    def create_storage(bucket_name: str) -> CloudStorage:
        """Create a cloud storage instance based on environment configuration.
        
        Args:
            bucket_name: Name of the bucket/container
            
        Returns:
            CloudStorage: An instance of the configured cloud storage
            
        Raises:
            ConfigurationError: If no valid cloud storage configuration is found
        """
        # Check for Azure configuration
        if os.getenv('AZURE_STORAGE_ACCOUNT_URL'):
            return AzureBlobStorage(
                bucket_name=bucket_name,
                account_url=os.getenv('AZURE_STORAGE_ACCOUNT_URL')
            )
            
        # Check for AWS configuration
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            return S3Storage(
                bucket_name=bucket_name,
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
        # Check for GCS configuration
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            return GCSStorage(
                bucket_name=bucket_name
            )
            
        raise ConfigurationError(
            "No valid cloud storage configuration found. "
            "Please set environment variables for one of the following:\n"
            "- Azure: AZURE_STORAGE_ACCOUNT_URL\n"
            "- AWS: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY\n"
            "- GCS: GOOGLE_APPLICATION_CREDENTIALS"
        )

    @staticmethod
    def create_storage_with_kwargs(
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
            if 'account_url' not in kwargs:
                raise ConfigurationError("Missing required Azure account URL")
            return AzureBlobStorage(
                bucket_name=bucket_name,
                account_url=kwargs['account_url']
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