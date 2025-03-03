from abc import ABC
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.sqlalchemy.base_model import Base


class ISqlAlchemyRepository[Model: Base](ABC):
    _model: type[Model]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, db_object: Model) -> UUID | int:
        self.session.add(db_object)
        await self.session.flush()
        return db_object.id

    async def create_many(self, db_objects: list[Model]) -> list[UUID | int]:
        self.session.add_all(db_objects)
        await self.session.flush()
        return [db_object.id for db_object in db_objects]

    async def get_one_by(self, **kwargs: Any) -> Model | None:
        query = select(self._model).filter_by(**kwargs).limit(1)
        result = await self.session.scalar(query)
        return result

    async def get(self, obj_id: UUID | int) -> Model | None:
        db_object = await self.session.get(self._model, obj_id)
        return db_object

    async def get_list(self, ids: list[UUID | int] | None = None, **filters: Any) -> list[Model]:
        query = select(self._model)

        if ids:
            query = query.where(self._model.id.in_(ids))

        if filters:
            query = query.filter_by(**filters)

        db_objects = await self.session.scalars(query)
        return list(db_objects.all())

    async def update(self, identifier: UUID | int, **kwargs: Any) -> None:
        await self.session.execute(update(self._model).where(self._model.id == identifier).values(kwargs))

    async def update_object(self, db_object: Model) -> None:
        self.session.add(db_object)
        await self.session.flush()
        await self.session.refresh(db_object)

    async def delete(self, obj_id: UUID | int) -> None:
        db_object = await self.session.get(self._model, obj_id)
        if db_object:
            await self.session.delete(db_object)
