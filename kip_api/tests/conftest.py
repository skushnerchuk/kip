import json
from typing import Dict

import pytest
from django.conf import settings
from django.test.client import Client

from data_factories import (
    generate_courses, generate_categories, generate_groups,
    generate_lessons, generate_users, UserFactoryCustom
)
from kip_api.models import User, CoursesCategory
from kip_api.tests.types_for_test import CORRECT_LOGIN_BODY

settings.DISABLE_LOGGING = True

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(transactional_db):
    pass


@pytest.yield_fixture()
def correct_login() -> Dict:
    body = CORRECT_LOGIN_BODY
    UserFactoryCustom(
        email=body['email'],
        email_confirmed=True,
        password=body['password']
    )
    yield body
    User.objects.filter(email=body['email']).delete()


@pytest.yield_fixture()
def correct_register(client: Client) -> [(str, Dict)]:
    body = CORRECT_LOGIN_BODY
    response = client.post('/api/v1/auth/register/', data=body, content_type='application/json')
    yield (body['email'], json.loads(response.content, encoding='utf-8'))
    User.objects.filter(email=body['email']).delete()


@pytest.yield_fixture()
def prepare_courses():
    generate_users(1)
    generate_categories(1)
    generate_courses(1)
    generate_groups(1)
    generate_lessons(1)
    yield
    User.objects.all().delete()
    CoursesCategory.objects.all().delete()


@pytest.yield_fixture()
def prepare_avatar():
    yield ''
