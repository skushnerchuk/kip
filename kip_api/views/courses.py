from django.db import IntegrityError
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kip_api.models import Course
from kip_api.serializers.courses import CourseListSerializer, CourseSerializer
from kip_api.utils import APIException
from kip_api.mixins import ValidateMixin


class CourseSignupView(APIView):
    """
    Регистрация пользователя на курс
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        try:
            request.user.courses.add(request.data['course_id'])
            request.user.save()
            return Response({'status': 'ok'}, status.HTTP_201_CREATED)
        except IntegrityError as ex:
            if ex.args[0] == 1452:
                raise APIException('Такого курса не существует', status.HTTP_400_BAD_REQUEST)
            if ex.args[0] == 1062:
                raise APIException('Вы уже записаны на этот курс', status.HTTP_400_BAD_REQUEST)
            raise


class CreateCourseView(ValidateMixin, APIView):
    """
    Создание курса
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)
    model = Course
    serializer_class = CourseSerializer

    def post(self, request):
        try:
            validated_data = self.check(request, CourseSerializer)
            course = Course.objects.create(email=validated_data['email'], )
            course.save()
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError as ex:
            if ex.args[0] == 1062:
                raise APIException('Курс с названием {} уже существует'.format(request.data['name']),
                                   status.HTTP_400_BAD_REQUEST)
            raise


class CoursesListView(ListAPIView):
    """
    Просмотр списка всех курсов без детализации по урокам
    """
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        items = super(ListAPIView, self).list(request, args, kwargs)
        return Response({'status': 'ok', 'courses': items.data}, status.HTTP_200_OK)


class CourseDetailView(RetrieveAPIView):
    """
    Просмотр списка всех курсов с детализацией по урокам
    """
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        course_detail = super().get(request, args, kwargs)
        return Response(
            {'status': 'ok', 'course_detail': course_detail.data},
            status.HTTP_200_OK
        )
