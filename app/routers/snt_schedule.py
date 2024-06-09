from fastapi import APIRouter, Query
from typing import List, Annotated, Optional
from requests import get
import os
import re
from datetime import datetime
from pydantic import BaseModel, Field

from .responses import ErrorResponse, Response

router = APIRouter()

class ScheduleData(BaseModel):
    date: str = Field(description="날짜", example="2024604")
    event: str = Field(description="학사일정", example="테스트 일정")

class ScheduleResponse(BaseModel):
    success: bool = Field(description="성공 여부", example=True)
    data: List[ScheduleData] = Field(description="학사일정 정보")

@router.get("", responses = {
    200: {"model": ScheduleResponse,"description": "학사일정 정보 조회 성공"}, 400: {"model": ErrorResponse, "description": "학사일정 정보 조회 실패"}
})
def lunch(
    month: int = Query(..., title="월", description="월", ge=1, le=12),
) -> ScheduleResponse | ErrorResponse:
    try:
        date = f"{datetime.now().year}{str(month).zfill(2)}"
        url = f"https://open.neis.go.kr/hub/SchoolSchedule?key={os.getenv('NEIS_API_KEY')}&type=json&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010536&MMEAL_SC_CODE=2&AA_YMD={date}"
        response = get(url)
        data = response.json()

        if 'SchoolSchedule' not in data:
            return ErrorResponse(error=data['RESULT']['MESSAGE'])
        
        result = []

        for schedule in data['SchoolSchedule'][1]['row']:
            if schedule['EVENT_NM'] == '토요휴업일': continue
            result.append({
                'date': schedule['AA_YMD'],
                'event': schedule['EVENT_NM']
            })
        
        return Response(data=result)
        
    except Exception as e:
        return ErrorResponse(error=str(e))
