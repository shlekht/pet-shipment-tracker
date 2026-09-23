import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractQueue,
    AbstractRobustConnection,
)


class RabbitMQ:
    def __init__(self, url: str):
        self.url = url
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self.exchange: AbstractExchange | None = None
        self.queue: AbstractQueue | None = None

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(url=self.url)
        self.channel = await self.connection.channel()


    async def close(self) -> None:
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    # Kombu (Celery) по умолчанию сам создаёт exchange/queue/binding в RabbitMQ, поэтому я здесь не создаю exchange, queue и т.п.
    # Kombu:
    # - создаcт direct exchange "celery"
    # - создаcт queue "celery"
    # - забиндит очередь с routing_key "celery"
