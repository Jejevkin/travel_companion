from http import HTTPStatus

import pytest

from ..conftest import random_email
from ..settings import test_settings


@pytest.mark.parametrize(
    'user_data, expected_status, expected_detail',
    [
        (
                {
                    'login': random_email(),
                    'password': 'TestPassword123',
                    'first_name': 'Test',
                    'last_name': 'User'
                },
                HTTPStatus.CREATED,
                None
        ),
        (
                {
                    'login': 'invalid_email',
                    'password': 'TestPassword123',
                    'first_name': 'Test',
                    'last_name': 'User'
                },
                HTTPStatus.UNPROCESSABLE_ENTITY,
                'value_error'
        ),
    ]
)
@pytest.mark.asyncio
async def test_signup(make_post_request, user_data, expected_status, expected_detail):
    url = f'{test_settings.service_url}/api/v1/auth/signup'
    headers, status, body = await make_post_request(url, json_data=user_data)
    assert status == expected_status
    if status == HTTPStatus.CREATED:
        assert 'access_token' in body
        assert 'refresh_token' in body
    else:
        assert expected_detail in str(body['detail'])


@pytest.mark.asyncio
async def test_login_success(make_post_request, register_user):
    user_info = await register_user
    user_data = user_info['user_data']
    url_login = f'{test_settings.service_url}/api/v1/auth/login'
    login_data = {
        'login': user_data['login'],
        'password': user_data['password']
    }
    headers, status, body = await make_post_request(url_login, json_data=login_data)
    assert status == HTTPStatus.OK
    assert 'access_token' in body
    assert 'refresh_token' in body
