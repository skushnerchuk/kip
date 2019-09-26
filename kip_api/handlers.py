import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from sentry_sdk import capture_message

from common.global_mixins import LoggingMixin


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
            'parseerror': self.validation_error_handler,
            'tokenerror': self.token_error_handler,
            'validationerror': self.validation_error_handler,
        }
        response = exception_handler(exc, context)
        exception_class = exc.__class__.__name__.lower()
        if exception_class in handlers:
            return handlers[exception_class]()
        result['message'] = '{}'.format(exc)
        if response:
            return Response(result, status=response.status_code,
                            content_type='application/json')
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content_type='application/json')

    def not_authenticated_handler(self):
        return Response(
            {'status': 'error', 'message': '{}'.format(self.exc)},
            status.HTTP_401_UNAUTHORIZED,
            content_type='application/json'
        )

    @staticmethod
    def invalid_token_handler():
        return Response(
            {'status': 'error', 'message': 'Некорректный токен авторизации'},
            status.HTTP_401_UNAUTHORIZED,
            content_type='application/json'
        )

    def auth_failed_handler(self):
        return Response(
            {'status': 'error', 'message': self.exc.default_detail},
            status.HTTP_403_FORBIDDEN,
            content_type='application/json'
        )

    def api_exception_handler(self):
        capture_message('API exception', level='error')
        return Response(
            {'status': 'error', 'message': '{}'.format(self.exc.message)},
            self.exc.status,
            content_type='application/json'
        )

    @staticmethod
    def http_404_handler():
        capture_message('Object not found', level='error')
        return Response(
            {'status': 'error', 'message': 'Объект не найден'},
            status.HTTP_404_NOT_FOUND,
            content_type='application/json'
        )

    def validation_error_handler(self):
        return Response(
            {'status': 'error', 'message': f'Неверные входные данные: {self.exc.message}'},
            status.HTTP_400_BAD_REQUEST,
            content_type='application/json'
        )

    @staticmethod
    def token_error_handler():
        return Response(
            {'status': 'error', 'message': 'Передан неверный токен'},
            status.HTTP_400_BAD_REQUEST,
            content_type='application/json'
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
