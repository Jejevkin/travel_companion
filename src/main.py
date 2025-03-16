import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

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
)


@app.get('/')
async def root():
    return {'message': 'Welcome to Travel Companion!'}


async def startup():
    logger.info('Приложение запускается...')


async def shutdown():
    logger.info('Приложение останавливается...')
