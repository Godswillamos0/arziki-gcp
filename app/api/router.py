from fastapi import APIRouter
from . import auth, chat, files, user

router = APIRouter()

router.include_router(auth.router)
router.include_router(chat.router)
router.include_router(files.router)
router.include_router(user.router)