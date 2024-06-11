from fastapi import APIRouter, Query, Request, HTTPException, Depends, Header
from pydantic import BaseModel, Field
import firebase_admin
from firebase_admin import credentials, messaging
import os
import datetime

from .responses import ErrorResponse, Response
from app.libs.database import Database

router = APIRouter()
firebase_admin.initialize_app(credentials.Certificate(os.path.join("app", "firebase-admin.json")))

class PushNotification(BaseModel):
    title: str
    body: str

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

def localhost_only(request: Request):
    secret_key = os.environ["SECRET_KEY"]
    header_key = request.headers.get("X-Secret-Key")
    if header_key != secret_key:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/subscribe", responses={
    200: {"model": Response, "description": "구독 성공"},
    400: {"model": ErrorResponse, "description": "구독 실패"}
})
def subscribe(
    token: str = Query(..., title="토큰", description="FCM 토큰"),
    db: Database = Depends(get_db)
) -> Response | ErrorResponse:
    try:
        db.execute("INSERT INTO slunch_noti (token) VALUES (?)", (token,))
        return Response(data="구독 성공")
    except Exception as e:
        return ErrorResponse(error=str(e))

@router.get("/unsubscribe", responses={
    200: {"model": Response, "description": "구독 해지 성공"},
    400: {"model": ErrorResponse, "description": "구독 해지 실패"}
})
def unsubscribe(
    token: str = Query(..., title="토큰", description="FCM 토큰"),
    db: Database = Depends(get_db)
) -> Response | ErrorResponse:
    try:
        db.execute("DELETE FROM slunch_noti WHERE token = ?", (token,))
        return Response(data="구독 해지 성공")
    except Exception as e:
        return ErrorResponse(error=str(e))
        
@router.post("/send", dependencies=[Depends(localhost_only)], responses={
    200: {"model": Response, "description": "푸시 알림 전송 성공"},
    400: {"model": ErrorResponse, "description": "푸시 알림 전송 실패"},
    403: {"model": ErrorResponse, "description": "허용되지 않은 IP 주소"}
})
def send(
    notification: PushNotification = Body(...),
    db: Database = Depends(get_db)
) -> Response | ErrorResponse:
    if not title or not body:
        raise ErrorResponse(error="제목과 내용을 입력해주세요.")

    try:
        subscribers = db.fetchall("SELECT token FROM slunch_noti")
        
        success, faild = 0, 0

        for subscriber in subscribers:
            try:
                message = messaging.Message(
                    data={"title": notification.title, "body": notification.body},
                    token=subscriber["token"]
                )
                messaging.send(message)
            except Exception as e:
                faild += 1
            else:
                success += 1

        return Response(data=f"푸시 알림 전송됨. 성공: {success}명, 실패: {faild}명, 전체 {len(subscribers)}명")
    except Exception as e:
        return ErrorResponse(error=str(e))