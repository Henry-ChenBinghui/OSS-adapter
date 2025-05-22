from ._storage_base import CloudStorage

def __getattr__(name):
    if name == 'S3Storage':
        from ._aws import S3Storage
        return S3Storage
    elif name == 'AzureBlobStorage':
        from ._azure import AzureBlobStorage
        return AzureBlobStorage
    elif name == 'GCSStorage':
        from ._gcp import GCSStorage
        return GCSStorage
    raise AttributeError(f"module 'cloud_storage_flat' has no attribute '{name}'")

__all__ = ['CloudStorage', 'S3Storage', 'AzureBlobStorage', 'GCSStorage'] 