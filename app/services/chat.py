from fastapi import Depends, HTTPException, File, UploadFile
from app.schemas.chat import (ChatMessageDTO, 
                          BussinessDataDTO)
from app.db.models import User, ChatMessages, FileUpload
from app.db.dependencies import db_dependency
from .auth import user_dependency
from ai.main_agent import (generate_reply as ask_llm,
                              predict_demand_v2,
                              generate_report_html, 
                              process_audio, 
                            )
from app.utils.cloud_storage_config import upload_blob, download_blob
from app.core.config import CLOUD_BUCKET_NAME
from datetime import datetime
from app.utils.pdf_config import convert_html_to_pdf





async def chat_with_ai(
    chat_message: ChatMessageDTO,
    user: user_dependency,
    db: db_dependency
):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Here you would integrate with your AI model to get a response
    
    ai_response = ask_llm(user_model.id, chat_message.message)
    
    # Save chat history
    chat_history_model = ChatMessages(
        user_id=user_model.id,
        message=chat_message.message,
        response=ai_response
    )
    db.add(chat_history_model)
    db.commit()
    
    return {
        "user_message": chat_message.message,
        "ai_response": ai_response
    }
    
    
async def get_chat_history(
    user: user_dependency,
    db: db_dependency
):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    chat_histories = db.query(ChatMessages).filter(ChatMessages.user_id == user_model.id).all()
    
    return [
        {
            "id": chat.id,
            "message": chat.message,
            "response": chat.response,
            "timestamp": chat.timestamp
        }
        for chat in chat_histories
    ]
    
    

    
    
async def transcribe_audio_file(
    user: user_dependency,
    db: db_dependency,
    file: UploadFile = File(...)
):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Transcribe audio file
    response, transcription = process_audio(user_model.id, file.file)
    
    
    # Save transcription record
    chat_history_model = ChatMessages(
        user_id=user_model.id,
        message=transcription,
        response=response
    )
    db.add(chat_history_model)
    db.commit()
    
    return {
        "transcription": response
    }
    

# generate analytics pdf report from predictions and save to cloud storage
async def generate_analytics_report(
    business_data: BussinessDataDTO,
    user: user_dependency,
    db: db_dependency
):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate demand predictions and save to output file
    output_file = f"{user_model.id}{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    prediction = predict_demand_v2(business_data.dict())
    
    # Generate HTML report
    html_content = generate_report_html(prediction)
    # Convert HTML to PDF
    output_file = await convert_html_to_pdf(html_content, output_file)
    
    
    # Upload report to cloud storage
    bucket_name = CLOUD_BUCKET_NAME
    blob_name = f"reports_{output_file}"
    upload_blob(bucket_name, output_file, blob_name)
    
    # Save file upload record
    file_upload_model = FileUpload(
        user_id=user_model.id,
        #file_name=output_file,
        file_path=f"https://storage.googleapis.com/{bucket_name}/{blob_name}",
        upload_time=datetime.now()
    )
    db.add(file_upload_model)
    db.commit()
    
    return {
        "file_name": output_file,
        "file_url": f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
    }