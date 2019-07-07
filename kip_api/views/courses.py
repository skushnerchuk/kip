from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from kip_api.mixins import ValidateMixin, ObjectExistMixin
from kip_api.permissions import IsEmailConfirmed
from kip_api.serializers.courses import (
    CourseSignupSerializer, UserCoursesSerializer, LessonSerializer
)
from kip_api.logic.user import UserService
from kip_api.logic.course import CourseService
from kip_api.models.courses import (
    CourseGroup, Participation, Lesson
)
from kip_api.utils import APIException


class CourseSignupView(ObjectExistMixin, ValidateMixin, APIView):
    """
    Регистрация пользователя на курс.
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated, IsEmailConfirmed,)

    def post(self, request):
        validated_data = self.check(request, CourseSignupSerializer)
        course_id = validated_data['course_id']
        cs = CourseService()
        cs.enroll(request.user.pk, course_id)
        return Response({'status': 'ok'}, status.HTTP_201_CREATED)


class UserGroupsView(ObjectExistMixin, ValidateMixin, ListAPIView):
    """
    Просмотр учебных групп пользователя
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated, IsEmailConfirmed,)
    serializer_class = UserCoursesSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        return CourseGroup.objects.filter(
            participations__user_id=user_id,
            closed=False
        ).select_related('course__category')

    def get(self, request, *args, **kwargs):
        items = super(ListAPIView, self).list(request, args, kwargs)
        return Response({'status': 'ok', 'groups': items.data}, status.HTTP_200_OK)


class CourseGroupScheduleView(ObjectExistMixin, APIView):
    """
    Просмотр расписания учебной группы
    Обычный пользователь может смотреть только группы, в которых он участвует,
    администраторы - все группы.
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated, IsEmailConfirmed,)

    def get(self, request, group_id):
        user_id = self.request.user.pk
        group = get_object_or_404(CourseGroup, id=group_id)
        filter = dict(user=user_id, group=group.id)
        # Если пользователь не участник группы и не администратор - запрещаем
        # При этом хитрим - не говорим прямо что нельзя, а просто "нет такого"
        if not self.object_exists(Participation, filter) and not request.user.is_superuser:
            return APIException('Страница не найдена', status.HTTP_404_NOT_FOUND)
        schedule = Lesson.objects.select_related('group').filter(group=group_id).order_by('number').all()
        serializer = LessonSerializer(schedule, many=True)
        return Response({'status': 'ok', 'schedule': serializer.data}, status.HTTP_200_OK)
