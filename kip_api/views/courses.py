from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kip_api.mixins import ValidateMixin, ObjectExistMixin
from kip_api.permissions import IsEmailConfirmed
from kip_api.serializers.courses import (
    CourseSignupSerializer
)
from kip_api.logic.user import UserService


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
#
#
# class CreateCourseView(ObjectExistMixin, ValidateMixin, APIView):
#     """
#     Создание курса
#     """
#     parser_classes = (JSONParser,)
#     permission_classes = (IsAdminUser,)
#     model = Course
#     serializer_class = CourseCreateSerializer
#
#     def post(self, request):
#         validated_data = self.check(request, CourseCreateSerializer)
#         name = validated_data['name']
#         category = validated_data['category_id']
#
#         if not self.object_exists(CoursesCategory, {'pk': category}):
#             raise APIException('Такой категории не существует', status.HTTP_404_NOT_FOUND)
#
#         if self.object_exists(Course, {'name': name, 'category_id': category}):
#             raise APIException('Курс с названием {} в указанной категории уже существует'.
#                                format(request.data['name']),
#                                status.HTTP_400_BAD_REQUEST)
#
#         course = Course.objects.create(name=validated_data['name'], category_id=category)
#         course.save()
#         return Response(status=status.HTTP_201_CREATED)
#
#
# class CoursesListView(ListAPIView):
#     """
#     Просмотр списка всех курсов без детализации по урокам
#     """
#     queryset = Course.objects.all()
#     serializer_class = CourseListSerializer
#     permission_classes = (IsAuthenticated,)
#
#     def get_queryset(self):
#         return Course.objects.select_related('category').all()
#
#     def get(self, request, *args, **kwargs):
#         items = super(ListAPIView, self).list(request, args, kwargs)
#         return Response({'status': 'ok', 'courses': items.data}, status.HTTP_200_OK)
#
#
# class CourseDetailView(RetrieveAPIView):
#     """
#     Просмотр списка всех курсов с детализацией по урокам
#     """
#     serializer_class = CourseSerializer
#     permission_classes = (IsAuthenticated,)
#
#     def get_queryset(self):
#         return Course.objects.select_related('category').filter(pk=self.kwargs['pk'])
#
#     def get(self, request, *args, **kwargs):
#         course_detail = super().get(request, args, kwargs)
#         return Response(
#             {'status': 'ok', 'course_detail': course_detail.data},
#             status.HTTP_200_OK
#         )
#
#
# class GroupListView(ListAPIView):
#     """
#     Просмотр списка всех групп курса
#     """
#     queryset = CourseGroup.objects.all()
#     serializer_class = CourseListSerializer
#     permission_classes = (IsAuthenticated,)
#
#     def get_queryset(self):
#         return Course.objects.select_related('category').all()
#
#     def get(self, request, *args, **kwargs):
#         items = super(ListAPIView, self).list(request, args, kwargs)
#         return Response({'status': 'ok', 'courses': items.data}, status.HTTP_200_OK)
