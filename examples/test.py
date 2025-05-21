from cloud_storage import CloudStorageFactory, CloudProvider
from datetime import timedelta
import os
import logging
import asyncio
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def setup_azure_client():
    """
    Create and configure Azure Blob Storage client.
    
    Returns:
        Azure storage client
    """
    try:
        client = CloudStorageFactory.create_storage(
            provider=CloudProvider.AZURE,
            bucket_name=os.getenv("AZURE_CONTAINER_NAME", "your-container-name"),
            account_url=os.getenv("AZURE_STORAGE_ACCOUNT_URL")
        )
        return client
    except Exception as e:
        logger.error(f"Failed to create Azure client: {str(e)}")
        raise

async def cleanup_files(client, files):
    """
    Clean up files from Azure storage.
    
    Args:
        client: Azure storage client
        files: List of file names to delete
    """
    for file in files:
        try:
            await client.delete_file(file)
            logger.info(f"Successfully deleted file: {file}")
        except Exception as e:
            logger.error(f"Failed to delete file {file}: {str(e)}")

async def main():
    """
    Main function demonstrating Azure Blob Storage operations.
    """
    files_to_cleanup = []
    
    async with await setup_azure_client() as azure_client:
        try:
            # 1. Upload file example
            logger.info("1. Uploading file...")
            await azure_client.upload_file("./test.txt", "test.txt")
            files_to_cleanup.append("test.txt")
            logger.info("File uploaded successfully!")

            # 2. Download file example
            logger.info("\n2. Downloading file...")
            await azure_client.download_file("test.txt", "./downloaded_test.txt")
            logger.info("File downloaded successfully!")

            # 3. List files in container
            logger.info("\n3. Listing files in container:")
            files = await azure_client.list_files()
            for file in files:
                logger.info(f"   - {file}")

            # 4. Check if file exists
            logger.info("\n4. Checking if file exists:")
            exists = await azure_client.file_exists("test.txt")
            logger.info(f"   test.txt exists: {exists}")

            # 5. Get file access URL (with 1-hour expiration)
            logger.info("\n5. Getting file access URL:")
            url = await azure_client.get_file_url("test.txt", expires_in=timedelta(hours=1))
            logger.info(f"   URL: {url}")

            # 6. Get file metadata
            logger.info("\n6. Getting file metadata:")
            metadata = await azure_client.get_file_metadata("test.txt")
            logger.info(f"   Size: {metadata['size']} bytes")
            logger.info(f"   Last modified: {metadata['last_modified']}")
            logger.info(f"   Content Type: {metadata['content_type']}")

            # 7. Upload using file object (for in-memory data)
            logger.info("\n7. Uploading using file object...")
            with open("./test.txt", "rb") as file_obj:
                await azure_client.upload_fileobj(file_obj, "test_fileobj.txt")
            files_to_cleanup.append("test_fileobj.txt")
            logger.info("File object uploaded successfully!")

            # 8. Download using file object (for direct data processing)
            logger.info("\n8. Downloading using file object...")
            with open("./downloaded_fileobj.txt", "wb") as file_obj:
                await azure_client.download_fileobj("test_fileobj.txt", file_obj)
            logger.info("File object downloaded successfully!")

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise
        finally:
            # Clean up uploaded files
            if files_to_cleanup:
                logger.info("\n9. Cleaning up files...")
                await cleanup_files(azure_client, files_to_cleanup)

if __name__ == "__main__":
    asyncio.run(main()) 