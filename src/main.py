import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth
from core.config import settings
from core.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()


app = FastAPI(
    title=settings.project_name,
    description='Сервис для планировани и управления путешествиями',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(auth.router, prefix=f'/api/{settings.api_version}/auth', tags=['auth'])


async def startup():
    logger.info('Приложение запускается...')


async def shutdown():
    logger.info('Приложение останавливается...')
