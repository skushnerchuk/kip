import os

import asyncio
import aio_pika

USER = os.getenv("RMQ_USER", "guest")
PASSWORD = os.getenv("RMQ_PASSWORD", "guest")
HOST = os.getenv("RMQ_HOST", "127.0.0.1")


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
                    print(message.body)

                    if queue.name in message.body.decode():
                        break


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
