import json
import os
import uuid

from amqpstorm import Connection
from amqpstorm import Message, exception as StormEx
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from rest_framework import status

from common.global_mixins import LoggingMixin
from kip_api.utils import (
    token_generator, APIException, create_email_confirm_url
)


class ValidateMixin:
    """
    Проверка качества входных данных
    """

    @staticmethod
    def check(request, serializer_class):
        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            raise APIException('Неверные входные данные', status.HTTP_400_BAD_REQUEST)
        return serializer.validated_data


class ObjectExistMixin:
    """
    Проверка что объект (или несколько), соответствующий фильтру, уже существует в базе
    """

    @staticmethod
    def object_exists(model_class, filters):
        """
        :param model_class: Класс модели, по которой проводится проверка
        :param filters: фильтры, упакованные в словарь
        :return: True - объект или несколько существуют, False - не существуют
        """
        return model_class.objects.filter(**filters).exists()


class BusMixin(LoggingMixin):
    """
    Миксина работы с шиной данных
    """

    def send_message_to_bus(self, query_name, message):
        rq_host = os.getenv('RMQ_HOST', '127.0.0.1')
        rq_port = int(os.getenv('RMQ_PORT', 5672))
        rq_user = os.getenv('RMQ_USERNAME', 'guest')
        rq_password = os.getenv('RMQ_PASSWORD', 'guest')

        try:
            connection = Connection(
                hostname=rq_host, port=rq_port,
                username=rq_user, password=rq_password
            )
            channel = connection.channel()
            msg_props = {
                'content_type': 'application/json',
                'delivery_mode': 2
            }
            message = Message.create(channel=channel,
                                     body=json.dumps(message, ensure_ascii=False),
                                     properties=msg_props)
            with channel.tx:
                message.publish(query_name)
        except StormEx.AMQPConnectionError as exc:
            self.error(self.create_exception_record(exc))


class EmailMixin(BusMixin):
    """
    Работа с электронной почтой
    """

    @staticmethod
    def send_test_email(user):
        """Отправка тестового сообщения в локальный ящик"""
        token = token_generator.make_token(user)
        url = create_email_confirm_url(user.pk, token)
        subject = 'Подтвердите регистрацию аккаунта'
        body = render_to_string('kip_api/email/confirm.html', {'url': url})
        mail.send_mail(subject, body, settings.INFORMER_EMAIL, [user.email], fail_silently=False)

    def send_email_for_confirm(self, user):
        """
        Отправка письма с ссылкой для подтверждения почты
        :param user: Объект пользователя
        """
        # Письмо с подтверждением отправляем только в том случае, если это не отладка и домен не example.com
        # так как этот домен используется для заполнения тестовыми данными
        if settings.DEBUG and 'example.com' in user.email:
            return
        # При тестировании письма отправляем в локальный ящик
        if settings.TESTING:
            self.send_test_email(user)
            return
        token = token_generator.make_token(user)
        url = create_email_confirm_url(user.pk, token)
        subject = 'Подтвердите регистрацию аккаунта'
        body = render_to_string('kip_api/email/confirm.html', {'url': url})
        message = {
            "uuid": str(uuid.uuid4()),
            "sender": settings.INFORMER_EMAIL,
            "receivers": [user.email],
            "subject": subject,
            "body": body,
            "attachments": []
        }
        self.send_message_to_bus('emails', message)
