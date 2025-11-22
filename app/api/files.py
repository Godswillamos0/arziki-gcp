from fastapi import APIRouter
from app.services.files import (
                            get_all_files,
                            )

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    responses={404: {"description": "Not found"}},
)

router.get("/", status_code=200)(get_all_files)

