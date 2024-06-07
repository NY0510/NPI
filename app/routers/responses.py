from pydantic import BaseModel, Field
from typing import Any

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="성공 여부")
    error: str = Field(..., description="에러 메시지")

class Response(BaseModel):
    success: bool = Field(True, description="성공 여부")
    data: Any = Field(..., description="데이터")