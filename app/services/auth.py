import time
from sqlalchemy import or_
from app.schemas.user import CreateUserDTO, UpdateUserDTO, UpdatePassword, ForgotPassword, RecoveryPassword
from app.db.models import User
from app.utils.token_config import TokenData
from app.utils.mail_config import send_mail
from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.db.dependencies import db_dependency
from passlib.context import CryptContext
from app.core.config import (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
from datetime import datetime, timedelta
from typing import Annotated
from app.utils.redis_config import set_key, get_key


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SECRET_KEY = SECRET_KEY
ALGORITHM = ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = TokenData.decode_token(token)
        
        username: str = payload.get('sub') 
        
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {
            'username': username, 
            'id': payload.get('id'), 
            'user_role': payload.get('role')
            }
        
    except JWTError:
        raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


user_dependency = Annotated[dict, Depends(get_current_user)]


async def create_user(create_user_dto: CreateUserDTO, db: db_dependency):
    hashed_password = pwd_context.hash(create_user_dto.password)
    db_user = User(
        email=create_user_dto.email,
        username=create_user_dto.username,
        hashed_password=hashed_password,
        role=create_user_dto.role or 'user',
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                db: db_dependency):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token = TokenData(user.username)
    access_token = token.create_token(
        expires=access_token_expires,
        user_id=user.id,
        role=user.role
    )
    
    response = JSONResponse(content={
        "access_token" : access_token,
         "token_type" : "bearer",
         "message": f"{user.username}, Login successful"})
    
    return response


def authenticate_user(username: str, 
                      password: str, 
                      db: db_dependency):
    # check if username is username or email
    def check_if_email(username: str):
        return "@" in username and "." in username
    
    if check_if_email(username):
        user = db.query(User).filter(User.email==username).first()
    else: 
        user = db.query(User).filter(User.username==username).first()
        
    if not user:
        raise HTTPException(status_code=404, detail="Incorrect username or password")
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return user


async def send_veification_mail(user: user_dependency, 
                                db: db_dependency,
                                ):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_model.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")
    
    token = TokenData(username=user_model.email).create_token(
        expires=timedelta(hours=1),
        user_id=user_model.id,
        role=user_model.role,
    )

    
    await send_mail(
        email=user_model.email,
        subject="Verify your account",
        body=f"Use this token to verify your account: http://127.0.0.1:8000/api/auth/verify?token={token}"
    )
    
    return {
        "detail": f"Verification email sent to {user_model.email}"
    }
    
    
async def verify_user(db: db_dependency,
                      token: str =Query(...)
                      ):
    
    payload = TokenData.decode_token(token)
    
    user_model = db.query(User).filter(User.id == payload.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_model.is_verified = 1
    
    db.commit()
    db.refresh(user_model)

    
    return {
        "username": user_model.username,
        "detail": "User verified successfully"
        }
    
    
async def send_forgot_password_mail(db: db_dependency,
                                    email: ForgotPassword):
    user_model = db.query(User).filter(User.email==email.email).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="Email address not found")
    
    token = TokenData(username=user_model.email).create_token(
        expires=timedelta(hours=1),
        user_id=user_model.id,
        role=user_model.role,
    )

    
    await send_mail(
        email=user_model.email,
        subject="Forgot Password",
        body=f"Use this token to verify your account: http://127.0.0.1:8000/api/auth/forgot-password?token={token}"
    )
    
    return {
        "detail": f"Forgot email sent to {user_model.email}"
    }
    
    
async def verify_password(db: db_dependency,
                          password: RecoveryPassword,
                          token:str = Query(...),
                          ):
    payload = TokenData.decode_token(token=token)
    
    user_model = db.query(User).filter(User.id == payload.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_model.hashed_password = pwd_context.hash(password.password)
    
    db.commit()
    return {
        "message": f"{user_model.email}, you have successfully changed your password."
    }
    
    
async def logout(request: Request,
                 user: user_dependency,
                 db: db_dependency):
    
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    #response = TokenData.remove_token_from_cookies()
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ")[1]
    
    #Decode token
    payload = TokenData.decode_token(token)
    
    exp = payload.get("exp")
    
    if not payload.get("exp"):
        raise HTTPException(status_code=400, detail="Token compromised, exp missing")
    
    ttl = exp - int(time.time())
    if ttl < 0:
        raise HTTPException(status_code=400, detail="Token already expired")

    #add access_token to redis
    await set_key(request=request,
            key= token,
            value="blacklisted",
            exp=ttl
            )
    
    
    return {
        "message": f"{user_model.username}, you've successfully logged out."
    }


def if_verified(user: user_dependency):
    if not user.get("is_verified"):
        raise HTTPException(status_code=403, detail="User not verified")
    return True
