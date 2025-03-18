import os
import io
import uuid
import aiofiles
from typing import BinaryIO, Optional
import boto3
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class StorageService(ABC):
    """Abstract base class for storage services."""
    
    @abstractmethod
    async def save_file(self, file_data: bytes, file_id: str, content_type: str) -> str:
        """Save a file to storage and return the path or URL."""
        pass
    
    @abstractmethod
    async def get_file(self, file_id: str) -> Optional[bytes]:
        """Get a file's contents from storage."""
        pass
    
    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from storage."""
        pass
    
    @abstractmethod
    def get_file_path(self, file_id: str) -> str:
        """Get the physical path to a file in storage."""
        pass
    
    @staticmethod
    def get_storage_service() -> 'StorageService':
        """Factory method to get the appropriate storage service."""
        storage_type = os.getenv("STORAGE_TYPE", "local").lower()
        
        if storage_type == "s3":
            return S3StorageService()
        else:
            return LocalStorageService()


class LocalStorageService(StorageService):
    """Storage service for local filesystem."""
    
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_file(self, file_data: bytes, file_id: str, content_type: str) -> str:
        """Save a file to local storage."""
        file_path = os.path.join(self.upload_dir, file_id)
        
        try:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_data)
            logger.info(f"File {file_id} saved to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving file {file_id}: {str(e)}")
            raise
    
    async def get_file(self, file_id: str) -> Optional[bytes]:
        """Get a file's contents from local storage."""
        file_path = os.path.join(self.upload_dir, file_id)
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File {file_id} not found at {file_path}")
                return None
            
            async with aiofiles.open(file_path, "rb") as f:
                data = await f.read()
            return data
        except Exception as e:
            logger.error(f"Error reading file {file_id}: {str(e)}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from local storage."""
        file_path = os.path.join(self.upload_dir, file_id)
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File {file_id} not found at {file_path}")
                return False
            
            os.remove(file_path)
            logger.info(f"File {file_id} deleted from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            return False
    
    def get_file_path(self, file_id: str) -> str:
        """Get the physical path to a file in local storage."""
        return os.path.join(self.upload_dir, file_id)


class S3StorageService(StorageService):
    """Storage service for AWS S3."""
    
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is not set")
        
        self.region = os.getenv("S3_REGION", "us-west-2")
        
        self.s3_client = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    async def save_file(self, file_data: bytes, file_id: str, content_type: str) -> str:
        """Save a file to S3 storage."""
        try:
            file_obj = io.BytesIO(file_data)
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_id,
                ExtraArgs={
                    "ContentType": content_type,
                }
            )
            s3_url = f"s3://{self.bucket_name}/{file_id}"
            logger.info(f"File {file_id} uploaded to S3: {s3_url}")
            return s3_url
        except Exception as e:
            logger.error(f"Error uploading file {file_id} to S3: {str(e)}")
            raise
    
    async def get_file(self, file_id: str) -> Optional[bytes]:
        """Get a file's contents from S3 storage."""
        try:
            file_obj = io.BytesIO()
            self.s3_client.download_fileobj(
                self.bucket_name,
                file_id,
                file_obj
            )
            file_obj.seek(0)
            data = file_obj.read()
            return data
        except Exception as e:
            logger.error(f"Error downloading file {file_id} from S3: {str(e)}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from S3 storage."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_id
            )
            logger.info(f"File {file_id} deleted from S3 bucket {self.bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_id} from S3: {str(e)}")
            return False
    
    def get_file_path(self, file_id: str) -> str:
        """
        Get the path to a file in S3 storage.
        
        Note: For S3, there's no direct file path. This returns a URL that can
        be used for accessing the file, but it's not a local path.
        """
        # For S3, we don't have a physical path, so return an S3 URL
        return f"s3://{self.bucket_name}/{file_id}"