import logging
from abc import ABC
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _execute_query(self, model, *filters, return_first=True, offset=0, limit=100):
        """
        Выполняет запрос к базе данных с заданными фильтрами.
        """
        query = select(model).filter(*filters).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().first() if return_first else result.scalars().all()

    async def _save_entities(self, entities):
        """
        Сохраняет сущности в базу данных.
        """
        entities = entities if isinstance(entities, list) else [entities]
        self.db.add_all(entities)
        try:
            await self.db.commit()
            for entity in entities:
                await self.db.refresh(entity)
            return entities[0] if len(entities) == 1 else entities

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f'Ошибка при сохранении в базу данных: {e}')
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Entity already exists')
        except Exception as e:
            await self.db.rollback()
            logger.error(f'Неизвестная ошибка при сохранении в базу данных: {e}')
            return None

    async def _delete_entity(self, entity):
        """
        Удаляет сущность в базу данных.
        """
        await self.db.delete(entity)
        try:
            await self.db.commit()
            return True
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f'Ошибка при удалении из базы данных: {e}')
            return False
