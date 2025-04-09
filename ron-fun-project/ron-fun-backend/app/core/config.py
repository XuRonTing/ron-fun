from typing import List, Union, Optional, Any
from pydantic import AnyHttpUrl, validator, DirectoryPath
from pydantic_settings import BaseSettings
import os
from urllib.parse import quote_plus

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ron.fun API"
    PROJECT_DESCRIPTION: str = "Ron.fun项目后端API服务"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS设置
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 数据库设置
    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    MYSQL_PORT: Optional[str] = "3306"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Any:
        if isinstance(v, str):
            return v
            
        # 为演示目的使用SQLite
        if values.get("MYSQL_SERVER") == "sqlite":
            return f"sqlite:///{values.get('MYSQL_DB')}"
            
        # MySQL连接
        username = quote_plus(values.get("MYSQL_USER", ""))
        password = quote_plus(values.get("MYSQL_PASSWORD", ""))
        host = values.get("MYSQL_SERVER", "")
        port = values.get("MYSQL_PORT", "3306")
        db = values.get("MYSQL_DB", "")
        
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{db}"

    # 安全设置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 日志设置
    LOG_LEVEL: str = "INFO"
    
    # 文件上传设置
    UPLOAD_DIR: DirectoryPath = os.path.join(os.getcwd(), "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB 
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf", "text/plain", "application/msword", 
                                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    # 文件存储类型: 本地存储或对象存储
    STORAGE_TYPE: str = "local"  # "local" 或 "s3"
    
    # S3兼容的对象存储设置 (如果STORAGE_TYPE=s3)
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()