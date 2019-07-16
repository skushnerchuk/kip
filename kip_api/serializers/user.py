#
# Сериализаторы представлений пользователей
#

from django.contrib.auth import get_user_model
from rest_framework import serializers

from kip_api.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сведения о профиле пользователя
    """

    class Meta:
        model = Profile
        fields = ('first_name', 'middle_name', 'last_name', 'birth_date', 'biography',)

    birth_date = serializers.DateField(required=True, allow_null=True)
    biography = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    first_name = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    middle_name = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    last_name = serializers.CharField(required=True, allow_null=True, allow_blank=True)


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
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    last_login = serializers.DateTimeField(required=False)
    date_joined = serializers.DateTimeField(required=False)
    email_confirmed = serializers.BooleanField(required=False)
