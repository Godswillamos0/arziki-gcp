from datetime import timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db import models
from app.db import database
from app.api import router as api_router
from app.utils.token_config import TokenData                
from redis import Redis
from app.utils.redis_config import get_key

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




PUBLIC_PATHS = [
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/verify",
    "/api/v1/user/me/forgot-password",
    "/api/v1/user/me/reset-password",
]

@app.on_event("startup")
async def startup_event():
    app.state.redis = Redis(host='localhost',port=6379)


@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()
        
        
@app.middleware("http")
async def check_blacklist(request: Request,
                          call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        r = await get_key(request, token)
        if r:
           # raise HTTPException(status_code=401, detail="Token is missing") --Don't use this it crashes in middleware
           return JSONResponse(status_code=401, content= {"detail" : "Token is missing"})
    response = await call_next(request)
    return response
        
        
# Include routers dynamically
app.include_router(api_router.router, 
                   prefix="/api/v1")


# Run app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
