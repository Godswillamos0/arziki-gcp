from fastapi import APIRouter, HTTPException, Depends
from app.services.auth import (create_user, 
                           login, 
                           verify_user, 
                           send_veification_mail, 
                           send_forgot_password_mail, 
                           verify_password
                        )



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


router.post("/register", status_code=201)(create_user)

router.post("/login", status_code=201)(login)

router.post("/send-verification-email/{username}", status_code=201)(send_veification_mail)

router.get("/verify/", status_code=200)(verify_user)

router.post("/forgot-password", status_code=201)(send_forgot_password_mail)

router.put("/forgot-password/", status_code=201)(verify_password)


