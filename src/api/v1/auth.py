import logging
from http import HTTPStatus
from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, status, HTTPException

from schemas.users import UserCreate, Token, UserLogin
from services.token import TokenServiceABC, get_token_service
from services.user import UserServiceABC, get_user_service

router = APIRouter()
logger = logging.getLogger(__name__)

AuthorizeDep = Annotated[AuthJWT, Depends()]
TokenServiceDep = Annotated[TokenServiceABC, Depends(get_token_service)]
UserServiceDep = Annotated[UserServiceABC, Depends(get_user_service)]


@router.post(
    '/login',
    status_code=HTTPStatus.OK,
    description='Authenticate user and provide access and refresh tokens',
)
async def login(
        user: UserLogin,
        authorize: AuthorizeDep,
        token_service: TokenServiceDep,
        user_service: UserServiceDep,
) -> Token:
    """
    Аутентифицирует пользователя и выдаёт access и refresh токены.
    """
    authenticated_user = await user_service.authenticate_user(user.login, user.password)
    if authenticated_user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Incorrect username or password')
    access_token, refresh_token = await token_service.create_tokens(str(authenticated_user.id), authorize)
    logger.info(f'Пользователь {user.login} успешно вошел в систему.')
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    '/signup',
    status_code=status.HTTP_201_CREATED,
    description='Register a new user and provide access and refresh tokens',
)
async def signup(
        user: UserCreate,
        authorize: AuthorizeDep,
        token_service: TokenServiceDep,
        user_service: UserServiceDep,
) -> Token:
    """
    Регистрирует нового пользователя и выдаёт access и refresh токены.
    """
    new_user = await user_service.create_user(user)
    if new_user is None:
        raise HTTPException(HTTPStatus.CONFLICT, 'User already exists')
    access_token, refresh_token = await token_service.create_tokens(str(new_user.id), authorize)
    logger.info(f'Пользователь {new_user.login} успешно зарегистрировался.')
    return Token(access_token=access_token, refresh_token=refresh_token)
