from __future__ import annotations

import asyncio
import inspect
from asyncio import Task
from typing import Any, TYPE_CHECKING

from factory import FactoryError
from factory.alchemy import (
    SESSION_PERSISTENCE_COMMIT,
    SESSION_PERSISTENCE_FLUSH,
    SQLAlchemyModelFactory,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.sqlalchemy.base_model import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AsyncSQLAlchemyFactory[Model: Base](SQLAlchemyModelFactory):
    @classmethod
    async def create(cls, **kwargs: Any) -> Any:
        session_factory = cls._meta.sqlalchemy_session_factory
        if session_factory:
            cls._meta.sqlalchemy_session = session_factory()

        session = cls._meta.sqlalchemy_session
        instance = await super().create(**kwargs)
        session_persistence = cls._meta.sqlalchemy_session_persistence

        if session_persistence == SESSION_PERSISTENCE_FLUSH:
            await session.flush()
        elif session_persistence == SESSION_PERSISTENCE_COMMIT:
            await session.commit()

        return instance

    @classmethod
    async def create_batch(cls, size: int, **kwargs: Any) -> list[Any]:
        return [await cls.create(**kwargs) for _ in range(size)]

    @classmethod
    async def _get_or_create(cls, model_class: Model, session: AsyncSession, *args: Any, **kwargs: Any) -> Any:
        key_fields = {}
        for field in cls._meta.sqlalchemy_get_or_create:
            if field not in kwargs:
                raise FactoryError(
                    'sqlalchemy_get_or_create - '
                    f"Unable to find initialization value for '{field}' in factory {cls.__name__}"
                )
            key_fields[field] = kwargs.pop(field)

        obj = (await session.execute(select(model_class).filter_by(**key_fields))).scalars().first()  # type: ignore

        if not obj:
            try:
                obj = await cls._save(model_class, session, *args, **key_fields, **kwargs)
            except IntegrityError as err:
                await session.rollback()
                get_or_create_params = {
                    lookup: value
                    for lookup, value in cls._original_params.items()
                    if lookup in cls._meta.sqlalchemy_get_or_create
                }
                if get_or_create_params:
                    try:
                        obj = (
                            (
                                await session.execute(
                                    select(model_class).filter_by(**get_or_create_params),  # type: ignore
                                )
                            )
                            .scalars()
                            .one()
                        )
                    except NoResultFound as inner_err:
                        raise err from inner_err
                else:
                    raise

        return obj

    @classmethod
    def _create(cls, model_class: Model, *args: Any, **kwargs: Any) -> Task[Any]:
        session_factory = cls._meta.sqlalchemy_session_factory
        if session_factory:
            cls._meta.sqlalchemy_session = session_factory()

        session = cls._meta.sqlalchemy_session

        async def async_create() -> Any:
            for key, value in kwargs.items():
                if inspect.isawaitable(value):
                    kwargs[key] = await value

            if cls._meta.sqlalchemy_get_or_create:
                return await cls._get_or_create(model_class, session, *args, **kwargs)
            return await cls._save(model_class, session, *args, **kwargs)

        return asyncio.create_task(async_create())

    @classmethod
    async def _save(cls, model_class: Model, session: AsyncSession, *args: Any, **kwargs: Any) -> Model:
        obj = model_class(*args, **kwargs)  # type: ignore # noqa

        session.add(obj)

        if cls._meta.sqlalchemy_session_persistence == SESSION_PERSISTENCE_FLUSH:
            await session.flush()
        elif cls._meta.sqlalchemy_session_persistence == SESSION_PERSISTENCE_COMMIT:
            await session.commit()

        return obj
