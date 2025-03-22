import logging
from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from models.users import User
from schemas.users import UserCreate
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)
DatabaseDep = Annotated[AsyncSession, Depends(get_session)]


class UserServiceABC(ABC):
    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> User | None:
        pass

    @abstractmethod
    async def create_user(self, user: UserCreate) -> User | None:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> User | None:
        pass


class UserService(BaseRepository, UserServiceABC):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def authenticate_user(self, username: str, password: str) -> User | None:
        """
        Аутентифицирует пользователя по имени пользователя и паролю.
        """
        if (user := await self._execute_query(User, User.login == username)) and user.check_password(password):
            logger.info(f'Пользователь \'{username}\' успешно вошел в систему.')
            return user

        logger.warning(f'Неудачная попытка аутентификации для пользователя \'{username}\'.')
        return None

    async def create_user(self, user_data: UserCreate) -> User | None:
        """
        Создает нового пользователя.
        """
        new_user = User.from_schema(user_data)
        if saved_user := await self._save_entity(new_user):
            logger.info(f'Пользователь \'{new_user.login}\' успешно создан.')
            return saved_user

        logger.error(f'Не удалось создать пользователя \'{new_user.login}\'.')
        return None

    async def get_user_by_id(self, user_id: str) -> User | None:
        """
        Получает пользователя по ID.
        """
        if user := await self._execute_query(User, User.id == user_id):
            logger.debug(f'Пользователь с ID \'{user_id}\' найден.')
            return user

        logger.warning(f'Пользователь с ID \'{user_id}\' не найден.')
        return None


def get_user_service(db: DatabaseDep) -> UserServiceABC:
    return UserService(db)
