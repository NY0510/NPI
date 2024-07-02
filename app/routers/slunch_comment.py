from fastapi import APIRouter, Query, Request, HTTPException, Depends, Body, Header
import os
from bson.json_util import dumps
import json
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import hashlib
import hmac
from bson import ObjectId

from .responses import ErrorResponse, Response
from app.libs.database import db

load_dotenv()
router = APIRouter()
db = db(os.getenv("MONGODB_URL"), "slunch")

# HMAC-SHA256 서명 생성 
def generate_signature(uuid: str, timestamp: int, secret_key: str) -> str:
    message = f"{uuid}:{timestamp}"
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

def check_non_normal_unicode(text: str) -> bool:
    non_normal_unicode = r"[\uD800-\uDFFF\uDC00-\uDFFF\uFEFF]"
    
    if re.search(non_normal_unicode, text):
        return True

@router.get("")
async def comment(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=100)):
    today = datetime.now().date()
    start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
    end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59, 999999)
    
    comments = db.find("comments", {"date": {"$gte": start_of_day, "$lt": end_of_day}}).sort("date", -1)
    comments = comments.skip((page - 1) * page_size).limit(page_size)
    comments = list(comments)
    
    data = []
    for comment in comments:
        data.append({
            "username": comment["username"],
            "comment": comment["comment"],
            "date": comment["date"],
            "uuid": comment["uuid"],
            "id": str(comment["_id"])
        })
    
    return Response(data=data)

@router.post("")
async def comment(request: Request, 
                  username: str = Body(..., max_length=8),
                  comment: str = Body(..., max_length=40),
                  x_uuid: str = Header(None),
                  x_timestamp: int = Header(None),
                  x_signature: str = Header(None),
                  x_real_ip: str = Header(None)):

    if not x_uuid or not x_timestamp or not x_signature:
        raise HTTPException(status_code=403, detail="Missing headers")

    thirty_seconds_ago = datetime.now() - timedelta(seconds=30)
    server_timestamp = int(datetime.now().timestamp() * 1000)
    
    # Check if user is banned
    if db.find_one("blocked_uuids", {"uuid": x_uuid}):
        print(f"Banned user {x_uuid} tried to comment")
        db.update("blocked_uuids", {"uuid": x_uuid}, {"$inc": {"count": 1}})
        raise HTTPException(status_code=403, detail="You are banned from commenting")

    # Check if user is commenting too fast
    if db.find_one("comments", {"uuid": x_uuid, "date": {"$gte": thirty_seconds_ago}}):
        raise HTTPException(status_code=429, detail="You are commenting too fast")

    # Validate timestamp
    if abs(server_timestamp - x_timestamp) > 30000:
        raise HTTPException(status_code=403, detail="Invalid timestamp")

    # Validate signature
    secret_key = os.getenv("SECRET_KEY")
    server_signature = generate_signature(x_uuid, x_timestamp, secret_key)
    if x_signature != server_signature:
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Check if username or comment contains non-normal unicode characters
    if check_non_normal_unicode(username) or check_non_normal_unicode(comment):
        raise HTTPException(status_code=403, detail="Non-normal unicode characters are not allowed")

    today = datetime.now()
    print(f"Comment from {x_real_ip}: {username} - {comment}")

    # Save comment to database
    db.insert("comments", {
        "username": username,
        "comment": comment,
        "date": today,
        "ip": x_real_ip,
        "uuid": x_uuid
    })

    return {"username": username, "comment": comment, "date": today, "ip": x_real_ip}

@router.put("/{comment_id}")
async def update_comment(comment_id: str, comment: str = Body(..., max_length=40), x_uuid: str = Header(None), x_timestamp: int = Header(-1), x_signature: str = Header(None)):
    if x_timestamp == -1:
        raise HTTPException(status_code=403, detail="Missing headers")
    
    thirty_seconds_ago = datetime.now() - timedelta(seconds=30)
    server_timestamp = int(datetime.now().timestamp() * 1000)
    
    # Check if user is banned
    if db.find_one("blocked_uuids", {"uuid": x_uuid}):
        print(f"Banned user {x_uuid} tried to update comment")
        db.update("blocked_uuids", {"uuid": x_uuid}, {"$inc": {"count": 1}})
        raise HTTPException(status_code=403, detail="You are banned from updating comments")

    # Check if user is updating too fast
    if db.find_one("comments", {"uuid": x_uuid, "date": {"$gte": thirty_seconds_ago}}):
        raise HTTPException(status_code=429, detail="You are updating too fast")

    # Validate timestamp
    if abs(server_timestamp - x_timestamp) > 30000:
        raise HTTPException(status_code=403, detail="Invalid timestamp")

    # Validate signature
    secret_key = os.getenv("SECRET_KEY")
    server_signature = generate_signature(x_uuid, x_timestamp, secret_key)
    if x_signature != server_signature:
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Check if comment exists
    existing_comment = db.find_one("comments", {"_id": ObjectId(comment_id)})  # Corrected line
    if not existing_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Update comment
    db.update_one("comments", {"_id": ObjectId(comment_id)}, {"$set": {"comment": comment}})
    
    return {"username": existing_comment["username"], "comment": comment, "date": existing_comment["date"], "ip": existing_comment["ip"]}