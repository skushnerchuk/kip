import pytest

from django.conf import settings
from django.test.client import Client
from rest_framework.response import Response

from data_factories import UserFactoryCustom
from .types_for_test import ApiResponse
from kip_api.models import User

settings.DISABLE_LOGGING = True

CORRECT_LOGIN_BODY = {
    'email': 'username@example.com',
    'password': '1234567890'
}
INCORRECT_REGISTER_BODY = [
    ('username_example.com', '1234567890'),
    ('username_example.com', ''),
]


@pytest.fixture()
@pytest.mark.parametrize(
    params=INCORRECT_REGISTER_BODY
)
def incorrect_register(request, client: Client, email: str, password: str) -> Response:
    body = {
        'email': email,
        'password': password
    }
    return (
        client.post(
            '/api/v1/auth/register/',
            data=body,
            content_type='application/json'
        )
    )


@pytest.fixture()
def correct_login(client: Client) -> ApiResponse:
    body = CORRECT_LOGIN_BODY
    UserFactoryCustom(
        email=body['email'],
        email_confirmed=True,
        password=body['password']
    )
    yield (
        client.post(
            '/api/v1/auth/login/',
            data=body,
            content_type='application/json'
        )
    )
    User.objects.filter(email=body['email']).delete()


@pytest.fixture()
def correct_register(client: Client) -> ApiResponse:
    body = CORRECT_LOGIN_BODY
    return (
        body['email'],
        client.post(
            '/api/v1/auth/register/',
            data=body,
            content_type='application/json'
        )
    )
