import logging
from abc import ABC
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.database import get_session
from db.redis import get_redis
from models.places import Place, SearchHistory, FavoritePlace
from schemas.places import NearbyPlaceRequest, NearbyPlaceResponse, SearchPlaceRequest, SearchPlaceResponse, \
    FavoritePlaceResponse
from services.base_repository import BaseRepository

logger = logging.getLogger(__name__)
DatabaseDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis)]


class PlaceServiceABC(ABC):
    async def search_places(self, place: SearchPlaceRequest, user_id: UUID | None) -> list[SearchPlaceResponse]:
        pass

    async def get_nearby_places(self, place: NearbyPlaceRequest, user_id: UUID | None) -> list[NearbyPlaceResponse]:
        pass

    async def get_favorite_places(self, user_id: UUID) -> list[FavoritePlaceResponse] | None:
        pass

    async def save_favorite_place(self, place: Place, user_id: UUID) -> FavoritePlaceResponse | None:
        pass

    async def delete_favorite_place(self, place_id: str, user_id: UUID) -> bool:
        pass

    async def get_place_by_id(self, place_id: str) -> Place | None:
        pass


class PlaceService(BaseRepository, PlaceServiceABC):
    def __init__(self, db: AsyncSession, redis: Redis):
        super().__init__(db)
        self.redis = redis
        self.client = httpx.AsyncClient()

    async def search_places(self, place: SearchPlaceRequest, user_id: UUID | None) -> list[SearchPlaceResponse]:
        """
        Выполняет поиск мест по названию.
        """
        params = place.to_params(settings.locationiq_api_key)
        data = await self._fetch_places(settings.LOCATIONIQ_SEARCH_URL, params=params)
        return await self._validate_and_save_places(data, SearchPlaceResponse, user_id)

    async def get_nearby_places(self, place: NearbyPlaceRequest, user_id: UUID | None) -> list[NearbyPlaceResponse]:
        """
        Выполняет поиск ближайших мест по координатам.
        """
        params = place.to_params(settings.locationiq_api_key)
        data = await self._fetch_places(settings.LOCATIONIQ_NEARBY_URL, params=params)
        return await self._validate_and_save_places(data, NearbyPlaceResponse, user_id)

    async def get_favorite_places(self, user_id: UUID) -> list[FavoritePlaceResponse] | None:
        """
        Получает список избранных мест для указанного пользователя.
        """
        favorite_places = await self._execute_query(FavoritePlace, FavoritePlace.user_id == user_id,
                                                    return_first=False)
        logger.info('Пользователь получил список избранных мест.' if favorite_places else 'Список избранных мест пуст.')
        return favorite_places

    async def save_favorite_place(self, place: Place, user_id: UUID) -> FavoritePlaceResponse | None:
        """
        Сохраняет выбранное место в избранное пользователя.
        """
        if saved_favorite := await self._save_entities([FavoritePlace(user_id=user_id, place_id=place.place_id)]):
            logger.info('Место успешно добавлено в избранное.')
            return saved_favorite

        logger.error('Данные уже существуют в избранном.')
        return None

    async def delete_favorite_place(self, place_id: str, user_id: UUID) -> bool:
        """
        Удаляет указанное место из избранного пользователя.
        """
        favorite_place = await self._execute_query(FavoritePlace, FavoritePlace.user_id == user_id,
                                                   FavoritePlace.place_id == place_id, return_first=True)

        if favorite_place:
            return await self._delete_entity(favorite_place)
        logger.warning(f'Не удалось удалить место {place_id} из избранного пользователя {user_id}.')
        return False

    async def get_place_by_id(self, place_id: str) -> Place | None:
        """
        Получает место по ID.
        """
        if place := await self._execute_query(Place, Place.place_id == place_id):
            logger.debug(f'Место с ID \'{place_id}\' найдено.')
            return place

        logger.warning(f'Место с ID \'{place_id}\' не найдено.')
        return None

    async def _fetch_places(self, url: str, params: dict) -> list[dict]:
        """
        Выполняет запрос к API LocationIQ и возвращает данные в формате JSON.
        """
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        logger.info('Запрос к API LocationIQ выполнен успешно.')
        return response.json()

    async def _validate_and_save_places(self, raw_data: list[dict],
                                        model: type[NearbyPlaceResponse | SearchPlaceResponse],
                                        user_id: UUID | None,
                                        ) -> list[SearchPlaceResponse | NearbyPlaceResponse]:
        """
        Валидирует данные, полученные из API, и сохраняет их в базу данных.
        """
        validated_items = [model.model_validate(item) for item in raw_data]

        entities_to_save = []
        for item in validated_items:
            new_place = Place.from_schema(item)
            entities_to_save.append(new_place)

            if user_id:
                history_record = SearchHistory(
                    user_id=user_id,
                    place_id=new_place.place_id,
                )
                entities_to_save.append(history_record)

        if saved_entities := await self._save_entities(entities_to_save):
            logger.info(f'Данные {saved_entities} успешно сохранены в базе данных.')
        return validated_items


def get_place_service(db: DatabaseDep, redis: RedisDep) -> PlaceServiceABC:
    return PlaceService(db, redis)
