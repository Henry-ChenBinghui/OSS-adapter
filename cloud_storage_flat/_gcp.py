from google.cloud import storage
from google.cloud.exceptions import NotFound
from typing import List, Dict, Optional, BinaryIO
from datetime import datetime, timedelta
from ..base import CloudStorage
from ..exceptions import OperationError, FileNotFoundError

class GCSStorage(CloudStorage):
    """Google Cloud Storage implementation."""
    
    def __init__(self, bucket_name: str, credentials_path: str):
        """Initialize Google Cloud Storage.
        
        Args:
            bucket_name: Name of the GCS bucket
            credentials_path: Path to the GCP credentials JSON file
        """
        self.bucket_name = bucket_name
        self.storage_client = storage.Client.from_service_account_json(credentials_path)
        self.bucket = self.storage_client.bucket(bucket_name)

    def upload_file(self, local_file_path: str, remote_file_path: str) -> None:
        try:
            blob = self.bucket.blob(remote_file_path)
            blob.upload_from_filename(local_file_path)
        except Exception as e:
            raise OperationError(f"Failed to upload file to GCS: {str(e)}")

    def upload_fileobj(self, file_obj: BinaryIO, remote_file_path: str) -> None:
        try:
            blob = self.bucket.blob(remote_file_path)
            blob.upload_from_file(file_obj)
        except Exception as e:
            raise OperationError(f"Failed to upload file object to GCS: {str(e)}")

    def download_file(self, remote_file_path: str, local_file_path: str) -> None:
        try:
            blob = self.bucket.blob(remote_file_path)
            blob.download_to_filename(local_file_path)
        except NotFound:
            raise FileNotFoundError(f"File not found in GCS: {remote_file_path}")
        except Exception as e:
            raise OperationError(f"Failed to download file from GCS: {str(e)}")

    def download_fileobj(self, remote_file_path: str, file_obj: BinaryIO) -> None:
        try:
            blob = self.bucket.blob(remote_file_path)
            blob.download_to_file(file_obj)
        except NotFound:
            raise FileNotFoundError(f"File not found in GCS: {remote_file_path}")
        except Exception as e:
            raise OperationError(f"Failed to download file object from GCS: {str(e)}")

    def delete_file(self, remote_file_path: str) -> None:
        try:
            blob = self.bucket.blob(remote_file_path)
            blob.delete()
        except Exception as e:
            raise OperationError(f"Failed to delete file from GCS: {str(e)}")

    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        try:
            blobs = self.bucket.list_blobs(prefix=prefix if prefix else '')
            return [blob.name for blob in blobs]
        except Exception as e:
            raise OperationError(f"Failed to list files in GCS: {str(e)}")

    def file_exists(self, remote_file_path: str) -> bool:
        try:
            blob = self.bucket.blob(remote_file_path)
            return blob.exists()
        except Exception as e:
            raise OperationError(f"Failed to check file existence in GCS: {str(e)}")

    def get_file_url(self, remote_file_path: str, expires_in: Optional[timedelta] = None) -> str:
        try:
            blob = self.bucket.blob(remote_file_path)
            if expires_in:
                return blob.generate_signed_url(
                    version='v4',
                    expiration=datetime.utcnow() + expires_in,
                    method='GET'
                )
            return blob.public_url
        except Exception as e:
            raise OperationError(f"Failed to generate URL for GCS: {str(e)}")

    def get_file_metadata(self, remote_file_path: str) -> Dict:
        try:
            blob = self.bucket.blob(remote_file_path)
            blob.reload()  # Ensure we have the latest metadata
            return {
                'size': blob.size,
                'last_modified': blob.updated,
                'content_type': blob.content_type,
                'etag': blob.etag,
                'metadata': blob.metadata or {}
            }
        except NotFound:
            raise FileNotFoundError(f"File not found in GCS: {remote_file_path}")
        except Exception as e:
            raise OperationError(f"Failed to get file metadata from GCS: {str(e)}") 