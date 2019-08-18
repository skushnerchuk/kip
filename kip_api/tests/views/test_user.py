import json
from django.urls import reverse

from kip_api.tests.base_test import BaseTest


class CreateUserViewTest(BaseTest):
    """
    Тестирование регистрации пользователя
    """
    ENDPOINT = '/api/v1/auth/register/'
    REGISTER_BODY = {
        'email': 'username@example.com',
        'password': '1234567890'
    }

    def test_view_url_exist(self):
        """Проверяем доступность ссылки по адресу"""
        resp = self.client.options(self.ENDPOINT)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Проверяем доступность ссылки по имени"""
        resp = self.client.options(reverse('register'))
        self.assertEqual(resp.status_code, 200)

    def test_register_user(self):
        """Проверяем регистрацию пользователя"""
        resp = self.client.post(
            self.ENDPOINT,
            data=self.REGISTER_BODY,
            content_type='application/json'
        )
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 201, resp_content.get('message'))

    def test_register_double_user(self):
        """Проверяем регистрацию пользователя с повторным адресом электронной почты"""
        resp = self.client.post(
            self.ENDPOINT,
            data=self.REGISTER_BODY,
            content_type='application/json'
        )
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 201, resp_content.get('message'))

        resp = self.client.post(
            self.ENDPOINT,
            data=self.REGISTER_BODY,
            content_type='application/json'
        )
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 400, resp_content.get('message'))
