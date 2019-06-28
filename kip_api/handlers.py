import datetime
import logging
import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)




def log(exc, context):
    log_record = {
        'fired': datetime.datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S.%f"),
        'traceback': {
            'stack': traceback.format_stack(),
            'data': traceback.format_exc()
        },
        'raw': '{}'.format(exc),
        'context': '{}'.format(context)
    }
    logger.error(log_record)


def core_exception_handler(exc, context):
    """
    Единая точка формирования объектов ошибок для возврата клиентам
    Некоторые ошибки обрабатываются в бизнес-логике, так как или требуют возврата
    дополнительных данных или зависят от контекста и окружения
    """
    log(exc)

    result = {'status': 'error', 'message': ''}
    handlers = {
        'notauthenticated': not_authenticated_handler,
        'invalidtoken': invalid_token_handler,
        'authenticationfailed': auth_failed_handler,
        'apiexception': api_exception_handler,
        'http404': http_404_handler,
        'validationerror': validation_error_handler,
    }
    response = exception_handler(exc, context)
    exception_class = exc.__class__.__name__.lower()
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    result['message'] = '{}'.format(exc)
    if response:
        return Response(result, status=response.status_code)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def not_authenticated_handler(exc, context, response):
    return Response({'status': 'error', 'message': '{}'.format(exc)}, status.HTTP_401_UNAUTHORIZED)


def invalid_token_handler(exc, context, response):
    return Response({'status': 'error', 'message': 'Некорректный токен авторизации'}, status.HTTP_400_BAD_REQUEST)


def auth_failed_handler(exc, context, response):
    return Response({'status': 'error', 'message': exc.default_detail}, status.HTTP_403_FORBIDDEN)


def api_exception_handler(exc, context, response):
    return Response({'status': 'error', 'message': '{}'.format(exc.message)}, exc.status)


def http_404_handler(exc, context, response):
    return Response({'status': 'error', 'message': 'Объект не найден'}, status.HTTP_404_NOT_FOUND)


def validation_error_handler(exc, context, response):
    return Response({'status': 'error', 'message': 'Неверные входные данные'}, status.HTTP_400_BAD_REQUEST)
