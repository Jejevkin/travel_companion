import logging
from abc import ABC

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

    async def _save_entity(self, entity):
        """
        Сохраняет сущность в базу данных.
        """
        self.db.add(entity)
        try:
            await self.db.commit()
            await self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f'Ошибка при сохранении в базу данных: {e}')
            return None
