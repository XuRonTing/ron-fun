import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from typing import List

from app.api.deps import get_current_user, get_current_active_superuser
from app.models.user import User
from app.services.file_storage import file_storage_service
from app.core.config import settings

router = APIRouter()

@router.post("/upload/image", summary="上传图片")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传图片文件
    
    Args:
        file: 图片文件
        current_user: 当前用户
        
    Returns:
        包含图片URL的响应
    """
    file_url = await file_storage_service.save_image(file)
    return {"url": file_url}

@router.post("/upload/document", summary="上传文档")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    上传文档文件(仅限管理员)
    
    Args:
        file: 文档文件
        current_user: 当前用户(管理员)
        
    Returns:
        包含文档URL的响应
    """
    file_url = await file_storage_service.save_file(file)
    return {"url": file_url}

@router.delete("/{file_path:path}", summary="删除文件")
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_active_superuser)
):
    """
    删除文件(仅限管理员)
    
    Args:
        file_path: 文件路径
        current_user: 当前用户(管理员)
        
    Returns:
        操作结果
    """
    result = await file_storage_service.delete_file(file_path)
    if result:
        return {"success": True, "message": "文件删除成功"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="文件不存在或删除失败"
    )

@router.get("/{file_path:path}", summary="获取文件")
async def get_file(file_path: str):
    """
    获取文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容
    """
    # 只支持从本地存储中获取文件
    if settings.STORAGE_TYPE.lower() != "local":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前存储配置不支持直接获取文件"
        )
    
    full_path = os.path.join(settings.UPLOAD_DIR, file_path)
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    return FileResponse(full_path) 