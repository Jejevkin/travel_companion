from http import HTTPStatus

import pytest

from ..settings import test_settings


@pytest.mark.asyncio
async def test_search_places_unauthorized(make_get_request):
    """
    Неавторизованный пользователь пытается найти место по названию.
    """
    query_params = {
        'query': 'Красная площадь',
        'limit': 5
    }
    url = f'{test_settings.service_url}/api/v1/places/search'

    _, status, body = await make_get_request(url, params=query_params)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.asyncio
async def test_search_places_authorized(register_user, make_get_request):
    """
    Авторизованный пользователь пытается найти место по названию.
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    query_params = {
        "query": "Berlin",
        "limit": 5
    }
    url = f'{test_settings.service_url}/api/v1/places/search'

    _, status, body = await make_get_request(url, params=query_params, headers=headers)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.asyncio
async def test_nearby_places_unauthorized(make_get_request):
    """
    Неавторизованный пользователь пытается найти ближайшие места по координатам.
    """
    url = f'{test_settings.service_url}/api/v1/places/nearby'
    query_params = {
        'lat': 55.7558,
        'lon': 37.6173,
        'tags': 'restaurant',
        'radius': 500,
        'limit': 5
    }
    _, status, body = await make_get_request(url, params=query_params)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.asyncio
async def test_nearby_places_authorized(register_user, make_get_request):
    """
    Авторизованный пользователь пытается найти ближайшие места по координатам.
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    url = f'{test_settings.service_url}/api/v1/places/nearby'
    query_params = {
        'lat': 40.7128,
        'lon': -74.0060,
        'tags': 'aeroway:aerodrome,tourism:hotel,amenity:parking',
        'radius': 1000,
        'limit': 10
    }
    _, status, body = await make_get_request(url, params=query_params, headers=headers)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.asyncio
async def test_get_favorite_places_unauthorized(make_get_request):
    """
    Неавторизованный пользователь пытается получить список избранных мест
    """
    url = f'{test_settings.service_url}/api/v1/places/favorite'
    _, status, body = await make_get_request(url)
    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in body


@pytest.mark.asyncio
async def test_get_favorite_places_authorized_no_data(register_user, make_post_request, make_get_request):
    """
    Авторизованный пользователь пытается получить список избранных мест.
    Данных нет, вернет пустой список.
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    url = f'{test_settings.service_url}/api/v1/places/favorite'
    _, status, body = await make_get_request(url, headers=headers)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) == 0


@pytest.mark.asyncio
async def test_get_favorite_places_authorized_with_data(register_user, make_post_request, make_get_request):
    """
    Авторизованный пользователь пытается получить список избранных мест.
    Данные есть.
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Ищем место
    query_params = {
        'query': 'Красная площадь',
        'limit': 5
    }
    search_url = f'{test_settings.service_url}/api/v1/places/search'

    _, status, body = await make_get_request(search_url, params=query_params)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0

    place_id_to_favorite = body[0]['place_id']

    # Добавляем место в избранное
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'
    place_data = {'place_id': place_id_to_favorite}
    _, post_status, post_body = await make_post_request(favorite_url, json_data=place_data, headers=headers)
    assert post_status == HTTPStatus.CREATED

    # Получаем список избранных мест
    _, get_status, get_body = await make_get_request(favorite_url, headers=headers)
    assert get_status == HTTPStatus.OK
    assert isinstance(get_body, list)

    # Ищем в списке добавленное место
    favorite_place_ids = [favorite['place_id'] for favorite in get_body]
    assert place_id_to_favorite in favorite_place_ids, 'Добавленного place_id нет в списке избранного'


@pytest.mark.asyncio
async def test_add_favorite_place_unauthorized(make_post_request):
    """
    Неавторизованный пользователь пытается добавить место в избранное.
    """
    url = f'{test_settings.service_url}/api/v1/places/favorite'
    place_data = {'place_id': 'test_place_id'}
    _, status, body = await make_post_request(url, json_data=place_data)
    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in body


@pytest.mark.asyncio
async def test_add_favorite_place_authorized(register_user, make_post_request, make_get_request):
    """
    Авторизованный пользователь добавляет место в избранное с валидным токеном.
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Ищем место
    query_params = {
        'query': 'Красная площадь',
        'limit': 5
    }
    search_url = f'{test_settings.service_url}/api/v1/places/search'

    _, status, body = await make_get_request(search_url, params=query_params)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0

    place_id_to_favorite = body[0]['place_id']

    # Добавляем место в избранное
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'
    place_data = {'place_id': place_id_to_favorite}
    _, post_status, post_body = await make_post_request(favorite_url, json_data=place_data, headers=headers)
    assert post_status == HTTPStatus.CREATED
    assert 'id' in post_body
    assert 'user_id' in post_body
    assert 'place_id' in post_body and post_body['place_id'] == place_id_to_favorite
    assert 'created_at' in post_body


@pytest.mark.asyncio
async def test_add_favorite_place_authorized_twice(register_user, make_post_request, make_get_request):
    """
    Попытка добавить дважды место в избранное с валидным токеном.
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Ищем место
    query_params = {
        'query': 'Красная площадь',
        'limit': 5
    }
    search_url = f'{test_settings.service_url}/api/v1/places/search'

    _, status, body = await make_get_request(search_url, params=query_params)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0

    place_id_to_favorite = body[0]['place_id']

    # Добавляем место в избранное
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'
    place_data = {'place_id': place_id_to_favorite}
    _, post_status, post_body = await make_post_request(favorite_url, json_data=place_data, headers=headers)
    assert post_status == HTTPStatus.CREATED
    assert 'id' in post_body
    assert 'user_id' in post_body
    assert 'place_id' in post_body and post_body['place_id'] == place_id_to_favorite
    assert 'created_at' in post_body

    # Повторно добавляем место в избранное
    _, post_status, post_body = await make_post_request(favorite_url, json_data=place_data, headers=headers)
    assert post_status == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_add_favorite_place_authorized_with_wrong_place_id(register_user, make_post_request):
    """
    Добавляем место в избранное с несуществующим id.
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Добавляем место в избранное
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'
    place_data = {'place_id': 'wrong_place_id'}
    _, post_status, post_body = await make_post_request(favorite_url, json_data=place_data, headers=headers)
    assert post_status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_favorite_place_unauthorized(make_delete_request):
    """
    Неавторизованный пользователь пытается удалить место из избранного.
    """
    place_id = 'some_random_place_id'
    url = f'{test_settings.service_url}/api/v1/places/favorite/{place_id}'
    _, status, body = await make_delete_request(url)
    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in body


@pytest.mark.asyncio
async def test_delete_favorite_place_authorized(register_user, make_post_request, make_get_request,
                                                make_delete_request):
    """
    Авторизованный пользователь удаляет место из избранного.
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Ищем место
    search_url = f'{test_settings.service_url}/api/v1/places/search'
    query_params = {'query': 'Красная площадь', 'limit': 5}
    _, search_status, search_body = await make_get_request(search_url, params=query_params, headers=headers)
    assert search_status == HTTPStatus.OK
    assert isinstance(search_body, list)
    assert len(search_body) > 0

    place_id_to_favorite = search_body[0]['place_id']

    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'
    place_data = {'place_id': place_id_to_favorite}
    _, post_status, post_body = await make_post_request(favorite_url, json_data=place_data, headers=headers)
    assert post_status == HTTPStatus.CREATED

    # Проверяем, что место находится в избранном
    _, get_status, get_body = await make_get_request(favorite_url, headers=headers)
    assert get_status == HTTPStatus.OK
    favorite_place_ids = [favorite['place_id'] for favorite in get_body]
    assert place_id_to_favorite in favorite_place_ids

    # Удаляем место
    delete_url = f'{test_settings.service_url}/api/v1/places/favorite/{place_id_to_favorite}'
    _, del_status, del_body = await make_delete_request(delete_url, headers=headers)
    assert del_status == HTTPStatus.OK

    # Проверяем, что место отсутствует в списке избранных
    _, new_get_status, new_get_body = await make_get_request(favorite_url, headers=headers)
    assert new_get_status == HTTPStatus.OK
    new_favorite_place_ids = [favorite['place_id'] for favorite in new_get_body]
    assert place_id_to_favorite not in new_favorite_place_ids


@pytest.mark.asyncio
async def test_delete_favorite_place_authorized_wrong_id(register_user, make_post_request, make_get_request,
                                                         make_delete_request):
    """
    Авторизованный пользователь пытается удалить место, которого нет в избранном (или вовсе не существует).
    """
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Попробуем удалить 'some_non_existing_id'
    wrong_place_id = 'some_non_existing_id'
    url = f'{test_settings.service_url}/api/v1/places/favorite/{wrong_place_id}'
    _, del_status, del_body = await make_delete_request(url, headers=headers)
    assert del_status == HTTPStatus.NOT_FOUND
    assert 'detail' in del_body
