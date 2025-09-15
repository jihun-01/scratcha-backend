# schemas/application.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.schemas.api_key import ApiKeyResponse

# 애플리케이션 생성 요청 스키마


class ApplicationCreate(BaseModel):
    appName: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="애플리케이션의 이름",
        example="내 첫번째 애플리케이션"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="애플리케이션에 대한 상세 설명",
        example="사용자 인증을 위한 스크래치 기반 캡챠 서비스"
    )
    expiresPolicy: int = Field(
        ...,
        description="API 키 만료 정책(일 단위). 0 또는 음수는 무제한을 의미합니다.",
        example=30
    )

# 애플리케이션 업데이트 요청 스키마


class ApplicationUpdate(BaseModel):

    appName: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="새로운 애플리케이션의 이름",
        example="새로운 애플리케이션 이름"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="새로운 애플리케이션에 대한 상세 설명",
        example="업데이트된 애플리케이션 설명"
    )

# 애플리케이션 응답 스키마


class ApplicationResponse(BaseModel):
    id: int = Field(..., description="애플리케이션의 고유 식별자", example=1)
    userId: int = Field(...,
                        description="애플리케이션을 소유한 사용자의 고유 식별자", example=101)
    appName: str = Field(..., description="애플리케이션의 이름", example="내 첫번째 애플리케이션")
    description: Optional[str] = Field(
        None, description="애플리케이션에 대한 상세 설명", example="사용자 인증을 위한 스크래치 기반 캡챠 서비스")
    key: Optional[ApiKeyResponse] = Field(
        None, description="애플리케이션에 발급된 API 키 정보")
    createdAt: datetime = Field(..., description="애플리케이션 생성 일시",
                                example="2024-01-01T12:00:00")
    updatedAt: datetime = Field(..., description="애플리케이션 마지막 수정 일시",
                                example="2024-01-01T12:00:00")
    deletedAt: Optional[datetime] = Field(
        None, description="애플리케이션 삭제 일시", example=None)

    class Config:
        from_attributes = True  # Pydantic v2: orm_mode 대신 from_attributes 사용


class CountResponse(BaseModel):
    count: int = Field(..., description="애플리케이션의 총 개수", example=42)
