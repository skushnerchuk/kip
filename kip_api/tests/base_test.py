import json

from django.conf import settings
from django.db import models
from django.test import TestCase
from django.core import mail

from data_factories import (
    generate_courses, generate_categories, generate_groups,
    generate_lessons, generate_users
)


class BaseTest(TestCase):
    """
    Базовый класс тестов
    """

    @classmethod
    def setUpTestData(cls):
        # Запрещаем логгирование на время автотестов
        settings.DISABLE_LOGGING = True
        # Чистим тестовый ящик
        mail.outbox = []
        generate_users(1)
        generate_categories(1)
        generate_courses(1)
        generate_groups(1)
        generate_lessons(1)

    @staticmethod
    def field_exist(model_object, field):
        """Проверяем наличие поля field в модели model"""
        try:
            model_object._meta.get_field(field)
            return True
        except models.FieldDoesNotExist:
            return False

    def check_verbose_name(self, obj):
        """Проверка отображаемого имени объекта obj."""
        if '_meta' in obj.__dir__():
            verbose_name = obj._meta.verbose_name
        else:
            verbose_name = obj.verbose_name

        self.assertNotEqual(
            '', verbose_name, f'Verbose name must have a value'
        )
        self.assertIsNotNone(
            verbose_name, f'Verbose name must have a value'
        )

    def check_plural_verbose_name(self, obj):
        """
        Проверка отображаемого имени во множественном числе объекта obj
        """
        if '_meta' in obj.__dir__():
            plural_name = obj._meta.verbose_name_plural
        else:
            plural_name = obj.verbose_name_plural

        self.assertNotEqual(
            '', plural_name, f'Plural verbose name must have a value'
        )
        self.assertIsNotNone(
            plural_name, f'Plural verbose name must have a value'
        )

    def check_fields_exist(self, model, fields):
        """Проверяем, что присутствуют все поля"""
        obj = model.objects.first()
        absent = [f for f in fields if not self.field_exist(obj, f)]
        self.assertListEqual(
            absent, [],
            f'The field(s) <{",".join(absent)}> must be exist!'
        )

    def check_request_by_status_code(self, endpoint, body, status_code):
        """Проверяем ответ сервера на соответствие коду"""
        resp = self.client.post(endpoint, data=body, content_type='application/json')
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, status_code, resp_content.get('message'))

    def check_endpoint_exist(self, endpoint):
        resp = self.client.options(endpoint)
        # При получении ошибки 401 тоже считаем, что endpoint существует, но требует авторизации
        self.assertIn(resp.status_code, [200, 401])

    def login(self, body):
        return self.client.post('/api/v1/auth/login/', data=body, content_type='application/json')
