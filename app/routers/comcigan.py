from typing import List, Annotated, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from pycomcigan import TimeTable, get_school_code

from .responses import ErrorResponse, Response

router = APIRouter()

class OriginalClass(BaseModel):
    period: int = Field(description="대체된 교시", example=1)
    subject: str = Field(description="대체된 과목", example="영어1B")
    teacher: str = Field(description="대체된 선생님", example="김지*")

class ClassInfo(BaseModel):
    period: int = Field(description="교시", example=1)
    subject: str = Field(description="과목", example="국사")
    teacher: str = Field(description="선생님", example="김환*")
    replaced: bool = Field(description="대체 여부", example=True)
    original: Optional[OriginalClass] = None

class TimetableResponse(BaseModel):
    success: bool = Field(description="성공 여부", example=True)
    data: List[List[ClassInfo]] = Field(description="시간표")

class ClasslistResponse(BaseModel):
    success: bool = Field(description="성공 여부", example=True)
    data: List[str] = Field(description="반 리스트", example=["1-1","1-2",'1-3',"1-4","1-5"])

class SchoolInfo(BaseModel):
    name: str = Field(description="학교 이름", example="선린인터넷고")
    period: str = Field(description="교육청", example="서울")
    code: int = Field(description="학교 코드", example=24966)

class SchoolSearchResponse(BaseModel):
    success: bool = Field(description="성공 여부", example=True)
    data: List[SchoolInfo] = Field(description="학교 검색 결과", example=[{"name":"선린중학교","period":"서울","code":24966},{"name":"선린인터넷고","period":"서울","code":24966}])


def get_timetable(school_name: str, school_grade: int, school_class: int, next_week: bool) -> Response | ErrorResponse:
    try:
        timetable = TimeTable(school_name, 1 if next_week else 0)
        del timetable.timetable[school_grade][school_class][0] # 0번째 인덱스에 빈 배열 제거
        return Response(data=timetable.timetable[school_grade][school_class])
    except Exception as e:
        return ErrorResponse(error=str(e))

def get_classlist(school_name: str) -> Response | ErrorResponse:
    try:
        timetable = TimeTable(school_name, 0)
        class_list = [f"{grade}-{_class}" for grade, grade_data in enumerate(timetable.timetable) for _class, class_data in enumerate(grade_data) if class_data]
        return Response(data=class_list)
    except Exception as e:
        return ErrorResponse(error=str(e))
        
def search_school(school_name: str) -> Response | ErrorResponse:
    try:
        search_results = get_school_code(school_name)
        filtered_results = [{'name': result[2], 'period': result[1], 'code': result[0]} for result in search_results if result[0] != 0] # code가 0인 학교는 제외
        return Response(data=filtered_results)
    except Exception as e:
        return ErrorResponse(error=str(e))

@router.get("/timetable", responses = {
    200: {"model": TimetableResponse, "description": "시간표 조회 성공"}, 400: {"model": ErrorResponse, "description": "시간표 조회 실패"}
})
def timetable(
    school_name: Annotated[str, Query(description="학교 이름\n\n중복되는 학교가 없을 경우 일부만 입력해도 자동으로 선택됩니다.")],
    school_grade: Annotated[int, Query(description="학년")],
    school_class: Annotated[int, Query(description="반")],
    next_week: Annotated[bool, Query(description="다음 주 시간표를 가져올지 여부")] = False
) -> TimetableResponse | ErrorResponse:
    return get_timetable(school_name, school_grade, school_class, next_week)

@router.get('/classlist', responses = {
    200: {"model": ClasslistResponse, "description": "반 리스트 조회 성공"}, 400: {"model": ErrorResponse, "description": "반 리스트 조회 실패"}
})
def classlist(
    school_name: Annotated[str, Query(description="학교 이름\n\n중복되는 학교가 없을 경우 일부만 입력해도 자동으로 선택됩니다.")]
) -> ClasslistResponse | ErrorResponse:
    return get_classlist(school_name)

@router.get('/search', responses = {
    200: {"model": SchoolSearchResponse, "description": "학교 검색 성공"}, 400: {"model": ErrorResponse, "description": "학교 검색 실패"}
})
def search(school_name: Annotated[str, Query(description="학교 이름\n\n중복되는 학교가 없을 경우 일부만 입력해도 자동으로 선택됩니다.")]
) -> SchoolSearchResponse | ErrorResponse:
    return search_school(school_name)
