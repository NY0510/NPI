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
    menu: List[str] = Field(description="학사일정", example=["테스트 일정 1", '테스트 일정 2'])

class ScheduleResponse(BaseModel):
    success: bool = Field(description="성공 여부", example=True)
    data: ScheduleData = Field(description="학사일정 정보")

@router.get("", responses = {
    200: {"model": ScheduleResponse,"description": "학사일정 정보 조회 성공"}, 400: {"model": ErrorResponse, "description": "학사일정 정보 조회 실패"}
})
def lunch(
    month: int = Query(..., title="월", description="월", ge=1, le=12),
    day: int = Query(..., title="일", description="일", ge=1, le=31)
) -> ScheduleResponse | ErrorResponse:
    try:
        # date = f"{datetime.now().year}{month:02d}{day:02d}"
        # url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?key={os.getenv('NEIS_API_KEY')}&type=json&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010536&MMEAL_SC_CODE=2&MLSV_YMD={date}"
        # response = get(url)
        # data = response.json()

        # if 'mealServiceDietInfo' not in data:
        #     return ErrorResponse(error=data['RESULT']['MESSAGE'])
        
        # menu = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
        # result = {"date": date, "menu": [re.sub(r'\s*\([^)]*\)', '', item.strip()) for item in menu.split('<br/>')]} # 괄호 안 내용 및 공백 제거 후 리스트로 변환

        result = {"date": "20210406", "menu": ["테스트 일정 1", "테스트 일정 2"]}
        
        return Response(data=result)
        
    except Exception as e:
        return ErrorResponse(error=str(e))
