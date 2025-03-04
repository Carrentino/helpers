import uuid
from datetime import datetime

from sqlalchemy import MetaData, func, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

CONSTRAINT_NAMING_CONVENTIONS = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}



class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONSTRAINT_NAMING_CONVENTIONS)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[datetime] = mapped_column(
        insert_default=lambda: datetime.now(),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        insert_default=lambda: datetime.now(),
        server_default=func.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return str(self.__dict__)
