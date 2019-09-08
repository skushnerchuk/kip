import json
import pytest

from django.urls import reverse
from django.test.client import Client
from rest_framework.response import Response

from kip_api.models import User
from .types_for_test import ApiResponse


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
def test_endpoints(client: Client, url: str, reverse_name: str) -> None:
    """
    Тестирование доступности точек API
    """
    resp = client.options(url)
    # При получении ошибки 401 тоже считаем, что endpoint существует, но требует авторизации
    assert resp.status_code in [200, 401]
    resp = client.options(reverse(reverse_name))
    assert resp.status_code in [200, 401]


@pytest.mark.django_db(transaction=True)
def test_register(correct_register: ApiResponse) -> None:
    """
    Проверка регистрации
    """
    email, response = correct_register
    assert response.status_code == 201
    user = User.objects.get(email=email)
    assert user.email == email


@pytest.mark.django_db(transaction=True)
def test_incorrect_register(incorrect_register: Response) -> None:
    """
    Проверка регистрации с неправильными данными
    """
    assert incorrect_register.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_login(correct_login: ApiResponse) -> None:
    """
    Проверка тела ответа после авторизации с корректными данными
    """
    email, response = correct_login
    access_token = None
    refresh_token = None
    assert response.status_code == 200
    resp_content = json.loads(response.content, encoding='utf8')
    # Проверяем, что пришли непустые токены
    tokens = resp_content.get('tokens')
    if tokens:
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')
    all_ok = tokens and (len(access_token) > 0) and (len(refresh_token) > 0)
    assert all_ok
