from fastapi import APIRouter, Query
from typing import List, Annotated, Optional
from requests import get
import os
import re
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .responses import ErrorResponse, Response

load_dotenv()
router = APIRouter()

class LunchData(BaseModel):
    date: str = Field(description="날짜", example="2024604")
    menu: List[str] = Field(description="급식 메뉴", example=["발아현미밥","옹심이수제비국","한식잡채","데리야끼닭장각구이","배추김치","멜론"])

class LunchResponse(BaseModel):
    success: bool = Field(description="성공 여부", example=True)
    data: Optional[List[dict[str, str | List[str]]]] = Field(description="급식 정보")


@router.get("", responses = {
    200: {"model": LunchResponse,"description": "급식 정보 조회 성공"}, 
    400: {"model": ErrorResponse, "description": "급식 정보 조회 실패"}
})
def lunch(
    month: int = Query(..., title="월", description="월", ge=1, le=12),
    day: Optional[int] = Query(None, title="일", description="일", ge=1, le=31)
) -> LunchResponse | ErrorResponse:
    try:
        if day is not None:
            date = f"{datetime.now().year}{month:02d}{day:02d}"
        else:
            date = f"{datetime.now().year}{month:02d}"

        url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?key={os.getenv('NEIS_API_KEY')}&type=json&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010536&MMEAL_SC_CODE=2&MLSV_YMD={date}"
        response = get(url)
        data = response.json()

        if 'mealServiceDietInfo' not in data:
            return ErrorResponse(error=data['RESULT']['MESSAGE'])

        results = []
        for row in data['mealServiceDietInfo'][1]['row']:
            menu = row['DDISH_NM']
            result = {"date": row['MLSV_YMD'], "menu": [re.sub(r'\s*\([^)]*\)', '', item.strip()) for item in menu.split('<br/>')]} # 괄호 안 내용 및 공백 제거 후 리스트로 변환
            
            results.append(result)
        
        return LunchResponse(success=True, data=results)
        
    except Exception as e:
        return ErrorResponse(error=str(e))