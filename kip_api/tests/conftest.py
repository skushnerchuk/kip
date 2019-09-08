import pytest
from django.conf import settings


settings.DISABLE_LOGGING = True

CORRECT_LOGIN_BODY = {
    'email': 'username@example.com',
    'password': '1234567890'
}


@pytest.fixture()
def correct_login(client):
    body = CORRECT_LOGIN_BODY
    return client.post(
        '/api/v1/auth/login/',
        data=body,
        content_type='application/json'
    )


@pytest.fixture(scope='session')
def correct_register(client):
    body = CORRECT_LOGIN_BODY
    return client.post(
        '/api/v1/auth/register/',
        data=body,
        content_type='application/json'
    )
