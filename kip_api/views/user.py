from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from kip.settings import BASE_URL
from kip_api.logic.user import UserService
from kip_api.mixins import ValidateMixin
from kip_api.serializers.user import (
    UserLoginSerializer, UserDetailSerializer, ProfileSerializer,
)
from kip_api.serializers.courses import UserCoursesSerializer
from kip_api.utils import token_generator, APIException
from kip_api.models.courses import Participation


class ConfirmEmailView(APIView):
    """
    Подтверждение почты пользователя
    """
    permission_classes = (AllowAny,)

    @staticmethod
    def get_user_object(pk):
        try:
            uid = force_text(urlsafe_base64_decode(pk))
            return get_user_model().objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return None

    def get(self, request, user, token):
        user = self.get_user_object(user)
        if user and token_generator.check_token(user, token):
            user.email_confirmed = True
            user.save()
            return Response(status=status.HTTP_302_FOUND, headers={'Location': BASE_URL})
        # TODO Заменить на редирект на страницу с соответствующим сообщением
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(ValidateMixin, APIView):
    """
    Регистрация нового пользователя
    """
    parser_classes = (JSONParser,)
    permission_classes = (AllowAny,)

    def post(self, request):
        validated_data = self.check(request, UserDetailSerializer)
        UserService.create(validated_data)
        return Response({'status': 'ok'}, status.HTTP_201_CREATED)


class LoginView(ValidateMixin, TokenObtainPairView):
    """
    Авторизация
    """
    parser_classes = (JSONParser,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        validated_data = self.check(request, UserLoginSerializer)
        auth_result = super(TokenObtainPairView, self).post(request, args, kwargs)
        if auth_result.status_code != status.HTTP_200_OK:
            raise APIException('Доступ запрещен', status.HTTP_403_FORBIDDEN)
        UserService.register_login(validated_data)
        result = dict(
            status='ok',
            tokens=auth_result.data,
        )
        # self.request.auth
        return Response(
            data=result,
            status=status.HTTP_200_OK,
            headers={'Authorization': 'Bearer {}'.format(auth_result.data['access'])}
        )


class LogoutView(APIView):
    """
    Выход из системы
    Сводится к блокировке refresh-токена, при этом фронт должен
    перед вызовом этого метода удалить оба токена из своего хранилища
    """
    parser_classes = (JSONParser,)
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        tokenb64 = request.data['token']
        token = RefreshToken(tokenb64)
        token.blacklist()
        return Response(status=status.HTTP_302_FOUND, headers={'Location': BASE_URL})


class UserDetailView(ValidateMixin, RetrieveAPIView):
    """
    Подробная информация о пользователе, включая профиль
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserDetailSerializer

    def get_queryset(self):
        self.kwargs['pk'] = self.request.user.pk
        return get_user_model().objects.select_related('profile').filter(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        user_detail = super().get(request, args, kwargs)
        return Response(
            {'status': 'ok', 'user_detail': user_detail.data},
            status.HTTP_200_OK
        )


class UserUpdateView(ValidateMixin, APIView):
    """
    Обновление профиля пользователя
    """
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        validated_data = self.check(request, ProfileSerializer)
        user = UserService.update_profile(request.user.pk, validated_data)
        serializer = UserDetailSerializer(user)
        return Response(
            {
                'status': 'ok',
                'user_detail': serializer.data
            },
            status.HTTP_200_OK
        )


class UserCoursesView(ListAPIView):
    """
    Просмотр информации по группам, в которые записан пользователь
    """
    parser_classes = JSONParser
    serializer_class = UserCoursesSerializer

    def get_queryset(self):
        return Participation.objects.select_related('group_id') \
            .filter(user_id=self.request.user.pk, closed=False)

    def get(self, request, *args, **kwargs):
        items = super(ListAPIView, self).list(request, args, kwargs)
        return Response({'status': 'ok', 'courses': items.data}, status.HTTP_200_OK)
