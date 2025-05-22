__all__ = ['S3Storage', 'AzureBlobStorage', 'GCSStorage']

def __getattr__(name):
    if name == 'S3Storage':
        from .aws import S3Storage
        return S3Storage
    elif name == 'AzureBlobStorage':
        from .azure import AzureBlobStorage
        return AzureBlobStorage
    elif name == 'GCSStorage':
        from .gcp import GCSStorage
        return GCSStorage
    raise AttributeError(f"module 'cloud_storage.adapters' has no attribute '{name}'") 