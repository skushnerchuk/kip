from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status

from kip_api.mixins import ObjectExistMixin, EmailMixin
from kip_api.models.user import Profile
from kip_api.utils import APIException
from kip_api.validators import validate_file_ext, validate_content_type, validate_file_size

User = get_user_model()


class UserService(ObjectExistMixin, EmailMixin):
    """
    Слой логики по работе с пользователями
    """

    def create(self, data):
        """
        Регистрация нового пользователя
        """
        email = data['email']
        password = data['password']
        if self.object_exists(User, {'email': email}):
            raise APIException(
                f'Пользователь с адресом {email} уже зарегистрирован',
                status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            user = User.objects.create(email=email)
            user.set_password(password)
            user.save()
            Profile.objects.create(user=user)
        self.send_email_for_confirm(user)

    @staticmethod
    def register_login(data):
        """
        Сохраняем дату и время последней регистрации пользователя
        TODO заменить pk на объект пользователя из request
        """
        user = get_object_or_404(User, email=data['email'])
        user.last_login = datetime.utcnow()
        user.save()

    @staticmethod
    def update_profile(pk, data):
        """
        Обновление данных пользователя. Пользователь может только обновить свой профиль
        TODO заменить pk на объект пользователя из request
        """
        user = get_object_or_404(User, pk=pk)
        user.profile.biography = data['biography']
        user.profile.birth_date = data['birth_date']
        user.profile.first_name = data['first_name']
        user.profile.middle_name = data['middle_name']
        user.profile.last_name = data['last_name']
        user.profile.save()
        return user

    @staticmethod
    def upload_avatar(request):
        """Загрузка аватара"""
        file = request.FILES['file']
        validate_file_ext(file.name, ['.jpg', '.png', '.jpeg'])
        validate_content_type(
            request._request.headers['Content-Type'],
            ['image/jpeg', 'image/png']
        )
        validate_file_size(file, settings.MAX_AVATAR_SIZE)
        request.user.profile.avatar = file
        request.user.profile.save()

    @staticmethod
    def delete_avatar(request):
        """Удаление аватара"""
        if (not request.user.profile.avatar) or (request.user.profile.avatar.url == settings.DEFAULT_AVATAR):
            return
        request.user.profile.avatar.delete()
        request.user.profile.save()
