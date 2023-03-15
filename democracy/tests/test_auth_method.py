import pytest

from democracy.tests.utils import get_data_from_response


list_url = '/v1/auth_method/'

def get_detail_url(auth_method):
    return list_url + str(auth_method.pk) + '/'


@pytest.mark.django_db
@pytest.mark.parametrize('client', [
    'api_client',
    'jane_doe_api_client',
    'admin_api_client'
])
def test_get_auth_methods_list(client, request, auth_method_library_card, auth_method_test_auth):
    """
    Tests that auth methods can be fetched via list endpoint by anyone
    """
    api_client = request.getfixturevalue(client)
    response = api_client.get(list_url)
    data = get_data_from_response(response)
    ids = [auth_method['id'] for auth_method in data['results']]
    assert auth_method_library_card.id in ids
    assert auth_method_test_auth.id in ids


@pytest.mark.django_db
@pytest.mark.parametrize('client, expected', [
    ('api_client', 401),
    ('jane_doe_api_client', 403),
    ('admin_api_client', 405)
])
def test_post_auth_methods_list(client, expected, request):
    """
    Tests that auth methods cannot be created via list endpoint by anyone
    """
    api_client = request.getfixturevalue(client)
    data = {'name': 'test', 'amr': 'some_amr'}
    response = api_client.post(list_url, data)
    assert response.status_code == expected


@pytest.mark.django_db
@pytest.mark.parametrize('client', [
    'api_client',
    'jane_doe_api_client',
    'admin_api_client'
])
def test_get_auth_method_detail(client, request, auth_method_library_card):
    """
    Tests that an auth method can be fetched via detail endpoint by anyone
    """
    api_client = request.getfixturevalue(client)
    response = api_client.get(get_detail_url(auth_method_library_card))
    data = get_data_from_response(response)
    assert auth_method_library_card.id == data.get('id')


@pytest.mark.django_db
@pytest.mark.parametrize('client, expected', [
    ('api_client', 401),
    ('jane_doe_api_client', 403),
    ('admin_api_client', 405)
])
def test_update_auth_method_detail(client, expected, request, auth_method_library_card):
    """
    Tests that auth methods cannot be updated via detail endpoint by anyone
    """
    api_client = request.getfixturevalue(client)
    data = {'name': 'test', 'amr': 'some_amr'}
    response = api_client.put(get_detail_url(auth_method_library_card), data)
    assert response.status_code == expected


@pytest.mark.django_db
@pytest.mark.parametrize('client, expected', [
    ('api_client', 401),
    ('jane_doe_api_client', 403),
    ('admin_api_client', 405)
])
def test_delete_auth_method_detail(client, expected, request, auth_method_library_card):
    """
    Tests that auth methods cannot be deleted via detail endpoint by anyone
    """
    api_client = request.getfixturevalue(client)
    response = api_client.delete(get_detail_url(auth_method_library_card))
    assert response.status_code == expected
