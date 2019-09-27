import json
import re
import os
from typing import Dict, Any, Optional, Callable

import pytest
from django.conf import settings
from django.core import mail
from django.test.client import Client
from django.urls import reverse
from rest_framework import status

from kip_api.models import User
from kip_api.tests.types_for_test import (
    ENDPOINTS, CORRECT_LOGIN_BODY, INCORRECT_REGISTER_BODY,
    UPDATE_PROFILE_BODY, UPLOAD_AVATAR_HEADERS, INCORRECT_UPLOAD_AVATAR_HEADERS
)
from kip_api.utils import generate_dump

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kip.settings")

EmailResponse = Optional[mail.EmailMessage]


def find_email_in_outbox(recipient: str) -> EmailResponse:
    """Поиск письма в тестовом ящике"""
    for m in mail.outbox:
        if recipient in m.to:
            return m
    return None


@pytest.mark.parametrize(
    'url, reverse_name', [(url, reverse_name) for url, reverse_name in ENDPOINTS]
)
def test_endpoints(client: Client, url: str, reverse_name: str) -> None:
    """Тестирование доступности точек API"""
    resp = client.options(url)
    # При получении ошибки 401 тоже считаем, что endpoint существует, но требует авторизации
    assert resp.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
    resp = client.options(reverse(reverse_name))
    assert resp.status_code in [200, 401]


def test_registration(client: Client) -> None:
    """Проверка регистрации"""
    body = CORRECT_LOGIN_BODY
    response = client.post('/api/v1/auth/register/', data=body, content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(email=body['email'])
    assert user.email == body['email']


def test_double_registration(client: Client, correct_login: Dict) -> None:
    """Проверка регистрации с уже существующей почтой"""
    user = User.objects.get(email=correct_login['email'])
    assert user.email == correct_login['email']
    response = client.post('/api/v1/auth/register/', data=correct_login, content_type='application/json')
    response_body = json.loads(response.content, encoding='utf-8')
    assert (response.status_code == status.HTTP_400_BAD_REQUEST) and \
           (response_body['status'] == 'error') and \
           (correct_login['email'] in response_body['message'])


@pytest.mark.parametrize(
    'body', [body for body in INCORRECT_REGISTER_BODY]
)
def test_incorrect_register(client: Client, body: Any) -> None:
    """Проверка регистрации с неправильными данными"""
    response = client.post('/api/v1/auth/register/', data=body, content_type='application/json')
    response_body = json.loads(response.content, encoding='utf-8')
    assert (response.status_code == status.HTTP_400_BAD_REQUEST) and \
           (response_body['status'] == 'error')


def test_login(client: Client, correct_login: Dict) -> None:
    """Проверка тела ответа после авторизации с корректными данными"""
    response = client.post('/api/v1/auth/login/', data=correct_login, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    resp_content = json.loads(response.content, encoding='utf8')
    # Проверяем, что пришли непустые токены
    tokens = resp_content.get('tokens')
    access_token = None
    refresh_token = None
    if tokens:
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')
    all_ok = tokens and (len(access_token) > 0) and (len(refresh_token) > 0)
    assert all_ok


def test_profile_update(client: Client, correct_login: Dict) -> None:
    """Проверка обновления профиля пользователя"""
    response = client.post('/api/v1/auth/login/', data=correct_login, content_type='application/json')
    response_body = json.loads(response.content, encoding='utf-8')
    token = response_body['tokens']['access']
    response = client.put(
        '/api/v1/user/update/',
        data=UPDATE_PROFILE_BODY,
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = json.loads(response.content, encoding='utf8')
    assert response_body['status'] == 'ok'
    profile = response_body['user_detail']['profile']
    assert profile['first_name'] == UPDATE_PROFILE_BODY['first_name']
    assert profile['middle_name'] == UPDATE_PROFILE_BODY['middle_name']
    assert profile['last_name'] == UPDATE_PROFILE_BODY['last_name']
    assert profile['birth_date'] == UPDATE_PROFILE_BODY['birth_date']
    assert profile['biography'] == UPDATE_PROFILE_BODY['biography']


def test_profile_update_with_incorrect_token(client: Client, correct_login: Dict) -> None:
    """Проверка обновления профиля пользователя с неверным токеном"""
    client.post('/api/v1/auth/login/', data=correct_login, content_type='application/json')
    response = client.put(
        '/api/v1/user/update/',
        data=UPDATE_PROFILE_BODY,
        content_type='application/json',
        HTTP_AUTHORIZATION='Bearer 1234567890'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response_body = json.loads(response.content, encoding='utf8')
    assert response_body['status'] == 'error'


def test_view_user_detail_with_correct_token(client: Client, correct_login: Dict) -> None:
    """Проверка просмотра сведений о пользователе"""
    response = client.post('/api/v1/auth/login/', data=correct_login, content_type='application/json')
    response_body = json.loads(response.content, encoding='utf-8')
    token = response_body['tokens']['access']
    response = client.get('/api/v1/user/', HTTP_AUTHORIZATION=f'Bearer {token}')
    response_body = json.loads(response.content, encoding='utf8')
    assert response.status_code, status.HTTP_200_OK
    assert (response_body['status'] == 'ok') and ('user_detail' in response_body)


def test_view_user_detail_with_incorrect_token(client: Client, correct_login: Dict) -> None:
    """Проверка просмотра сведений о пользователе с некорректным токеном"""
    client.post('/api/v1/auth/login/', data=correct_login, content_type='application/json')
    response = client.get('/api/v1/user/', HTTP_AUTHORIZATION=f'Bearer 1234567890')
    assert response.status_code, status.HTTP_401_UNAUTHORIZED


def test_confirm_email(client: Client, correct_register: [(str, Dict)]) -> None:
    """Тестирование подтверждения почты"""
    recipient, response = correct_register
    email = find_email_in_outbox(recipient)
    assert email
    user = User.objects.get(email=recipient)
    assert not user.email_confirmed
    # Переходим по ссылке из письма
    match = re.search(r'href=[\'"]?([^\'" >]+)', email.body)
    assert match
    confirm_url = match.group(1)
    response = client.get(confirm_url)
    # После подтверждения мы должны перейти на главную страницу,
    assert response._headers['location'][1] == settings.BASE_URL
    # Смотрим что почта подтвердилась
    user = User.objects.get(email=recipient)
    assert user.email_confirmed


#
# Тестирование загрузки аватара в профиль пользователя
#

def test_avatar_upload(
        client: Client,
        correct_login: Dict,
        delete_user_images: Callable,
        request) -> None:
    """Проверка загрузки, когда все входные данные корректны"""
    response = client.post('/api/v1/auth/login/',
                           data=correct_login,
                           content_type='application/json')
    response_body = json.loads(response.content, encoding='utf-8')
    token = response_body['tokens']['access']
    headers = {
        'HTTP_AUTHORIZATION': f'Bearer {token}',
        **UPLOAD_AVATAR_HEADERS
    }
    response = client.generic(
        'POST',
        '/api/v1/user/update/avatar/',
        generate_dump(1024),
        **headers)
    response_body = json.loads(response.content, encoding='utf8')
    # Сначала проверяем, что сервер вернул корректные данные
    assert response.status_code == 200 and \
           response_body['status'] == 'ok' and \
           response_body['url']
    # Теперь проверяем, что файл действительно сохранился на диске
    # Это будет работать, если файл сохраняется на диске на той же машине
    # Если файл сохраняется на другом сервере или в облаке, надо будет
    # эту проверку заменить
    filename = response_body['url'].split('/')[-1]
    path = '/'.join([settings.MEDIA_ROOT, correct_login['email'], filename])
    # после теста удаляем всю папку медиа для этого пользователя
    request.node.user_media = '/'.join([settings.MEDIA_ROOT, correct_login['email']])
    assert os.path.isfile(path)


@pytest.mark.parametrize(
    'headers', [headers for headers in INCORRECT_UPLOAD_AVATAR_HEADERS]
)
def test_avatar_upload_with_incorrect_headers(
        client: Client,
        correct_login: Dict,
        headers: Dict,
        delete_user_images: Callable,
        request) -> None:
    """Проверка загрузки, когда заголовки некорректны"""
    response = client.post('/api/v1/auth/login/',
                           data={},
                           content_type='application/json')
    response_body = json.loads(response.content, encoding='utf-8')
    token = response_body['tokens']['access']
    headers = {
        'HTTP_AUTHORIZATION': f'Bearer {token}',
        **headers
    }
    response = client.generic(
        'POST',
        '/api/v1/user/update/avatar/',
        generate_dump(1024),
        **headers)
    response_body = json.loads(response.content, encoding='utf8')
    # На всякий случай удаляем папку медиа пользователя, вдруг
    # тест провалился и файл загрузился
    request.node.user_media = '/'.join([settings.MEDIA_ROOT, correct_login['email']])
    assert response.status_code == 400 and \
           response_body['status'] == 'error' and \
           response_body['message']
