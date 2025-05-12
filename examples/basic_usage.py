from cloud_storage import CloudStorageFactory, CloudProvider
from datetime import timedelta
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    # AWS S3 示例
    s3_client = CloudStorageFactory.create_storage(
        provider=CloudProvider.AWS,
        bucket_name="your-s3-bucket",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    # Azure Blob Storage 示例
    azure_client = CloudStorageFactory.create_storage(
        provider=CloudProvider.AZURE,
        bucket_name="your-azure-container",
        connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    )

    # Google Cloud Storage 示例
    gcs_client = CloudStorageFactory.create_storage(
        provider=CloudProvider.GCP,
        bucket_name="your-gcs-bucket",
        credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )

    # 使用示例 - 以 S3 为例
    try:
        # 上传文件
        s3_client.upload_file("local_file.txt", "remote_file.txt")

        # 下载文件
        s3_client.download_file("remote_file.txt", "downloaded_file.txt")

        # 列出文件
        files = s3_client.list_files(prefix="remote_")
        print("Files in bucket:", files)

        # 检查文件是否存在
        exists = s3_client.file_exists("remote_file.txt")
        print("File exists:", exists)

        # 获取文件URL（带过期时间）
        url = s3_client.get_file_url(
            "remote_file.txt",
            expires_in=timedelta(hours=1)
        )
        print("File URL:", url)

        # 获取文件元数据
        metadata = s3_client.get_file_metadata("remote_file.txt")
        print("File metadata:", metadata)

        # 删除文件
        s3_client.delete_file("remote_file.txt")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 