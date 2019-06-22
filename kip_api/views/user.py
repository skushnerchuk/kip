from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from kip.settings import BASE_URL
from kip_api.serializers.user import UserDetailSerializer
from kip_api.utils import token_generator, APIException
from kip_api.mixins import ValidateMixin


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
    model = get_user_model()
    serializer_class = UserDetailSerializer

    def post(self, request):
        try:
            validated_data = self.check(request, UserDetailSerializer)
            user = get_user_model().objects.create(email=validated_data['email'])
            user.set_password(request.data['password'])
            user.save()
            return Response({'status': 'ok'}, status.HTTP_201_CREATED)
        except IntegrityError as ex:
            if ex.args[0] == 1062:
                raise APIException('Пользователь с адресом {} уже зарегистрирован'.format(request.data['email']),
                                   status.HTTP_400_BAD_REQUEST)
            raise


class LoginView(ValidateMixin, TokenObtainPairView):
    """
    Авторизация
    """
    parser_classes = (JSONParser,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        validated_data = self.check(request, UserDetailSerializer)
        auth_result = super(TokenObtainPairView, self).post(request, args, kwargs)
        if auth_result.status_code != status.HTTP_200_OK:
            raise APIException('Доступ запрещен', status.HTTP_403_FORBIDDEN)
        user = get_user_model().objects.filter(email=validated_data['email']).first()
        user.last_login = timezone.now()
        user.save()
        result = dict(status='ok')
        result['tokens'] = auth_result.data
        return Response(result, status.HTTP_200_OK)


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


class UserDetailView(RetrieveAPIView):
    """
    Подробная информация о пользователе, включая профиль и курсы, на которые он записан
    """
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return get_user_model().objects.select_related('profile').filter(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        user_detail = super().get(request, args, kwargs)
        return Response(
            {'status': 'ok', 'user_detail': user_detail.data},
            status.HTTP_200_OK
        )
