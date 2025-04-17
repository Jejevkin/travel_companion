import logging
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache

from core.common import request_key_builder
from core.config import settings
from schemas.places import (
    NearbyPlaceRequest,
    NearbyPlaceResponse,
    SearchPlaceRequest,
    SearchPlaceResponse,
    FavoritePlaceCreate,
    FavoritePlaceResponse
)
from services.place import PlaceServiceABC, get_place_service

router = APIRouter()
logger = logging.getLogger(__name__)

AuthorizeDep = Annotated[AuthJWT, Depends(AuthJWTBearer())]
PlaceServiceDep = Annotated[PlaceServiceABC, Depends(get_place_service)]


@router.get('/search',
            status_code=HTTPStatus.OK,
            description='Search places', )
@cache(expire=settings.redis_ttl, key_builder=request_key_builder)
async def search_places(
        place_query: Annotated[SearchPlaceRequest, Query()],
        authorize: AuthorizeDep,
        place_service: PlaceServiceDep,
) -> list[SearchPlaceResponse]:
    """
    Эндпоинт для поиска мест по названию.
    """
    await authorize.jwt_optional()
    user_id = await authorize.get_jwt_subject()
    user_uuid = UUID(user_id) if user_id else None
    if places := await place_service.search_places(place_query, user_uuid):
        logger.info(f'Пользователь {user_id} получил список мест.')
        return places
    raise HTTPException(HTTPStatus.NOT_FOUND, 'Places not found')


@router.get('/nearby',
            status_code=HTTPStatus.OK,
            description='Getting a list of places by coordinates', )
@cache(expire=settings.redis_ttl, key_builder=request_key_builder)
async def get_nearby_places(
        place: Annotated[NearbyPlaceRequest, Query()],
        authorize: AuthorizeDep,
        place_service: PlaceServiceDep,
) -> list[NearbyPlaceResponse]:
    """
    Эндпоинт для поиска ближайших мест по координатам.
    """
    await authorize.jwt_optional()
    user_id = await authorize.get_jwt_subject()
    user_uuid = UUID(user_id) if user_id else None
    if nearby_places := await place_service.get_nearby_places(place, user_uuid):
        logger.info(f'Пользователь {user_id} получил список ближайших мест.')
        return nearby_places
    raise HTTPException(HTTPStatus.NOT_FOUND, 'Places not found')


@router.get('/favorite',
            status_code=HTTPStatus.OK,
            description='Get favorite places', )
async def get_favorite_places(
        authorize: AuthorizeDep,
        place_service: PlaceServiceDep,
) -> list[FavoritePlaceResponse]:
    """
    Эндпоинт для получения списка избранных мест.
    """
    await authorize.jwt_required()
    user_id = await authorize.get_jwt_subject()
    favorite_places = await place_service.get_favorite_places(UUID(user_id))
    logger.info(f'Пользователь {user_id} получил список избранных мест (кол-во: {len(favorite_places)}).')
    return favorite_places


@router.post('/favorite',
             status_code=HTTPStatus.CREATED,
             description='Save favorite place', )
async def save_favorite_place(
        favorite_place: FavoritePlaceCreate,
        authorize: AuthorizeDep,
        place_service: PlaceServiceDep,
) -> FavoritePlaceResponse:
    """
    Эндпоинт для сохранения места в избранное.
    """
    await authorize.jwt_required()
    user_id = await authorize.get_jwt_subject()
    place = await place_service.get_place_by_id(favorite_place.place_id)

    if not place:
        logger.warning(f'Место с ID \'{favorite_place.place_id}\' не найдено.')
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Place not found')

    if favorite_place := await place_service.save_favorite_place(place, UUID(user_id)):
        logger.info(f'Пользователь {user_id} добавил место {place.place_id} в избранное.')
        return favorite_place
    raise HTTPException(HTTPStatus.CONFLICT, 'Favorite place already exists')


@router.delete('/favorite/{place_id}',
               status_code=HTTPStatus.OK,
               description='Delete favorite place', )
async def delete_favorite_place(
        place_id: str,
        authorize: AuthorizeDep,
        place_service: PlaceServiceDep,
) -> None:
    """
    Эндпоинт для удаления места из избранного.
    """
    await authorize.jwt_required()
    user_id = await authorize.get_jwt_subject()
    deleted = await place_service.delete_favorite_place(place_id, UUID(user_id))
    if deleted:
        logger.info(f'Пользователь {user_id} удалил место {place_id} из избранного.')
        return
    raise HTTPException(HTTPStatus.NOT_FOUND, 'Favorite place not found')
