from aiokafka import AIOKafkaProducer
import orjson
from uuid import uuid4
from pydantic import BaseModel
from helpers.contextvars import TRACE_ID
from typing import Any, Dict


class KafkaProducer:
    def __init__(self, kafka_broker: str) -> None:
        """
        Инициализация Kafka Producer.
        :param kafka_broker: Адрес Kafka брокера (например, 'localhost:9092').
        """
        self.kafka_broker = kafka_broker
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Запускает Kafka Producer."""
        self._producer = AIOKafkaProducer(bootstrap_servers=self.kafka_broker)
        await self._producer.start()

    async def stop(self) -> None:
        """Останавливает Kafka Producer."""
        if self._producer:
            await self._producer.stop()

    async def send_message(
            self, topic: str, message: Dict[str, Any], key: str | None = None
    ) -> None:
        """
        Отправляет сообщение в указанный Kafka топик.
        :param topic: Название топика Kafka.
        :param message: Сообщение, которое будет отправлено в топик.
        :param key: (опционально) Ключ для сообщения (по умолчанию None).
        """
        if not self._producer:
            raise RuntimeError("Producer is not started.")
        TRACE_ID.set(str(uuid4()))
        serialized_message = orjson.dumps(message)

        await self._producer.send_and_wait(topic, value=serialized_message, key=key)

    async def send_model_message(
            self, topic: str, model: BaseModel, key: str | None = None
    ) -> None:
        """
        Отправляет модель Pydantic как сообщение в Kafka.
        :param topic: Название топика Kafka.
        :param model: Модель Pydantic, которая будет сериализована и отправлена.
        :param key: (опционально) Ключ для сообщения (по умолчанию None).
        """
        await self.send_message(topic, model.dict(), key)