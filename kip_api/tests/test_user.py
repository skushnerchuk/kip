import json
import pytest

from django.urls import reverse

ENDPOINTS = [
    ('/api/v1/auth/register/', 'register'),
    ('/api/v1/auth/login/', 'login'),
    ('/api/v1/auth/logout/', 'logout'),
    ('/api/v1/user/', 'user_detail'),
    ('/api/v1/user/update/', 'user_update')
]


@pytest.mark.parametrize(
    'url, reverse_name', [(url, reverse_name) for url, reverse_name in ENDPOINTS]
)
def test_endpoints(client, url, reverse_name):
    print(f'Check endpoint: {url}, {reverse_name}')
    resp = client.options(url)
    # При получении ошибки 401 тоже считаем, что endpoint существует, но требует авторизации
    assert resp.status_code in [200, 401]
    resp = client.options(reverse(reverse_name))
    assert resp.status_code in [200, 401]


@pytest.mark.django_db(transaction=True)
def test_register(correct_register):
    print('Test register')
    assert correct_register.status_code == 201


@pytest.mark.django_db(transaction=True)
def test_login(correct_register, correct_login):
    """
    Проверка тела ответа после авторизации с корректными данными
    Так как база между тестами чистится, также дергаем фикстуру регистрации
    """
    print('Test login')
    access_token = None
    refresh_token = None
    resp_content = json.loads(correct_login.content, encoding='utf8')
    assert correct_login.status_code == 200
    # Проверяем, что пришли непустые токены
    tokens = resp_content.get('tokens')
    if tokens:
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')
    all_ok = tokens and (len(access_token) > 0) and (len(refresh_token) > 0)
    assert all_ok
