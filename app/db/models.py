import uuid
from sqlalchemy import (
    Column, String, DateTime, func, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    user_name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    profile_image = Column(String, nullable=True)
    
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    

class ChatHistory(Base):
    __tablename__ = "chat_messages"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    response = Column(String, nullable=True)
    
    user = relationship("User", back_populates="chat_messages")
    
    
class FileUpload(Base):
    __tablename__ = "file_uploads"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    file_path = Column(String, nullable=False)
    upload_time = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="file_uploads")
    