import logging
import traceback
from contextlib import asynccontextmanager
from core.exceptions import ExternalServiceError

import httpx
from async_fastapi_jwt_auth.exceptions import MissingTokenError, InvalidHeaderError, JWTDecodeError
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis

from api.v1 import auth, places
from core import http as http_module
from core.config import settings
from core.logger import setup_logging
from db import redis as redis_module

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()


app = FastAPI(
    title=settings.project_name,
    description='Сервис для планирования и управления путешествиями',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.exception_handler(MissingTokenError)
async def missing_token_exception_handler(request: Request, exc: MissingTokenError):
    """
    Обработка ошибки отсутствия токена.
    """
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': exc.message}
    )


@app.exception_handler(InvalidHeaderError)
async def invalid_header_exception_handler(request: Request, exc: InvalidHeaderError):
    """
    Обработка ошибки некорректного заголовка.
    """
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'detail': exc.message}
    )


@app.exception_handler(JWTDecodeError)
async def jwt_decode_exception_handler(request: Request, exc: JWTDecodeError):
    """
    Обработка ошибки декодирования токена.
    """
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'detail': exc.message}
    )

@app.exception_handler(ExternalServiceError)
async def external_service_exception_handler(request: Request, exc: ExternalServiceError):
    """
    Обработка ошибки внешнего сервиса.
    """
    return ORJSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.message}
    )


@app.middleware('http')
async def log_exceptions(request: Request, call_next):
    """
    Middleware для логирования необработанных исключений.
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f'Необработанная ошибка: {e}')
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        logger.error(f'Traceback: {traceback_str}')
        return ORJSONResponse({'detail': 'Internal server error'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


app.include_router(auth.router, prefix=f'/api/{settings.api_version}/auth', tags=['auth'])
app.include_router(places.router, prefix=f'/api/{settings.api_version}/places', tags=['places'])


async def startup():
    logger.info('Приложение запускается...')
    http_module.http_client = httpx.AsyncClient()
    redis_module.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    FastAPICache.init(RedisBackend(redis_module.redis), prefix='fastapi-cache')
    logger.info('Приложение запущено.')


async def shutdown():
    logger.info('Приложение останавливается...')
    if http_module.http_client:
        await http_module.http_client.aclose()
    if redis_module.redis:
        await redis_module.redis.close()
    logger.info('Приложение остановлено.')
