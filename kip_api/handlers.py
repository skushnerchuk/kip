import datetime
import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from kip.global_mixins import LoggingMixin


class ErrorHandler(LoggingMixin):
    """
    Класс обработки ошибок и формирования ответов клиентам
    """
    def process(self, exc, context):
        self.exc = exc
        self.context = context
        self.add_to_log()

        result = {'status': 'error', 'message': ''}
        handlers = {
            'notauthenticated': self.not_authenticated_handler,
            'invalidtoken': self.invalid_token_handler,
            'authenticationfailed': self.auth_failed_handler,
            'apiexception': self.api_exception_handler,
            'http404': self.http_404_handler,
            'validationerror': self.validation_error_handler,
        }
        response = exception_handler(exc, context)
        exception_class = exc.__class__.__name__.lower()
        if exception_class in handlers:
            return handlers[exception_class]()
        result['message'] = '{}'.format(exc)
        if response:
            return Response(result, status=response.status_code)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def not_authenticated_handler(self):
        return Response(
            {'status': 'error', 'message': '{}'.format(self.exc)},
            status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def invalid_token_handler():
        return Response(
            {'status': 'error', 'message': 'Некорректный токен авторизации'},
            status.HTTP_400_BAD_REQUEST
        )

    def auth_failed_handler(self):
        return Response(
            {'status': 'error', 'message': self.exc.default_detail},
            status.HTTP_403_FORBIDDEN
        )

    def api_exception_handler(self):
        return Response(
            {'status': 'error', 'message': '{}'.format(self.exc.message)},
            self.exc.status
        )

    @staticmethod
    def http_404_handler():
        return Response(
            {'status': 'error', 'message': 'Объект не найден'},
            status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def validation_error_handler():
        return Response(
            {'status': 'error', 'message': 'Неверные входные данные'},
            status.HTTP_400_BAD_REQUEST
        )

    def add_to_log(self):
        log_record = {
            'traceback': {
                'stack': traceback.format_stack(),
                'data': traceback.format_exc()
            },
            'raw': '{}'.format(self.exc),
            'context': '{}'.format(self.context)
        }
        self.error(log_record)


def core_exception_handler(exc, context):
    """
    Единая точка формирования объектов ошибок для возврата клиентам
    Некоторые ошибки обрабатываются в бизнес-логике, так как или требуют возврата
    дополнительных данных или зависят от контекста и окружения
    """
    handler = ErrorHandler()
    return handler.process(exc, context)
