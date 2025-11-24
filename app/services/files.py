from fastapi import HTTPException, Depends, Path, UploadFile
from app.db.models import User, ChatMessages, FileUpload
from app.db.dependencies import db_dependency
from .auth import user_dependency
from ai.main_agent import (generate_reply as ask_llm,
                              predict_demand_v2,
                              generate_report_html, 
                              transcribe_audio)
from app.utils.cloud_storage_config import upload_blob, download_blob
from app.core.config import CLOUD_BUCKET_NAME
from datetime import datetime


async def get_all_files(
    user: user_dependency,
    db: db_dependency
):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    files = db.query(FileUpload).filter(FileUpload.user_id == user_model.id).all()
    
    return [
        {
            "id": file.id,
            "file_url": file.file_path,
            "uploaded_at": file.upload_time
        }
        for file in files
    ]
    
    
async def get_file_by_id(
    user: user_dependency,
    db: db_dependency,
    file_id: str = Path(...)
):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    file_model = db.query(FileUpload).filter(FileUpload.id == file_id,
                                             FileUpload.user_id == user_model.id).first()
    
    if not file_model:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "id": file_model.id,
        "file_url": file_model.file_path,
        "uploaded_at": file_model.upload_time
    }
    
    
