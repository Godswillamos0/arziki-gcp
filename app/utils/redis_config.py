from fastapi import Request
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


async def set_key(request: Request, key:str, value:str, exp:int):
    r = request.app.state.redis
    r.setex(key, exp, value)
    
    
async def get_key(request: Request, key:str):
    r = request.app.state.redis
    value = r.get(key)
    return value.decode() if value else None