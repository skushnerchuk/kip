from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from kip_api.mixins import ValidateMixin, ObjectExistMixin
from kip_api.permissions import IsEmailConfirmed
from kip_api.serializers.courses import (
    CourseSignupSerializer, UserCoursesSerializer
)

from kip_api.logic.user import UserService
from kip_api.models.courses import CourseGroup


class CourseSignupView(ObjectExistMixin, ValidateMixin, APIView):
    """
    Регистрация пользователя на курс.
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated, IsEmailConfirmed,)

    def post(self, request):
        validated_data = self.check(request, CourseSignupSerializer)
        course_id = validated_data['course_id']
        us = UserService()
        us.enroll_to_course(request.user.pk, course_id)
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
