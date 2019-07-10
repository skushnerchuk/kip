from django.contrib.auth import get_user_model
from rest_framework import serializers

from kip_api.models.courses import (
    Participation, CourseGroup, Courses
)
from kip_api.serializers.user import UserDetailSerializer


class CourseSignupSerializer(serializers.ModelSerializer):
    """
    Сериализатор записи на курс
    """

    class Meta:
        model = CourseGroup
        fields = ('course_id',)

    course_id = serializers.IntegerField()


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор записи на курс
    """

    class Meta:
        model = Courses
        fields = ('name',)

    name = serializers.CharField()


class CourseGroupSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений о группе
    """

    class Meta:
        model = CourseGroup
        fields = ('pk', 'course', 'name',)

    pk = serializers.IntegerField()
    course = serializers.CharField()
    name = serializers.CharField()


class UserCoursesSerializer(serializers.ModelSerializer):
    """
    Сериализатор групп, в которые входит пользователь
    Предоставляет краткую информацию для отображения списка
    """

    class Meta:
        model = CourseGroup
        fields = ['pk', 'name', 'course', 'short_schedule', 'detail_program']

    course = serializers.CharField()
