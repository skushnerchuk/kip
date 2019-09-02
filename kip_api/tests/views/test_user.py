import json
import re

from django.conf import settings
from django.core import mail
from django.urls import reverse

from data_factories import UserFactoryCustom
from kip_api.models.user import User
from kip_api.tests.base_test import BaseTest

REGISTER_ENDPOINT = '/api/v1/auth/register/'
LOGIN_ENDPOINT = '/api/v1/auth/login/'
LOGOUT_ENDPOINT = '/api/v1/auth/logout/'
USER_DETAIL_ENDPOINT = '/api/v1/user/'
USER_UPDATE_ENDPOINT = '/api/v1/user/update/'

REGISTER_BODY = {
    'email': 'username@example.com',
    'password': '1234567890'
}
INCORRECT_EMAIL_REGISTER_BODY = {
    'email': 'username_example.com',
    'password': '1234567890'
}
INCORRECT_PASSWORD_REGISTER_BODY = {
    'email': 'username_example.com',
    'password': ''
}
INCORRECT_FIELDS_REGISTER_BODY = {
    'e_mail': 'username@example.com',
    'pa_ssword': '1234567890'
}
INCORRECT_BODY = "This is string for crash"
LOGIN_BODY = {
    'email': 'username@example.com',
    'password': '1234567890'
}
LOGIN_WITH_INCORRECT_PASSWORD_BODY = {
    'email': 'username@example.com',
    'password': '0987654321'
}
UPDATE_PROFILE_BODY = {
    'biography': 'My biography',
    'birth_date': '1975-01-01',
    'first_name': 'First Name',
    'middle_name': 'Middle Name',
    'last_name': 'Last Name'
}


class CreateUserViewTest(BaseTest):
    """Тестирование регистрации пользователя"""

    def test_view_endpoint_exist(self):
        """Проверяем доступность ссылки по адресу"""
        self.check_endpoint_exist(REGISTER_ENDPOINT)

    def test_view_endpoint_accessible_by_name(self):
        """Проверяем доступность ссылки по имени"""
        self.check_endpoint_exist(reverse('register'))

    def test_register_user(self):
        """Проверяем регистрацию пользователя"""
        self.check_request_by_status_code(REGISTER_ENDPOINT, REGISTER_BODY, 201)

    def test_register_double_user(self):
        """Проверяем регистрацию пользователя с повторным адресом электронной почты"""
        self.check_request_by_status_code(REGISTER_ENDPOINT, REGISTER_BODY, 201)
        self.check_request_by_status_code(REGISTER_ENDPOINT, REGISTER_BODY, 400)

    def test_register_with_incorrect_email(self):
        """Проверяем регистрацию пользователя с некорректным адресом электронной почты"""
        self.check_request_by_status_code(REGISTER_ENDPOINT, INCORRECT_EMAIL_REGISTER_BODY, 400)

    def test_register_with_incorrect_fields(self):
        """Проверяем регистрацию пользователя с некорректными полями"""
        self.check_request_by_status_code(REGISTER_ENDPOINT, INCORRECT_FIELDS_REGISTER_BODY, 400)

    def test_register_with_incorrect_password(self):
        """Проверяем регистрацию пользователя с некорректными полями"""
        self.check_request_by_status_code(REGISTER_ENDPOINT, INCORRECT_PASSWORD_REGISTER_BODY, 400)

    def test_register_with_incorrect_register_body(self):
        """Проверяем регистрацию пользователя с некорректным телом запроса"""
        self.check_request_by_status_code(REGISTER_ENDPOINT, INCORRECT_BODY, 400)


class ConfirmEmailViewTest(BaseTest):
    """Тестирование подтверждения электронной почты"""

    @staticmethod
    def find_email_in_outbox(recipient):
        """Поиск письма в тестовом ящике"""
        for m in mail.outbox:
            if recipient in m.to:
                return m
        return None

    def setUp(self):
        """Регистрируем пользователя, у которого будем проверять подтверждение почты"""
        self.check_request_by_status_code(REGISTER_ENDPOINT, REGISTER_BODY, 201)

    def test_confirm_email(self):
        """Проверка подтверждения почты"""
        email_address = REGISTER_BODY['email']
        email = self.find_email_in_outbox(email_address)
        self.assertIsNotNone(email, 'Email with confirmation link not found in test email inbox!')

        user = User.objects.get(email=email_address)
        self.assertFalse(user.email_confirmed, f'Email {email_address} is confirmed without clicking on the link!')

        # Переходим по ссылке из письма
        match = re.search(r'href=[\'"]?([^\'" >]+)', email.body)
        self.assertIsNotNone(match, 'Confirm url not found in email body!')
        confirm_url = match.group(1)
        resp = self.client.get(confirm_url)
        # После подтверждения мы должны перейти на главную страницу,
        self.assertURLEqual(
            resp._headers['location'][1],
            settings.BASE_URL,
            f'Redirect link {resp._headers["location"][1]} not equal expected: {settings.BASE_URL}'
        )
        # Смотрим что почта подтвердилась
        user = User.objects.get(email=email_address)
        self.assertIsNotNone(user, f'User with email {email_address} not exist in database!')
        self.assertTrue(user.email_confirmed, f'Email {email_address} not confirmed!')


class LoginViewTest(BaseTest):
    """Тестирование авторизации пользователя"""

    @classmethod
    def setUpTestData(cls):
        UserFactoryCustom(
            email=LOGIN_BODY['email'],
            email_confirmed=True,
            password=LOGIN_BODY['password']
        )

    @staticmethod
    def find_email_in_outbox(recipient):
        """Поиск письма в тестовом ящике"""
        for m in mail.outbox:
            if recipient in m.to:
                return m
        return None

    def test_view_endpoint_exist(self):
        """Проверяем доступность ссылки по адресу"""
        self.check_endpoint_exist(LOGIN_ENDPOINT)

    def test_view_endpoint_accessible_by_name(self):
        """Проверяем доступность ссылки по имени"""
        self.check_endpoint_exist(reverse('login'))

    def test_login_with_correct_data_and_check_tokens(self):
        """Проверка тела ответа после авторизации с корректными данными"""
        access_token = None
        refresh_token = None
        resp = self.login(LOGIN_BODY)
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 200, resp_content.get('message'))
        # Проверяем, что пришли непустые токены
        tokens = resp_content.get('tokens')
        if tokens:
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')
        all_ok = tokens and (len(access_token) > 0) and (len(refresh_token) > 0)
        self.assertTrue(all_ok, 'The answer does not contain tokens or they are empty!')

    def test_login_with_correct_data_and_check_auth_header(self):
        """Проверка заголовка авторизации после авторизации с корректными данными"""
        resp = self.login(LOGIN_BODY)
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 200, resp_content.get('message'))
        auth_header = resp._headers.get('authorization')
        self.assertIsNotNone(auth_header, 'Headers does not contain authorization item!')
        auth_header_value = auth_header[1]
        self.assertIn(
            'Bearer ', auth_header_value,
            f'Authorization header item contain incorrect value: {auth_header_value}'
        )

    def test_login_with_incorrect_password(self):
        """Проверка авторизации с неправильным паролем"""
        resp = self.login(LOGIN_WITH_INCORRECT_PASSWORD_BODY)
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 403, resp_content.get('message'))

    def test_login_with_incorrect_body(self):
        """Проверка авторизации с неправильным паролем"""
        resp = self.login(INCORRECT_BODY)
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 400, resp_content.get('message'))


class LogoutViewTest(BaseTest):
    """Тестирование выхода пользователя из системы"""

    @classmethod
    def setUpTestData(cls):
        UserFactoryCustom(
            email=LOGIN_BODY['email'],
            email_confirmed=True,
            password=LOGIN_BODY['password']
        )

    def test_view_endpoint_exist(self):
        """Проверяем доступность ссылки по адресу"""
        self.check_endpoint_exist(LOGOUT_ENDPOINT)

    def test_view_endpoint_accessible_by_name(self):
        """Проверяем доступность ссылки по имени"""
        self.check_endpoint_exist(reverse('logout'))

    def test_logout_after_login(self):
        """Тестирование корректного выхода пользователя из системы после корректной авторизации"""
        resp = self.client.post(LOGIN_ENDPOINT, data=LOGIN_BODY, content_type='application/json')
        resp_content = json.loads(resp.content, encoding='utf8')
        refresh_token = resp_content['tokens']['refresh']
        resp = self.client.post(LOGOUT_ENDPOINT, data={'token': refresh_token}, content_type='application/json')
        self.assertEqual(resp.status_code, 302)
        self.assertURLEqual(
            resp._headers['location'][1],
            settings.BASE_URL,
            f'Redirect link {resp._headers["location"][1]} not equal expected: {settings.BASE_URL}'
        )

    def test_logout_after_login_with_incorrect_token(self):
        """Тестирование выхода пользователя из системы с некорректным токеном"""
        self.client.post(LOGIN_ENDPOINT, data=LOGIN_BODY, content_type='application/json')
        resp = self.client.post(LOGOUT_ENDPOINT, data={'token': 'Incorrect token'}, content_type='application/json')
        self.assertEqual(resp.status_code, 400)


class UserDetailViewTest(BaseTest):
    """Тестирование просмотра информации о пользователе"""

    @classmethod
    def setUpTestData(cls):
        UserFactoryCustom(
            email=LOGIN_BODY['email'],
            email_confirmed=True,
            password=LOGIN_BODY['password']
        )

    def test_view_endpoint_exist(self):
        """Проверяем доступность ссылки по адресу"""
        self.check_endpoint_exist(USER_DETAIL_ENDPOINT)

    def test_view_endpoint_accessible_by_name(self):
        """Проверяем доступность ссылки по имени"""
        self.check_endpoint_exist(reverse('user_detail'))

    def test_view_detail_after_correct_login(self):
        """Проверяем доступ с корректным токеном"""
        resp_content = json.loads(self.login(LOGIN_BODY).content, encoding='utf8')
        token = resp_content['tokens']['access']
        resp = self.client.get(USER_DETAIL_ENDPOINT, HTTP_AUTHORIZATION=f'Bearer {token}')
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 200, resp_content.get('message'))

    def test_view_detail_with_incorrect_token(self):
        """Проверяем доступ с некорректным токеном"""
        token = "Incorrect token"
        resp = self.client.get(USER_DETAIL_ENDPOINT, HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(resp.status_code, 403)


class UserUpdateViewTest(BaseTest):
    """Тестирование редактирования информации о пользователе"""

    @classmethod
    def setUpTestData(cls):
        UserFactoryCustom(
            email=LOGIN_BODY['email'],
            email_confirmed=True,
            password=LOGIN_BODY['password']
        )

    def test_view_endpoint_exist(self):
        """Проверяем доступность ссылки по адресу"""
        self.check_endpoint_exist(USER_UPDATE_ENDPOINT)

    def test_view_endpoint_accessible_by_name(self):
        """Проверяем доступность ссылки по имени"""
        self.check_endpoint_exist(reverse('user_update'))

    def test_update_after_correct_login(self):
        """Проверяем обновление профиля с корректным токеном"""
        resp_content = json.loads(self.login(LOGIN_BODY).content, encoding='utf8')
        token = resp_content['tokens']['access']
        resp = self.client.put(
            USER_UPDATE_ENDPOINT,
            data=UPDATE_PROFILE_BODY, content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}')
        resp_content = json.loads(resp.content, encoding='utf8')
        self.assertEqual(resp.status_code, 200, resp_content.get('message'))

    def test_update_with_incorrect_token(self):
        """Проверяем обновление профиля с некорректным токеном"""
        token = 'Incorrect token'
        resp = self.client.put(
            USER_UPDATE_ENDPOINT,
            data=UPDATE_PROFILE_BODY, content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(resp.status_code, 403)
