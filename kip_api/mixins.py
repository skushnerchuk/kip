from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework import status

from kip.settings import EMAIL_INFORMATOR, DEBUG
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


class EmailMixin:
    """
    Работа с электронной почтой
    """

    @staticmethod
    def send_email(receiver, subject, body):
        """
        Отправка письма. Результат отправки не проверяется.
        TODO Переделать на асинхронную отправку
        :param receiver: Получатель
        :param subject: Тема письма
        :param body: Тело письма (в формате HTML)
        :return: None
        """
        email = EmailMessage()
        email.content_subtype = 'html'
        email.subject = subject
        email.body = body
        email.from_email = EMAIL_INFORMATOR
        email.to = [receiver]
        email.send(fail_silently=True)

    def send_email_for_confirm(self, user):
        """
        Отправка письма с ссылкой для подтверждения почты
        :param user: Объект пользователя
        :return: None
        """
        # Письмо с подтверждением отправляем только в том случае, если это не отладка и домен не example.com
        # так как этот домен используется для заполнения тестовыми данными
        if DEBUG and 'example.com' in user.email:
            return
        token = token_generator.make_token(user)
        url = create_email_confirm_url(user.pk, token)
        subject = 'Подтвердите регистрацию аккаунта'
        body = render_to_string('kip_api/email/confirm.html', {'url': url})
        self.send_email(user.email, subject, body)


class ObjectExistMixin:
    """
    Проверка что объект уже существует в базе
    """

    @staticmethod
    def object_exists(model_class, filter):
        """
        :param model_class: Класс модели, по которой проводится проверка
        :param filter: фильтры, упакованные в словарь
        :return: True - объект или несколько существуют, False - не существуют
        """
        return model_class.objects.filter(**filter).exists()
