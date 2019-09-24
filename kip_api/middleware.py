import time
import uuid
from typing import Dict, Callable

from django.core.handlers.wsgi import WSGIRequest
from django.db import connection

from kip_api.mixins import BusMixin


#
# Прослойка для организации мониторинга времен выполнения запросов, включая SQL
# Отправка метрик осуществляется через общую шину данных во избежание задержек
# при отсутствии связи с InfluxDB
#
class MonitoringMiddleware(BusMixin):

    @staticmethod
    def current_time_in_milliseconds() -> int:
        return int(round(time.time() * 1000))

    def __init__(self, get_response: Callable):
        super().__init__()
        self.get_response = get_response

    def send_metrics(self, metrics: Dict) -> None:
        body = {
            'uuid': self.id,
            'metrics': metrics
        }
        self.send_message_to_bus('metrics', body)

    def send_request_metrics(self):
        # Формируем метрику по сетевому запросу
        metrics = {
            'measurement': 'request_duration',
            'tags': {
                'host': self.request.get_host(),
            },
            'fields': {
                'endpoint': self.request.path,
                'uuid': self.id,
                'value': self.current_time_in_milliseconds() - self.start_time,
            }
        }
        self.send_metrics(metrics)

    def send_http_errors_metrics(self):
        # Формируем метрику по ошибкам
        if self.response.status_code < 400:
            return
        metrics = {
            'measurement': 'http_error',
            'tags': {
                'host': self.request.get_host(),
            },
            'fields': {
                'endpoint': self.request.path,
                'uuid': self.id,
                'value': self.response.status_code
            }
        }
        self.send_metrics(metrics)

    def send_sql_metrics(self):
        # Формируем метрику по SQL-запросам
        if connection.queries:
            sql_total_time = 0
            for query in connection.queries:
                query_time = query.get('time')
                if query_time is None:
                    query_time = query.get('duration', 0) / 1000
                sql_total_time += float(query_time)
            sql_metrics = {
                'measurement': 'sql_duration_for_request',
                'tags': {
                    'host': self.request.get_host(),
                },
                'fields': {
                    'related_to': self.id,
                    'value': sql_total_time,
                    'count': len(connection.queries)
                }
            }
            self.send_metrics(sql_metrics)

    def __call__(self, request: WSGIRequest):
        self.start_time = self.current_time_in_milliseconds()
        self.id = str(uuid.uuid4())
        self.request = request
        self.response = self.get_response(self.request)

        # Отправляем метрику по сетевому запросу
        self.send_request_metrics()
        # Отправляем метрику по SQL-запросам в привязке к сетевому запросу
        self.send_sql_metrics()
        # Отправляем метрику по ошибкам
        self.send_http_errors_metrics()
        return self.response
