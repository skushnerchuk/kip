#
# Обработчик событий отправки почты
# Эксперимент в async/await
# Мое предпочтение в синхронной парадигме - AMQPStorm
#

import asyncio
import json
import os
import logging
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aio_pika
import aiosmtplib
from dotenv import load_dotenv

from common.global_mixins import LoggingMixin

DEBUG = int(os.getenv('DEBUG', 1))
LOGGING_LEVEL = int(os.getenv('LOGGING_LEVEL', logging.DEBUG))

logging.basicConfig(
    level=LOGGING_LEVEL,
    handlers=[logging.StreamHandler(sys.stdout)],
    format='%(message)s'
)

if DEBUG:
    load_dotenv('email.env')
USER = os.getenv('RMQ_USER', 'guest')
PASSWORD = os.getenv('RMQ_PASSWORD', 'guest')
HOST = os.getenv('RMQ_HOST', '127.0.0.1')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'admin')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'admin')
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', 30))


class Email(LoggingMixin):
    """
    Отправка электронной почты
    Отправка вложений пока не поддерживается
    """

    @staticmethod
    async def send_html_email(message):
        """
        Отправка писем в формате HTML
        """
        msg = MIMEMultipart("alternative")
        msg['Subject'] = message['subject']
        msg['From'] = message['sender']
        msg['To'] = ', '.join(message['receivers'])
        msg.attach(MIMEText(message['body'], "html"))

        s = aiosmtplib.SMTP(hostname=EMAIL_HOST, port=EMAIL_PORT, loop=loop)
        try:
            await s.connect()
            await s.login(username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD)
            await s.sendmail(msg['From'], msg['To'], msg.as_string(), timeout=EMAIL_TIMEOUT)
        finally:
            s.close()

    async def send(self, message_body):
        """
        Отправка письма
        :param message_body: строка с json-описанием сообщения
        """
        try:
            message = json.loads(message_body)
            await self.send_html_email(message)
            # Прикапываем в логах отправленное письмо
            self.info(message)
        except Exception as exc:
            # Конечно не хорошо ловить все подряд, но мы это делаем для
            # того чтобы все отправить в лог
            self.error(self.create_exception_record(exc))


async def main(loop):
    connection = await aio_pika.connect_robust(
        "amqp://{}:{}@{}/".format(USER, PASSWORD, HOST),
        loop=loop
    )

    queue_name = "emails"

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
                    e = Email()
                    await e.send(message.body)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
