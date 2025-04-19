import random
import string
from http import HTTPStatus

import aiohttp
import backoff
import pytest
from aiohttp import ClientError, ServerTimeoutError

from .settings import test_settings


def random_email():
    return ''.join(random.choices(string.ascii_letters, k=8)) + '@test.com'


@pytest.fixture
def make_get_request():
    @backoff.on_exception(backoff.expo, (ClientError, ServerTimeoutError), jitter=backoff.full_jitter, max_tries=5)
    async def inner(url: str, params: dict = None, headers: dict = None, return_content: bool = False):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                status = response.status
                if return_content:
                    body = await response.read()
                else:
                    try:
                        body = await response.json()
                    except aiohttp.ContentTypeError:
                        body = await response.text()
                response_headers = response.headers
        return response_headers, status, body

    return inner


@pytest.fixture
def make_post_request():
    @backoff.on_exception(backoff.expo, (ClientError, ServerTimeoutError), jitter=backoff.full_jitter, max_tries=5)
    async def inner(url: str, json_data: dict = None, headers: dict = None, data=None, params=None):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data, data=data, params=params, headers=headers) as response:
                status = response.status
                try:
                    body = await response.json()
                except aiohttp.ContentTypeError:
                    body = await response.text()
                response_headers = response.headers
        return response_headers, status, body

    return inner


@pytest.fixture
def make_delete_request():
    @backoff.on_exception(backoff.expo, (ClientError, ServerTimeoutError), jitter=backoff.full_jitter, max_tries=5)
    async def inner(url: str, json_data: dict = None, headers: dict = None, data=None, params=None):
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, json=json_data, data=data, params=params, headers=headers) as response:
                status = response.status
                try:
                    body = await response.json()
                except aiohttp.ContentTypeError:
                    body = await response.text()
                response_headers = response.headers
        return response_headers, status, body

    return inner


@pytest.fixture
async def register_user(make_post_request):
    url = f'{test_settings.service_url}/api/v1/auth/signup'
    user_data = {
        'login': random_email(),
        'password': 'TestPassword123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    _, status, body = await make_post_request(url, json_data=user_data)
    assert status == HTTPStatus.CREATED
    return {
        'user_data': user_data,
        'access_token': body['access_token'],
        'refresh_token': body['refresh_token']
    }
