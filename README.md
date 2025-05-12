# Cloud Storage Adapter

这是一个云存储服务的抽象层实现，支持以下云平台：

- Amazon S3
- Azure Blob Storage
- Google Cloud Storage (GCS)

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```python
from cloud_storage import CloudStorageFactory, CloudProvider

# 创建 S3 客户端
s3_client = CloudStorageFactory.create_storage(
    provider=CloudProvider.AWS,
    bucket_name="your-bucket",
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key",
    region_name="your-region"
)

# 上传文件
s3_client.upload_file("local_file.txt", "remote_file.txt")

# 下载文件
s3_client.download_file("remote_file.txt", "downloaded_file.txt")

# 列出文件
files = s3_client.list_files()
```

## 环境变量配置

你可以通过环境变量来配置认证信息，创建 `.env` 文件：

```env
# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=your-region

# Azure
AZURE_STORAGE_CONNECTION_STRING=your-connection-string

# GCP
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
```

## 支持的操作

所有云存储适配器都支持以下操作：

- 上传文件
- 下载文件
- 删除文件
- 列出文件
- 检查文件是否存在
- 获取文件 URL
- 获取文件元数据
