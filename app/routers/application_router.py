# routers/applications.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..models.user import User
from ..core.security import get_current_user
from .deps_router import get_db
from ..schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from ..services.application_service import ApplicationService

router = APIRouter(
    prefix="/applications",
    tags=["applications"],
    responses={404: {"description": "Not found"}},
)


def service(db: Session = Depends(get_db)) -> ApplicationService:  # 의존성 주입을 통해 데이터베이스 세션을 가져오는 함수
    """애플리케이션 서비스 인스턴스를 생성합니다."""
    return ApplicationService(db)


@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="애플리케이션 생성 및 API 키 발급",
    description="새로운 애플리케이션을 생성합니다.",
)
def create_application(
    createApp: ApplicationCreate,  # 애플리케이션 생성에 필요한 데이터
    currentUser: User = Depends(get_current_user),  # 현재 인증된 사용자 정보 가져오기
    service: ApplicationService = Depends(service)
):
    return service.create_application(currentUser, createApp)


@router.get(
    "/all",
    response_model=List[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="내 애플리케이션 목록 조회",
    description="현재 인증된 사용자의 모든 애플리케이션 목록을 조회합니다.",
)
def get_applications(
    currentUser: User = Depends(get_current_user),
    service: ApplicationService = Depends(service)
):
    return service.get_applications(currentUser)


@router.get(
    "/{appId}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="애플리케이션 단일 조회",
    description="애플리케이션 ID로 단일 애플리케이션을 조회합니다.",
)
def get_application(
    appId: int,  # 애플리케이션 ID
    currentUser: User = Depends(get_current_user),  # 현재 인증된 사용자 정보 가져오기
    service: ApplicationService = Depends(service)
):
    return service.get_application(appId, currentUser)


@router.patch(
    "/{appId}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="애플리케이션 정보 업데이트",
    description="애플리케이션 정보를 업데이트합니다.",
)
def update_application(
    appId: str,  # 애플리케이션 ID
    appUpdate: ApplicationUpdate,  # 애플리케이션 업데이트에 필요한 데이터
    currentUser: User = Depends(get_current_user),  # 현재 인증된 사용자 정보 가져오기
    service: ApplicationService = Depends(service)
):
    # 애플리케이션을 업데이트합니다. 현재는 API 키도 함께 업데이트하지 않음
    return service.update_application(appId, currentUser, appUpdate)


@router.delete(
    "/{appId}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="애플리케이션 소프트 삭제",
    description="애플리케이션을 소프트 삭제합니다.",
)
def delete_application(
    appId: str,  # 애플리케이션 ID
    currentUser: User = Depends(get_current_user),
    service: ApplicationService = Depends(service)
):
    # 애플리케이션을 소프트 삭제합니다. 현재는 API 키도 함께 삭제하지 않음
    return service.delete_application(appId, currentUser)
