import logging

import jwt
from fastapi import Request

from core.config import settings

logger = logging.getLogger(__name__)


async def request_key_builder(
        func,
        namespace: str,
        request: Request,
        *args,
        **kwargs
) -> str:
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = 'anonymous'
    if token:
        try:
            decoded_token = jwt.decode(token, settings.authjwt_secret_key, algorithms=[settings.authjwt_algorithm])
            user_id = decoded_token.get('sub', 'anonymous')
        except jwt.PyJWTError:
            logger.error('Невалидный токен.')

    cache_key = ':'.join([
        namespace,
        user_id,
        request.method.lower(),
        request.url.path,
        repr(sorted(request.query_params.items()))
    ])
    return cache_key
