import os
import uuid
import string
import random

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


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
        settings.BASE_URL, settings.API_URL,
        urlsafe_base64_encode(force_bytes(user_id)),
        token
    )


def image_file_name(instance, original_filename):
    """
    Динамическая генерация пути, куда сохранять загружаемый файл
    Все картинки мы сохраняем в папке пользователя
    """
    _, ext = os.path.splitext(original_filename)
    filename = str(uuid.uuid4()) + ext

    return '/'.join([instance.user.email, filename])


def generate_dump(size: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(size))


def file_exists(filepath):
    try:
        return os.path.isfile(filepath)
    except:
        return False
