from fastapi import (Depends, 
                     HTTPException, 
                     File, 
                     UploadFile)
from schemas.user import UpdateUserDTO, UpdatePassword, CreateUserDTO
from db.models import User
from db.dependencies import db_dependency
from .auth import user_dependency, pwd_context
from app.utils.cloud_storage_config import uploader, cloudinary
from time import time


async def get_user_details(user: user_dependency,
                           db: db_dependency
                            ):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "email": user_model.email,
        "username": user_model.username,
        "role": user_model.role,
        "is_active": user_model.is_active,
    }
    

async def update_user_details(user_update: UpdateUserDTO,
                              user: user_dependency,
                              db: db_dependency
):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    data_update = user_update.model_dump(exclude_unset=True)
    
    user_model.email = data_update.get("email", user_model.email)
    user_model.username = data_update.get("username", user_model.username)
    user_model.hashed_password = pwd_context.hash(data_update.get("password", user_model.hashed_password))
    user_model.role = data_update.get("role", user_model.role)
    user_model.is_active = data_update.get("is_active", user_model.is_active)
    
    db.commit()
    
    return {
        "username" : user_model.username,
        "email" : user_model.email,
        "role" : user_model.role,
        "is_active" : user_model.is_active,
        #"profile_image" : user_model.profile_image
    }


async def update_user_password(password_update: UpdatePassword,
                               username: str,
                               db: db_dependency
                                ):
    user_model = db.query(User).filter(User.username == username).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not pwd_context.verify(password_update.old_password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    
    user_model.hashed_password = pwd_context.hash(password_update.new_password)
    
    db.commit()
    
    return {
        "message": "Password updated successfully"
        }


async def upload_profile_img(user: user_dependency,
                             db: db_dependency,
                             file: UploadFile = File(...),
                                ):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        upload_result = uploader.upload(file.file,
                                        folder="profile_pictures",
                                        resource_type="image",
                                        public_id=file.filename.split(".")[0]
                                        )
        
        user_model.profile_image = upload_result.get("secure_url")
        db.commit()
        print(upload_result)
        return {
            "detail": "Profile image uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload image") from e
    
    
async def get_profile_img(user: user_dependency,
                          db: db_dependency
                           ):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    image_url = user_model.profile_image
    
    if not image_url:
        raise HTTPException(status_code=404, detail="Profile image not found")
    
    
    return {
        "profile_image_url": image_url,
    }