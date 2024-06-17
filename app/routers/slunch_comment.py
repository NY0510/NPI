from fastapi import APIRouter, Query, Request, HTTPException, Depends, Body
import os
from bson.json_util import dumps
import json
import datetime

from .responses import ErrorResponse, Response
from app.libs.database import db

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
async def comment(request: Request, username: str = Body(...), comment: str = Body(...)):
    today = datetime.datetime.now()
    
    db.insert("comments", {
        "username": username,
        "comment": comment,
        "date": today
    })
    
    return Response(data={"username": username, "comment": comment, "date": today})
