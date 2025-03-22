import logging
from abc import ABC, abstractmethod

from async_fastapi_jwt_auth import AuthJWT

logger = logging.getLogger(__name__)


class TokenServiceABC(ABC):
    @abstractmethod
    async def create_tokens(self, user_id: str, authorize: AuthJWT) -> tuple[str, str]:
        pass


class TokenService(TokenServiceABC):
    async def create_tokens(self, user_id: str, authorize: AuthJWT) -> tuple[str, str]:
        """
        Создает access и refresh токены для пользователя.
        """
        access_token = await authorize.create_access_token(subject=user_id)
        refresh_token = await authorize.create_refresh_token(subject=user_id)
        logger.info(f'Токены созданы для пользователя {user_id}.')
        return access_token, refresh_token


def get_token_service() -> TokenServiceABC:
    return TokenService()
