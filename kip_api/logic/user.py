from datetime import datetime

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status

from kip_api.mixins import ObjectExistMixin, EmailMixin
from kip_api.models.user import Profile
from kip_api.utils import APIException

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
                'Пользователь с адресом {} уже зарегистрирован'.format(email),
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
        """
        user = get_object_or_404(User, email=data['email'])
        user.last_login = datetime.utcnow()
        user.save()

    @staticmethod
    def update_profile(pk, data):
        """
        Обновление данных пользователя. Пользователь может только обновить свой профиль
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
        request.user.profile.avatar = file
        request.user.profile.save()

    @staticmethod
    def delete_avatar(request):
        """Удаление аватара"""
        if (not request.user.profile.avatar) or (request.user.profile.avatar.url == settings.DEFAULT_AVATAR):
            return
        request.user.profile.avatar.delete()
        request.user.profile.save()
