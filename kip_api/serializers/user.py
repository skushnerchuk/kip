#
# Сериализаторы представлений пользователей
#
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from kip_api.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сведения о профиле пользователя
    """
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('first_name', 'middle_name', 'last_name', 'birth_date', 'biography', 'avatar_url',)

    birth_date = serializers.DateField(required=True, allow_null=True)
    biography = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    first_name = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    middle_name = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    last_name = serializers.CharField(required=True, allow_null=True, allow_blank=True)

    @staticmethod
    def get_avatar_url(profile):
        try:
            if os.path.isfile(profile.avatar.path):
                return profile.avatar.url
        except ValueError as ex:
            return settings.DEFAULT_AVATAR


class UserLoginSerializer(serializers.ModelSerializer):
    """
    Сериализация данных при авторизации
    """

    class Meta:
        model = get_user_model()
        fields = (
            'email', 'password',
        )

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Информация о пользователе, включая профиль
    """

    class Meta:
        model = get_user_model()
        fields = (
            'profile', 'email', 'password', 'last_login', 'date_joined', 'email_confirmed',
        )

    profile = ProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    last_login = serializers.DateTimeField(required=False)
    date_joined = serializers.DateTimeField(required=False)
    email_confirmed = serializers.BooleanField(required=False)
