from collections.abc import Callable
from typing import Any
from uuid import uuid4

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from orjson import orjson  # type: ignore
from pydantic import BaseModel

from src.contextvars import REQUEST_ID


class KafkaConsumerTopicsListeners:
    def __init__(
        self,
    ) -> None:
        self._topic_listeners: dict[str, Callable] = {}  # type: ignore
        self._topic_message_models: dict[str, type[BaseModel]] = {}

    @property
    def topics(
        self,
    ) -> list[str]:
        return list(self._topic_listeners.keys())

    def add_topic_listener(
        self,
        topic: str,
        listener: Callable,  # type: ignore
        message_model: type[BaseModel] | None = None,
    ) -> None:
        self._topic_listeners[topic] = listener
        if message_model:
            self._topic_message_models[topic] = message_model

    def add(
        self,
        topic: str,
        message_model: type[BaseModel] | None = None,
    ) -> Callable:  # type: ignore
        def _wrapper(
            func: Callable,  # type: ignore
        ) -> Callable:  # type: ignore
            self.add_topic_listener(
                topic=topic,
                listener=func,
                message_model=message_model,
            )
            return func

        return _wrapper

    async def process_incoming_message(
        self,
        message: ConsumerRecord,
    ) -> Any:
        REQUEST_ID.set(str(uuid4()))
        if (listener := self._topic_listeners.get(message.topic)) is None:
            return None
        dict_data = orjson.loads(message.value)
        model = self._topic_message_models.get(message.topic)
        data = model.model_validate(dict_data) if model else dict_data
        return await listener(data)

    async def listen(
        self,
        consumer: AIOKafkaConsumer,
    ) -> None:
        async for message in consumer:
            await self.process_incoming_message(message)
