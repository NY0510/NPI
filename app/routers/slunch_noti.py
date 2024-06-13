from fastapi import APIRouter, Query, Request, HTTPException, Depends, Body
from pydantic import BaseModel, Field
import firebase_admin
from firebase_admin import credentials, messaging
import os
import datetime
from contextlib import contextmanager

from .responses import ErrorResponse, Response
from app.libs.database import Database

router = APIRouter()
firebase_admin.initialize_app(credentials.Certificate(os.path.join("app", "firebase-admin.json")))

class PushNotification(BaseModel):
    title: str
    body: str
    
@contextmanager
def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

def authorize_request(request: Request):
    secret_key = os.environ["SECRET_KEY"]
    header_key = request.headers.get("X-Secret-Key")
    if header_key != secret_key:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.post("/send", dependencies=[Depends(authorize_request)], responses={
    200: {"model": Response, "description": "푸시 알림 전송 성공"},
    400: {"model": ErrorResponse, "description": "푸시 알림 전송 실패"},
    403: {"model": ErrorResponse, "description": "접근 권한 없음"}
})
def send(
    notification: PushNotification = Body(...),
) -> Response | ErrorResponse:
    try:
        message = messaging.Message(
            data={"title": notification.title, "body": notification.body},
            topic="lunch"
        )
        messaging.send(message)
        
        return Response(data="푸시 알림 전송됨")
    except Exception as e:
        return ErrorResponse(error=str(e))
