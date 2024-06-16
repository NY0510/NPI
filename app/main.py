from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.routers import comcigan, snt_lunch, snt_schedule, slunch_noti

load_dotenv()

tags_metadata = [
    {
        'name': '컴시간',
        'description': '[컴시간알리미](http://컴시간학생.kr)의 시간표를 가져옵니다.'  
    },
    {
        'name': '선린인터넷고 급식',
        'description': '선린인터넷고등학교의 급식을 가져옵니다.'
    },
    {
        'name': '선린인터넷고 학사일정',
        'description': '선린인터넷고등학교의 학사일정을 가져옵니다.'
    },
    {
        'name': 'Slunch 급식 알림',
        'description': 'Slunch의 급식 알림을 관리합니다.'
    }
]

app = FastAPI(
    title="NPI",
    description="NY64's Private API",
    version='0.1.0',
    contact={
        'name': 'NY64',
        'url': 'https://ny64.kr',
        'email': 'me@ny64.kr'
    },
    redoc_url=None,
    openapi_tags=tags_metadata
)

@app.get("/", response_class=PlainTextResponse)
def root() -> PlainTextResponse:
    return f"""NY64's Private API v{app.version}
API Docs: /docs
Contact: {app.contact['email']}
"""

app.include_router(comcigan.router, prefix="/comcigan", tags=["컴시간"])
app.include_router(snt_lunch.router, prefix="/snt_lunch", tags=["선린인터넷고 급식"])
app.include_router(snt_schedule.router, prefix="/snt_schedule", tags=["선린인터넷고 학사일정"])
app.include_router(slunch_noti.router, prefix="/slunch_noti", tags=["Slunch 급식 알림"])