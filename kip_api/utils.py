from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.db import models

from kip.settings import BASE_URL, API_URL


class APIException(Exception):
    """
    Общее исключение API
    """

    def __init__(self, message, status):
        self.status = status
        self.message = message
        super().__init__(self, message)


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Генератор токенов для подтверждения почты
    """

    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


token_generator = AccountActivationTokenGenerator()


def create_email_confirm_url(user_id, token):
    """
    Создание ссылки для подтверждения почты
    :param user_id: идентификатор пользователя (pk из таблицы)
    :param token: сгенерированный токен, по которому будем проверять корректность ссылки
    :return: ссылка
    """
    return '{}{}auth/confirm_email/{}/{}'.format(
        BASE_URL, API_URL,
        urlsafe_base64_encode(force_bytes(user_id)),
        token
    )
