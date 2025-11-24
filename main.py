from datetime import timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db import models
from app.db import database
from app.api import router as api_router
from app.utils.token_config import TokenData                

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
        
        
# Include routers dynamically
app.include_router(api_router.router, 
                   prefix="/api/v1")


# Run app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
