import os
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO, Union, Tuple
from pathlib import Path
from datetime import datetime
import aiofiles
from fastapi import UploadFile, HTTPException, status
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageBackend(ABC):
    """
    存储后端抽象基类
    """
    @abstractmethod
    async def save_file(self, file: UploadFile, folder: str = None) -> str:
        """
        保存文件
        
        Args:
            file: 上传的文件
            folder: 文件夹路径
            
        Returns:
            文件URL或路径
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def get_file_url(self, file_path: str) -> str:
        """
        获取文件URL
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件URL
        """
        pass
    
class LocalStorageBackend(StorageBackend):
    """
    本地文件存储后端
    """
    def __init__(self):
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    async def save_file(self, file: UploadFile, folder: str = None) -> str:
        """
        保存文件到本地
        
        Args:
            file: 上传的文件
            folder: 子文件夹(可选)
            
        Returns:
            文件相对路径
        """
        # 创建基于日期的子文件夹
        date_folder = datetime.now().strftime("%Y%m%d")
        target_folder = os.path.join(settings.UPLOAD_DIR, date_folder)
        if folder:
            target_folder = os.path.join(target_folder, folder)
        
        # 确保目标文件夹存在
        os.makedirs(target_folder, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(target_folder, unique_filename)
        
        # 保存文件
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                # 读取上传的文件内容并写入
                content = await file.read()
                await out_file.write(content)
            
            # 返回相对于上传目录的路径
            rel_path = os.path.join(date_folder, folder or "", unique_filename)
            return rel_path.replace("\\", "/")  # 确保路径分隔符一致
            
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="文件保存失败"
            )
    
    async def delete_file(self, file_path: str) -> bool:
        """
        从本地删除文件
        
        Args:
            file_path: 文件相对路径
            
        Returns:
            是否删除成功
        """
        full_path = os.path.join(settings.UPLOAD_DIR, file_path)
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        获取文件URL
        
        Args:
            file_path: 文件相对路径
            
        Returns:
            文件URL
        """
        # 在实际环境中，这应该返回完整的URL，包括域名
        # 这里简单返回API路径
        if file_path:
            return f"/api/v1/files/{file_path}"
        return ""

class S3StorageBackend(StorageBackend):
    """
    S3兼容的对象存储后端
    """
    def __init__(self):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        except ImportError:
            logger.error("boto3 模块未安装，无法使用S3存储")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="存储服务配置错误"
            )
        except Exception as e:
            logger.error(f"初始化S3客户端失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="存储服务配置错误"
            )
    
    async def save_file(self, file: UploadFile, folder: str = None) -> str:
        """
        保存文件到S3
        
        Args:
            file: 上传的文件
            folder: 子文件夹(可选)
            
        Returns:
            文件路径
        """
        # 创建基于日期的对象键
        date_folder = datetime.now().strftime("%Y%m%d")
        object_key = date_folder
        if folder:
            object_key = f"{object_key}/{folder}"
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        object_key = f"{object_key}/{unique_filename}"
        
        # 上传文件到S3
        try:
            content = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content,
                ContentType=file.content_type
            )
            return object_key
        except Exception as e:
            logger.error(f"上传文件到S3失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="文件上传失败"
            )
    
    async def delete_file(self, file_path: str) -> bool:
        """
        从S3删除文件
        
        Args:
            file_path: 文件路径(对象键)
            
        Returns:
            是否删除成功
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
        except Exception as e:
            logger.error(f"从S3删除文件失败: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        获取S3文件URL
        
        Args:
            file_path: 文件路径(对象键)
            
        Returns:
            文件URL
        """
        if not file_path:
            return ""
        
        try:
            # 生成预签名URL
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=3600  # URL有效期1小时
            )
            return url
        except Exception as e:
            logger.error(f"生成S3预签名URL失败: {str(e)}")
            # 返回常规URL
            return f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{file_path}"

class FileStorageService:
    """
    文件存储服务，提供统一的文件操作接口
    """
    def __init__(self):
        # 根据配置选择存储后端
        if settings.STORAGE_TYPE.lower() == "s3":
            self.backend = S3StorageBackend()
        else:
            self.backend = LocalStorageBackend()
    
    async def save_image(self, file: UploadFile) -> str:
        """
        保存图片文件
        
        Args:
            file: 上传的图片文件
            
        Returns:
            图片URL
        """
        # 验证文件类型
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的图片类型"
            )
        
        # 保存图片
        file_path = await self.backend.save_file(file, folder="images")
        return self.backend.get_file_url(file_path)
    
    async def save_file(self, file: UploadFile) -> str:
        """
        保存普通文件
        
        Args:
            file: 上传的文件
            
        Returns:
            文件URL
        """
        # 验证文件类型
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型"
            )
        
        # 保存文件
        file_path = await self.backend.save_file(file, folder="documents")
        return self.backend.get_file_url(file_path)
    
    async def delete_file(self, file_url: str) -> bool:
        """
        删除文件
        
        Args:
            file_url: 文件URL或路径
            
        Returns:
            是否删除成功
        """
        # 从URL中提取文件路径
        if "/api/v1/files/" in file_url:
            file_path = file_url.split("/api/v1/files/")[1]
        else:
            file_path = file_url
        
        return await self.backend.delete_file(file_path)


# 创建文件存储服务实例
file_storage_service = FileStorageService() 