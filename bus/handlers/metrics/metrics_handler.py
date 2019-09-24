#
# Обработчик событий отправки метрик
#

import asyncio
import json
import logging
import os
import sys

import aio_pika
from aioinflux import InfluxDBClient
from dotenv import load_dotenv

from common.global_mixins import LoggingMixin

DEBUG = int(os.getenv('DEBUG', 1))
if DEBUG:
    load_dotenv('metrics.env')

LOGGING_LEVEL = int(os.getenv('LOGGING_LEVEL', logging.DEBUG))
USER = os.getenv('RMQ_USER', 'guest')
PASSWORD = os.getenv('RMQ_PASSWORD', 'guest')
HOST = os.getenv('RMQ_HOST', '127.0.0.1')
INFLUX_HOST = os.getenv('INFLUX_HOST', '127.0.0.1')
INFLUX_DB = os.getenv('INFLUX_DB', '127.0.0.1')

logging.basicConfig(
    level=LOGGING_LEVEL,
    handlers=[logging.StreamHandler(sys.stdout)],
    format='%(message)s'
)


class Metrics(LoggingMixin):
    """
    Отправка метрик в систему мониторинга
    """

    @staticmethod
    async def send_metrics(metrics):
        """
        Отправка метрик в InfluxDB
        """
        async with InfluxDBClient(db=INFLUX_DB) as client:
            await client.write(metrics)

    async def send(self, metrics):
        """
        Отправка метрик
        :param metrics: строка с json-описанием метрик
        """
        try:
            message = json.loads(metrics)
            await self.send_metrics(message['metrics'])
        except Exception as exc:
            # Конечно не хорошо ловить все подряд, но мы это делаем для
            # того чтобы все отправить в лог
            self.error(self.create_exception_record(exc))


async def main(loop):
    async with InfluxDBClient(host=INFLUX_HOST, db=INFLUX_DB) as client:
        await client.create_database(db=INFLUX_DB)

    connection = await aio_pika.connect_robust(
        "amqp://{}:{}@{}/".format(USER, PASSWORD, HOST),
        loop=loop
    )

    queue_name = "metrics"

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(
            queue_name,
            auto_delete=False,
            durable=True,
            passive=True
        )
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    e = Metrics()
                    await e.send(message.body)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
