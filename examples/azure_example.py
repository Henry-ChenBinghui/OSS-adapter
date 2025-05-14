from cloud_storage import CloudStorageFactory, CloudProvider
from datetime import timedelta
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    # 创建 Azure Blob Storage 客户端
    azure_client = CloudStorageFactory.create_storage(
        provider=CloudProvider.AZURE,
        bucket_name="your-container-name",  # 替换为您的容器名称
        account_url=os.getenv("AZURE_STORAGE_ACCOUNT_URL")  # 从环境变量获取账户 URL
    )

    try:
        # 1. 上传文件示例
        print("1. 上传文件...")
        azure_client.upload_file("./test.txt", "test.txt")
        print("   文件上传成功！")

        # 2. 下载文件示例
        print("\n2. 下载文件...")
        azure_client.download_file("test.txt", "./downloaded_test.txt")
        print("   文件下载成功！")

        # 3. 列出容器中的文件
        print("\n3. 列出容器中的文件:")
        files = azure_client.list_files()
        for file in files:
            print(f"   - {file}")

        # 4. 检查文件是否存在
        print("\n4. 检查文件是否存在:")
        exists = azure_client.file_exists("test.txt")
        print(f"   test.txt 存在: {exists}")

        # 5. 获取文件的访问 URL（带1小时过期时间）
        print("\n5. 获取文件的访问 URL:")
        url = azure_client.get_file_url("test.txt", expires_in=timedelta(hours=1))
        print(f"   URL: {url}")

        # 6. 获取文件元数据
        print("\n6. 获取文件元数据:")
        metadata = azure_client.get_file_metadata("test.txt")
        print(f"   大小: {metadata['size']} 字节")
        print(f"   最后修改时间: {metadata['last_modified']}")
        print(f"   Content Type: {metadata['content_type']}")

        # 7. 使用文件对象上传（适用于内存中的数据）
        print("\n7. 使用文件对象上传...")
        with open("./test.txt", "rb") as file_obj:
            azure_client.upload_fileobj(file_obj, "test_fileobj.txt")
        print("   文件对象上传成功！")

        # 8. 使用文件对象下载（适用于直接处理数据）
        print("\n8. 使用文件对象下载...")
        with open("./downloaded_fileobj.txt", "wb") as file_obj:
            azure_client.download_fileobj("test_fileobj.txt", file_obj)
        print("   文件对象下载成功！")

        # 9. 删除文件
        print("\n9. 删除文件...")
        azure_client.delete_file("test.txt")
        azure_client.delete_file("test_fileobj.txt")
        print("   文件删除成功！")

    except Exception as e:
        print(f"\n错误: {str(e)}")

if __name__ == "__main__":
    main() 