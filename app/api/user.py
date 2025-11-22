from fastapi import APIRouter
from app.services.files import (
                            get_all_files,
                            get_file_by_id
                            )

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    responses={404: {"description": "Not found"}},
)

router.get("/", status_code=200)(get_all_files)

router.get("/{file_id}", status_code=200)(get_file_by_id)
