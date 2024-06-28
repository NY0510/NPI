from fastapi import APIRouter, Query, Request, HTTPException, Depends, Body, Header
import os
from bson.json_util import dumps
import json
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

from .responses import ErrorResponse, Response
from app.libs.database import db

load_dotenv()
router = APIRouter()
db = db(os.getenv("MONGODB_URL"), "slunch")

@router.get("")
async def comment(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=100)):
    today = datetime.datetime.now().date()
    start_of_day = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
    end_of_day = datetime.datetime(today.year, today.month, today.day, 23, 59, 59, 999999)
    
    comments = db.find("comments", {"date": {"$gte": start_of_day, "$lt": end_of_day}}).sort("date", -1)
    comments = comments.skip((page - 1) * page_size).limit(page_size)
    comments = list(comments)
    
    data = []
    for comment in comments:
        data.append({
            "username": comment["username"],
            "comment": comment["comment"],
            "date": comment["date"]
        })
    
    return Response(data=data)

@router.post("")
async def comment(request: Request, username: str = Body(..., max_length=8), comment: str = Body(..., max_length=40), uuid: Optional[str] = Body(None), x_real_ip: str = Header(None)):
    if uuid is not None:
        thirty_seconds_ago = datetime.now() - timedelta(seconds=30)

        if db.find_one("blocked_uuids", {"uuid": uuid}) is not None:
            raise HTTPException(status_code=403, detail="You are banned from commenting")
        
        if db.find_one("comments", {"uuid": uuid, "date": {"$gte": thirty_seconds_ago}}):
            raise HTTPException(status_code=429, detail="You are commenting too fast")
    
    today = datetime.now()
    
    print(f"Comment from {x_real_ip}: {username} - {comment}")
    
    db.insert("comments", {
        "username": username,
        "comment": comment,
        "date": today,
        "ip": x_real_ip,
        "uuid": uuid
    })
    
    return Response(data={"username": username, "comment": comment, "date": today, "ip": x_real_ip})
