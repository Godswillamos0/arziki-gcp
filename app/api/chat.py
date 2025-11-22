from fastapi import APIRouter, HTTPException, Depends
from app.services.chat import (chat_with_ai,
                           get_chat_history,
                           transcribe_audio_file,
                           generate_analytics_report,
                        )

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)

router.post("/message", status_code=200)(chat_with_ai)

router.get("/history", status_code=200)(get_chat_history)

router.post("/audio", status_code=200)(transcribe_audio_file)

router.post("/analytics", status_code=200)(generate_analytics_report)
