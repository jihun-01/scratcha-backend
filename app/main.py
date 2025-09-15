from fastapi import FastAPI, Request, status, HTTPException
import logging.config
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from prometheus_fastapi_instrumentator import Instrumentator


from db.session import engine
from app.routers import payment_router, users_router, auth_router, application_router, api_key_router, captcha_router, usage_stats_router, contact_router
from app.admin.admin import setup_admin
from app.admin.auth import AdminAuth
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    print("로깅 설정 적용...")
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
    yield
    # Shutdown event
    print("데이터베이스 연결 풀 해제...")
    engine.dispose()
    print("애플리케이션 종료.")

app = FastAPI(
    title="Dashboard API",
    description="scratCHA API 서버",
    lifespan=lifespan  # Add lifespan to FastAPI app
)

# Prometheus 메트릭을 설정합니다.
Instrumentator().instrument(app).expose(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic 모델 유효성 검사 오류에 대한 커스텀 핸들러.
    첫 번째 오류 메시지를 detail 필드에 직접 담아 응답합니다.
    """
    error_list = exc.errors()
    if not error_list:
        # 오류 목록이 비어있는 드문 경우
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "입력 값의 유효성 검사에 실패했습니다."},
        )

    # 첫 번째 오류 정보를 가져옵니다.
    first_error = error_list[0]
    message = first_error['msg']

    # 'Value error, ' 접두사 제거
    if first_error['type'] == 'value_error':
        message = message.removeprefix('Value error, ')

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": message},
    )


# 로거 설정
logger = logging.getLogger(__name__)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTPException이 발생했을 때, 오류 내용을 로깅하기 위한 커스텀 핸들러입니다.
    """
    logger.error(
        f"HTTP 예외 발생: {request.method} {request.url.path} {exc.status_code} {exc.detail}"
    )
    # 기본 HTTPException 동작과 동일하게 JSON 응답을 반환합니다.
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SessionMiddleware를 추가하여 request.session을 사용할 수 있도록 합니다.
# SQLAdmin의 인증 백엔드(AdminAuth)가 세션에 접근하기 위해 필요합니다.
# secret_key는 세션 데이터를 암호화하는 데 사용됩니다. 실제 운영 환경에서는 환경 변수 등으로 관리해야 합니다.
app.add_middleware(SessionMiddleware,
                   secret_key=settings.SESSION_SECRET_KEY)

# SQLAdmin 관리자 인터페이스를 설정합니다.
# setup_admin 함수를 통해 모든 ModelView가 등록됩니다.
authentication_backend = AdminAuth(
    secret_key=settings.SESSION_SECRET_KEY)
admin = setup_admin(app, engine)
admin.authentication_backend = authentication_backend


@app.get("/")
def read_root():
    return {"message": "scratCHA API 서버"}


# 라우터 등록
app.include_router(users_router.router, prefix="/api/dashboard")
app.include_router(auth_router.router, prefix="/api/dashboard")
app.include_router(application_router.router, prefix="/api/dashboard")
app.include_router(api_key_router.router, prefix="/api/dashboard")
app.include_router(usage_stats_router.router, prefix="/api/dashboard")
app.include_router(captcha_router.router, prefix="/api")
app.include_router(payment_router.router, prefix="/api")
app.include_router(contact_router.router, prefix="/api")
