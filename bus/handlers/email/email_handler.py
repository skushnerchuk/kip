import asyncio
import json
import os
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aio_pika

# Для импорта глобальных миксин следует подключить этот файл сюда через символическую ссылку, например так:
#   ln -s ~/dev/projects/kip/kip/global_mixins.py global_mixins.py
from .global_mixins import LoggingMixin

USER = os.getenv("RMQ_USER", "guest")
PASSWORD = os.getenv("RMQ_PASSWORD", "guest")
HOST = os.getenv("RMQ_HOST", "127.0.0.1")

EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', 30))


class Email(LoggingMixin):
    """
    Отправка электронной почты
    Отправка вложений пока не поддерживается
    """

    @staticmethod
    def send_html_email(message):
        """
        Отправка писем в формате HTML
        :param message:
        :return:
        """
        msg = MIMEMultipart("alternative")
        msg['Subject'] = message['subject']
        msg['From'] = message['sender']
        msg['To'] = ', '.join(message['receivers'])
        msg.attach(MIMEText(message['body'], "html"))
        with smtplib.SMTP(host=EMAIL_HOST, port=EMAIL_PORT) as s:
            s.login(user=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD)
            s.sendmail(msg['From'], msg['To'], msg.as_string())

    def send(self, message_body):
        """
        Отправка письма
        :param message_body: строка с json-описанием сообщения
        """
        try:
            message = json.loads(message_body)
            # Прикапываем в логах отправленное письмо
            self.info(message)
            self.send_html_email(message)
        except Exception as exc:
            # Конечно не хорошо ловить все подряд, но мы это делаем для
            # того чтгобы все отправить в лог
            log_record = {
                'traceback': {
                    'stack': traceback.format_stack(),
                    'data': traceback.format_exc()
                },
                'raw': '{}'.format(exc)
            }
            self.error(log_record)


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
                    e.send(message.body)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
