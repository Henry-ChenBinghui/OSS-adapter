import boto3
from typing import List, Dict, Optional, BinaryIO
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from ..base import CloudStorage
from ..exceptions import OperationError, FileNotFoundError

class S3Storage(CloudStorage):
    """AWS S3 storage implementation."""
    
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str
    ):
        """Initialize S3 storage.
        
        Args:
            bucket_name: Name of the S3 bucket
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.bucket = self.s3_resource.Bucket(bucket_name)

    def upload_file(self, local_file_path: str, remote_file_path: str) -> None:
        try:
            self.s3_client.upload_file(local_file_path, self.bucket_name, remote_file_path)
        except ClientError as e:
            raise OperationError(f"Failed to upload file to S3: {str(e)}")

    def upload_fileobj(self, file_obj: BinaryIO, remote_file_path: str) -> None:
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, remote_file_path)
        except ClientError as e:
            raise OperationError(f"Failed to upload file object to S3: {str(e)}")

    def download_file(self, remote_file_path: str, local_file_path: str) -> None:
        try:
            self.s3_client.download_file(self.bucket_name, remote_file_path, local_file_path)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found in S3: {remote_file_path}")
            raise OperationError(f"Failed to download file from S3: {str(e)}")

    def download_fileobj(self, remote_file_path: str, file_obj: BinaryIO) -> None:
        try:
            self.s3_client.download_fileobj(self.bucket_name, remote_file_path, file_obj)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found in S3: {remote_file_path}")
            raise OperationError(f"Failed to download file object from S3: {str(e)}")

    def delete_file(self, remote_file_path: str) -> None:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_file_path)
        except ClientError as e:
            raise OperationError(f"Failed to delete file from S3: {str(e)}")

    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix if prefix else ''
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            raise OperationError(f"Failed to list files in S3: {str(e)}")

    def file_exists(self, remote_file_path: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=remote_file_path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise OperationError(f"Failed to check file existence in S3: {str(e)}")

    def get_file_url(self, remote_file_path: str, expires_in: Optional[timedelta] = None) -> str:
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': remote_file_path
            }
            if expires_in:
                params['ExpiresIn'] = int(expires_in.total_seconds())
            return self.s3_client.generate_presigned_url('get_object', Params=params)
        except ClientError as e:
            raise OperationError(f"Failed to generate presigned URL for S3: {str(e)}")

    def get_file_metadata(self, remote_file_path: str) -> Dict:
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=remote_file_path)
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response.get('ContentType'),
                'etag': response['ETag'],
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise FileNotFoundError(f"File not found in S3: {remote_file_path}")
            raise OperationError(f"Failed to get file metadata from S3: {str(e)}") 