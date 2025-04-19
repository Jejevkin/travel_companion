from http import HTTPStatus

import pytest

from ..settings import test_settings


@pytest.mark.asyncio
async def test_search_places_unauthorized(make_get_request):
    """
    Неавторизованный пользователь пытается найти место по названию.
    """
    # Arrange
    query_params = {'query': 'Красная площадь', 'limit': 5}
    url = f'{test_settings.service_url}/api/v1/places/search'

    # Act
    _, status, body = await make_get_request(url, params=query_params)

    # Assert
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.asyncio
async def test_search_places_authorized(register_user, make_get_request):
    """
    Авторизованный пользователь пытается найти место по названию.
    """
    # Arrange
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    query_params = {'query': 'Berlin', 'limit': 5}
    url = f'{test_settings.service_url}/api/v1/places/search'

    # Act
    _, status, body = await make_get_request(url, params=query_params, headers=headers)

    # Assert
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.asyncio
async def test_nearby_places_unauthorized(make_get_request):
    """
    Неавторизованный пользователь пытается найти ближайшие места по координатам.
    """
    # Arrange
    url = f'{test_settings.service_url}/api/v1/places/nearby'
    query_params = {
        'lat': 55.7558,
        'lon': 37.6173,
        'tags': 'restaurant',
        'radius': 500,
        'limit': 5
    }

    # Act
    _, status, body = await make_get_request(url, params=query_params)

    # Assert
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.asyncio
async def test_nearby_places_authorized(register_user, make_get_request):
    """
    Авторизованный пользователь пытается найти ближайшие места по координатам.
    """
    # Arrange
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

    # Act
    _, status, body = await make_get_request(url, params=query_params, headers=headers)

    # Assert
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.asyncio
async def test_get_favorite_places_unauthorized(make_get_request):
    """
    Неавторизованный пользователь пытается получить список избранных мест
    """
    # Arrange
    url = f'{test_settings.service_url}/api/v1/places/favorite'

    # Act
    _, status, body = await make_get_request(url)

    # Assert
    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in body


@pytest.mark.asyncio
async def test_get_favorite_places_authorized_no_data(register_user, make_post_request, make_get_request):
    """
    Авторизованный пользователь пытается получить список избранных мест.
    Данных нет, вернет пустой список.
    """
    # Arrange
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'{test_settings.service_url}/api/v1/places/favorite'

    # Act
    _, status, body = await make_get_request(url, headers=headers)

    # Assert
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) == 0


@pytest.mark.asyncio
async def test_get_favorite_places_authorized_with_data(register_user, make_post_request, make_get_request):
    """
    Авторизованный пользователь пытается получить список избранных мест.
    Данные есть.
    """
    # Arrange
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    query_params = {'query': 'Красная площадь', 'limit': 5}
    search_url = f'{test_settings.service_url}/api/v1/places/search'
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'

    # Act: поиск места
    _, search_status, search_body = await make_get_request(search_url, params=query_params)
    place_id = search_body[0]['place_id']

    # Act: добавление в избранное
    _, post_status, _ = await make_post_request(
        favorite_url,
        json_data={'place_id': place_id},
        headers=headers,
    )

    # Act: получение списка избранного
    _, get_status, get_body = await make_get_request(favorite_url, headers=headers)

    # Assert: результаты поиска корректны
    assert search_status == HTTPStatus.OK
    assert isinstance(search_body, list) and search_body

    # Assert: место успешно добавлено
    assert post_status == HTTPStatus.CREATED

    # Assert: список избранного содержит добавленное место
    assert get_status == HTTPStatus.OK
    assert isinstance(get_body, list)
    favorite_ids = [item['place_id'] for item in get_body]
    assert place_id in favorite_ids, f'Добавленного place_id {place_id} нет в списке избранного'


@pytest.mark.asyncio
async def test_add_favorite_place_unauthorized(make_post_request):
    """
    Неавторизованный пользователь пытается добавить место в избранное.
    """
    # Arrange
    url = f'{test_settings.service_url}/api/v1/places/favorite'
    place_data = {'place_id': 'test_place_id'}

    # Act
    _, status, body = await make_post_request(url, json_data=place_data)

    # Assert
    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in body


@pytest.mark.asyncio
async def test_add_favorite_place_authorized(register_user, make_post_request, make_get_request):
    """
    Авторизованный пользователь добавляет место в избранное с валидным токеном.
    """
    # Arrange
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    query_params = {'query': 'Красная площадь', 'limit': 5}
    search_url = f'{test_settings.service_url}/api/v1/places/search'
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'

    # Act: поиск места
    _, search_status, search_body = await make_get_request(search_url, params=query_params)
    place_id = search_body[0]['place_id']

    # Act: добавление в избранное
    _, post_status, post_body = await make_post_request(
        favorite_url,
        json_data={'place_id': place_id},
        headers=headers,
    )

    # Assert: результаты поиска корректны
    assert search_status == HTTPStatus.OK
    assert isinstance(search_body, list) and search_body

    # Assert: место успешно добавлено
    assert post_status == HTTPStatus.CREATED
    assert post_status == HTTPStatus.CREATED
    assert 'id' in post_body
    assert 'user_id' in post_body
    assert 'place_id' in post_body and post_body['place_id'] == place_id
    assert 'created_at' in post_body


@pytest.mark.asyncio
async def test_add_favorite_place_authorized_twice(register_user, make_post_request, make_get_request):
    """
    Попытка добавить дважды место в избранное с валидным токеном.
    """
    # Arrange
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    query_params = {'query': 'Красная площадь', 'limit': 5}
    search_url = f'{test_settings.service_url}/api/v1/places/search'
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'

    # Act: поиск места
    _, search_status, search_body = await make_get_request(search_url, params=query_params)
    place_id = search_body[0]['place_id']

    # Act: добавление в избранное
    _, post_status, post_body = await make_post_request(
        favorite_url,
        json_data={'place_id': place_id},
        headers=headers,
    )

    # Act: повторное добавление в избранное
    _, post_status_2, post_body_2 = await make_post_request(
        favorite_url,
        json_data={'place_id': place_id},
        headers=headers,
    )

    # Assert: результаты поиска корректны
    assert search_status == HTTPStatus.OK
    assert isinstance(search_body, list) and search_body

    # Assert: место успешно добавлено
    assert post_status == HTTPStatus.CREATED
    assert post_status == HTTPStatus.CREATED
    assert 'id' in post_body
    assert 'user_id' in post_body
    assert 'place_id' in post_body and post_body['place_id'] == place_id
    assert 'created_at' in post_body

    # Assert: место уже добавлено
    assert post_status_2 == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_add_favorite_place_authorized_with_wrong_place_id(register_user, make_post_request):
    """
    Добавляем место в избранное с несуществующим id.
    """
    # Arrange
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'
    place_data = {'place_id': 'wrong_place_id'}

    # Act
    _, post_status, post_body = await make_post_request(favorite_url, json_data=place_data, headers=headers)

    # Assert
    assert post_status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_favorite_place_unauthorized(make_delete_request):
    """
    Неавторизованный пользователь пытается удалить место из избранного.
    """
    # Arrange
    place_id = 'some_random_place_id'
    url = f'{test_settings.service_url}/api/v1/places/favorite/{place_id}'

    # Act
    _, status, body = await make_delete_request(url)

    # Assert
    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in body


@pytest.mark.asyncio
async def test_delete_favorite_place_authorized(register_user, make_post_request, make_get_request,
                                                make_delete_request):
    """
    Авторизованный пользователь удаляет место из избранного.
    """
    # Arrange
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    query_params = {'query': 'Красная площадь', 'limit': 5}
    search_url = f'{test_settings.service_url}/api/v1/places/search'
    favorite_url = f'{test_settings.service_url}/api/v1/places/favorite'

    # Act: поиск места
    _, search_status, search_body = await make_get_request(search_url, params=query_params)
    place_id = search_body[0]['place_id']

    # Act: добавление в избранное
    _, post_status, _ = await make_post_request(
        favorite_url,
        json_data={'place_id': place_id},
        headers=headers,
    )

    # Act: получение списка избранного
    _, get_status, get_body = await make_get_request(favorite_url, headers=headers)

    # Act: удаление места из избранного
    _, delete_status, _ = await make_delete_request(f'{favorite_url}/{place_id}', headers=headers)

    # Act: проверяем, что место отсутствует в списке избранных
    _, get_status_2, get_body_2 = await make_get_request(favorite_url, headers=headers)

    # Assert: результаты поиска корректны
    assert search_status == HTTPStatus.OK
    assert isinstance(search_body, list) and search_body

    # Assert: место успешно добавлено
    assert post_status == HTTPStatus.CREATED

    # Assert: список избранного содержит добавленное место
    assert get_status == HTTPStatus.OK
    assert isinstance(get_body, list)
    favorite_ids = [item['place_id'] for item in get_body]
    assert place_id in favorite_ids, f'Добавленного place_id {place_id} нет в списке избранного'

    # Assert: место успешно удалено
    assert delete_status == HTTPStatus.OK

    # Assert: список избранного не содержит удаленное место
    assert get_status_2 == HTTPStatus.OK
    assert isinstance(get_body_2, list)
    favorite_ids = [item['place_id'] for item in get_body_2]
    assert place_id not in favorite_ids, f'Удаленный place_id {place_id} найден в списке избранного'


@pytest.mark.asyncio
async def test_delete_favorite_place_authorized_wrong_id(register_user, make_post_request, make_get_request,
                                                         make_delete_request):
    """
    Авторизованный пользователь пытается удалить место, которого нет в избранном (или вовсе не существует).
    """
    # Arrange
    user_info = await register_user
    access_token = user_info['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    wrong_place_id = 'some_non_existing_id'
    url = f'{test_settings.service_url}/api/v1/places/favorite/{wrong_place_id}'

    # Act
    _, del_status, del_body = await make_delete_request(url, headers=headers)

    # Assert
    assert del_status == HTTPStatus.NOT_FOUND
    assert 'detail' in del_body
