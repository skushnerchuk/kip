from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from kip_api.mixins import ValidateMixin, ObjectExistMixin
from kip_api.models import Course, CoursesCategory
from kip_api.permissions import IsEmailConfirmed
from kip_api.serializers.courses import (
    CourseListSerializer, CourseSerializer, CourseCreateSerializer
)
from kip_api.utils import APIException


class CourseSignupView(ObjectExistMixin, ValidateMixin, APIView):
    """
    Регистрация пользователя на курс.
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated, IsEmailConfirmed,)

    def post(self, request):

        course_pk = int(request.data['course_id'])
        if not self.object_exists(Course, {'pk': course_pk}):
            raise APIException('Такого курса не существует', status.HTTP_400_BAD_REQUEST)
        courses = list(request.user.courses.all().values_list('pk', flat=True))
        if course_pk in courses:
            raise APIException('Вы уже записаны на этот курс', status.HTTP_400_BAD_REQUEST)
        request.user.courses.add(request.data['course_id'])
        request.user.save()
        return Response({'status': 'ok'}, status.HTTP_201_CREATED)


class CreateCourseView(ObjectExistMixin, ValidateMixin, APIView):
    """
    Создание курса
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAdminUser,)
    model = Course
    serializer_class = CourseCreateSerializer

    def post(self, request):
        validated_data = self.check(request, CourseCreateSerializer)
        name = validated_data['name']
        category = validated_data['category_id']

        if not self.object_exists(CoursesCategory, {'pk': category}):
            raise APIException('Такой категории не существует', status.HTTP_400_BAD_REQUEST)

        if self.object_exists(Course, {'name': name, 'category_id': category}):
            raise APIException('Курс с названием {} в указанной категории уже существует'.
                               format(request.data['name']),
                               status.HTTP_400_BAD_REQUEST)

        course = Course.objects.create(name=validated_data['name'], category_id=category)
        course.save()
        return Response(status=status.HTTP_201_CREATED)


class CoursesListView(ListAPIView):
    """
    Просмотр списка всех курсов без детализации по урокам
    """
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Course.objects.select_related('category').all()

    def get(self, request, *args, **kwargs):
        items = super(ListAPIView, self).list(request, args, kwargs)
        return Response({'status': 'ok', 'courses': items.data}, status.HTTP_200_OK)


class CourseDetailView(RetrieveAPIView):
    """
    Просмотр списка всех курсов с детализацией по урокам
    """
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Course.objects.select_related('category').filter(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        course_detail = super().get(request, args, kwargs)
        return Response(
            {'status': 'ok', 'course_detail': course_detail.data},
            status.HTTP_200_OK
        )
