from rest_framework import status
from .utils import APIException


class ValidateMixin:
    """
    Проверка качества входных данных
    """

    @staticmethod
    def check(request, serializer_class):
        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            raise APIException('Неверные входные данные', status.HTTP_400_BAD_REQUEST)
        return serializer.validated_data