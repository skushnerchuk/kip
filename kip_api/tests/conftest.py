from typing import Dict

import pytest
from django.conf import settings

from data_factories import UserFactoryCustom
from kip_api.models import User
from kip_api.tests.types_for_test import CORRECT_LOGIN_BODY

settings.DISABLE_LOGGING = True


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
