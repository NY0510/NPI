from fastapi import APIRouter, Query, Request, HTTPException, Depends
from pydantic import BaseModel, Field
import firebase_admin
from firebase_admin import credentials, messaging
from os import path

from .responses import ErrorResponse, Response
from app.libs.database import db

router = APIRouter()
firebase_admin.initialize_app(credentials.Certificate(path.join("app", "firebase-admin.json")))

def localhost_only(request: Request):
    if not any(ip in request.client.host for ip in ["192.168","127.0.0.1"]):
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/subscribe", responses={
    200: {"model": Response, "description": "구독 성공"},
    400: {"model": ErrorResponse, "description": "구독 실패"}
})
def subscribe(
    token: str = Query(..., title="토큰", description="FCM 토큰"),
) -> Response | ErrorResponse:
    try:
        db.execute("INSERT INTO slunch_noti (token) VALUES (%s)", (token,))
        return Response(data="구독 성공")
    except Exception as e:
        return ErrorResponse(error=str(e))

@router.get("/unsubscribe", responses={
    200: {"model": Response, "description": "구독 해지 성공"},
    400: {"model": ErrorResponse, "description": "구독 해지 실패"}
})
def unsubscribe(
    token: str = Query(..., title="토큰", description="FCM 토큰"),
) -> Response | ErrorResponse:
    try:
        db.execute("DELETE FROM slunch_noti WHERE token = %s", (token,))
        return Response(data="구독 해지 성공")
    except Exception as e:
        return ErrorResponse(error=str(e))

@router.get("/send", dependencies=[Depends(localhost_only)], responses={
    200: {"model": Response, "description": "푸시 알림 전송 성공"},
    400: {"model": ErrorResponse, "description": "푸시 알림 전송 실패"},
    403: {"model": ErrorResponse, "description": "허용되지 않은 IP 주소"}
})
def send(
    title: str = Query(..., title="제목", description="푸시 알림 제목"),
    body: str = Query(..., title="내용", description="푸시 알림 내용"),
) -> Response | ErrorResponse:
    try:
        notiPayload = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            topic="lunch"
        )
        messaging.send(notiPayload)
        return Response(data="푸시 알림 전송 성공")
    except Exception as e:
        return ErrorResponse(error=str(e))