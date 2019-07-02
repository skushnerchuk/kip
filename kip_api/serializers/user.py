from django.contrib.auth import get_user_model
from rest_framework import serializers

from kip_api.models.courses import Profile
from .courses import CourseListSerializer


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сведения о профиле пользователя
    """

    class Meta:
        model = Profile
        fields = ('birth_date',)

    birth_date = serializers.DateField()


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Подробная информация о пользователе, включая профиль и все его курсы
    """

    class Meta:
        model = get_user_model()
        fields = (
            'courses', 'profile', 'email', 'password', 'first_name',
            'last_name', 'last_login', 'date_joined', 'email_confirmed',
        )

    courses = CourseListSerializer(read_only=True, many=True, required=False)
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(required=False)
    date_joined = serializers.DateTimeField(required=False)
    email_confirmed = serializers.BooleanField(required=False)
