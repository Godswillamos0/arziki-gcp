from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class CreateUserDTO(BaseModel):
    email: EmailStr
    password: str
    username: str
    role: Optional[str] = "user"
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "name@mail.com",
                "password": "strongpassword123",
                "username": "username123",
                "role": "user",
            }
        }
    }
    
    
class UpdateUserDTO(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    username: Optional[str]
    role: Optional[str]
    is_active: Optional[bool]
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "name@email.com",
                "password": "newstrongpassword123",
                "username": "newusername123",
                "role": "admin",
                "is_active": True,
            }
        }
    }
    
class UpdatePassword(BaseModel):
    old_password: str
    new_password: str
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newstrongpassword123",
            }
        }
    }
    
    
class ForgotPassword(BaseModel):
    email: EmailStr
    
    model_config = {
        "from_attributes" : True,
        "json_schema_extra" : {
            "example": {
                "email": "name@email.com"
                }
        }
    }
    
    
class RecoveryPassword(BaseModel):
    password: str
    
    model_config = {
        "from_attributes" : True,
        "json_schema_extra" : {
            "example" : {
                "password": "newstrongpassword123"
                }
        }
    }