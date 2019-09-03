from kip_api.tests.base_test import BaseTest
from kip_api.models.user import User, Profile


class UserModelMetadataTest(BaseTest):
    """
    Тестирование метаданных пользовательской модели
    Мы не хотим, чтобы изменения метаданных проходили мимо тестов,
    поэтому будем их проверять. Для упрощения не будут проверятся типы полей,
    их размерности и т.п.
    Также здесь будет проверяться модель Profile, как неразрывно связанная
    с моделью User
    """

    # Метаданные самой модели

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = User.objects.first()._meta.model_name
        self.assertEqual(
            'user',
            model_name,
            f'Incorrect user model name: {model_name}')

    def test_model_verbose_name(self):
        """Проверка отображаемого названия модели"""
        self.check_verbose_name(User.objects.first())

    def test_model_verbose_name_plural(self):
        """Проверка отображаемого названия модели во множественном числе"""
        self.check_plural_verbose_name(User.objects.first())

    # Метаданные поля email

    def test_email_field_exist(self):
        """Проверяем наличие полей"""
        fields = ['email', 'email_confirmed', 'groups']
        self.check_fields_exist(User, fields)

    def test_email_field_unique(self):
        """Проверяем уникальность поля email"""
        field = User.objects.first()._meta.get_field('email')
        self.assertTrue(field._unique, 'Email field must be unique!')

    # Метаданные поля email_confirmed

    def test_user_disabled_fields(self):
        """Проверяем, что отсутствуют поля, которые мы перекрываем"""
        fields = ['username', 'first_name', 'last_name', ]
        obj = User.objects.first()
        absent = [f for f in fields if self.field_exist(obj, f)]
        self.assertListEqual(
            absent, [],
            f'The field(s) <{",".join(absent)}> must be absent!'
        )

    def test_username_field(self):
        """Проверяем, что USERNAME_FIELD выставлен в модели правильно"""
        self.assertEqual(
            User.USERNAME_FIELD, 'email',
            'Field USERNAME_FIELD must be equal "email"'
        )

    def test_required_fields(self):
        """проверяем, что поле REQUIRED_FIELDS пустое"""
        self.assertListEqual(
            User.REQUIRED_FIELDS, [],
            'Field REQUIRED_FIELD must be empty'
        )

    def test_user_str_method(self):
        """Проверка метода __str__ - он должен возвращать почту пользователя"""
        user = User.objects.first()
        self.assertEqual(
            user.__str__(), user.email,
            'Values of __str__() function and email field must be equal!'
        )

    def test_profile_model_name(self):
        """Проверяем корректность имени модели"""
        model_name = Profile.objects.first()._meta.model_name
        self.assertEqual(
            model_name, 'profile',
            f'Profile model incorrect name: {model_name}'
        )

    def test_profile_fields(self):
        """Проверяем, что присутствуют все поля"""
        fields = [
            'user', 'birth_date', 'biography', 'first_name',
            'middle_name', 'last_name',
        ]
        self.check_fields_exist(Profile, fields)

    def test_profile_str_method(self):
        """Проверка метода __str__()"""
        user = User.objects.first()
        profile = Profile.objects.get(user_id=user.id)
        self.assertEqual(profile.__str__(), f'Профиль: {profile.user.email}')
