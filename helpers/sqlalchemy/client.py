from pydantic import PostgresDsn
from sqlalchemy import AsyncAdaptedQueuePool, text
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)

from helpers.contextvars import TRACE_ID
from helpers.sqlalchemy.base_model import Base


class SQLAlchemyClient:
    def __init__(self, dsn: PostgresDsn) -> None:
        self._engine = create_async_engine(
            url=dsn.unicode_string(),
            poolclass=AsyncAdaptedQueuePool,
            pool_pre_ping=True,
            echo=True,
        )
        self._ctx_session_manager = async_scoped_session(
            async_sessionmaker(autoflush=True, expire_on_commit=False, bind=self._engine),
            scopefunc=TRACE_ID.get,
        )

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._ctx_session_manager.session_factory

    def get_session(self) -> AsyncSession:
        return self._ctx_session_manager()

    async def close_ctx_session(self) -> None:
        await self._ctx_session_manager.remove()

    async def close(self) -> None:
        await self._engine.dispose()

    async def drop_all_tables(self) -> None:
        metadata = Base.metadata
        async with self._engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)

    async def create_all_tables(self) -> None:
        metadata = Base.metadata
        async with self._engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def create_database(self, dsn: PostgresDsn) -> None:
        db_url = dsn

        if dsn.path is None:
            raise ValueError('Database name must be provided')

        original_db_name = dsn.path.replace('/', '')

        postgres_db_engine = create_async_engine(
            db_url.unicode_string().replace(db_url.path, '/postgres'),  # type: ignore
            isolation_level='AUTOCOMMIT',
        )

        async with postgres_db_engine.connect() as conn:
            database_existence = await conn.execute(
                text(
                    f"SELECT 1 FROM pg_database WHERE datname='{original_db_name}'",  # noqa: S608
                ),
            )
            database_exists = database_existence.scalar() == 1

            if not database_exists:
                await conn.execute(
                    text(
                        f'CREATE DATABASE "{original_db_name}" ENCODING "utf8" TEMPLATE template1',  # noqa: E501
                    ),
                )
        await postgres_db_engine.dispose()

    @staticmethod
    async def drop_database(dsn: PostgresDsn) -> None:
        db_url = dsn

        if dsn.path is None:
            raise ValueError('Database name must be provided')

        original_db_name = dsn.path.replace('/', '')

        postgres_db_engine = create_async_engine(
            db_url.unicode_string().replace(db_url.path, '/postgres'),  # type: ignore
            isolation_level='AUTOCOMMIT',
        )

        async with postgres_db_engine.connect() as conn:
            database_existence = await conn.execute(
                text(
                    f"SELECT 1 FROM pg_database WHERE datname='{original_db_name}'",  # noqa: S608
                ),
            )
            database_exists = database_existence.scalar() == 1

        if database_exists:
            async with postgres_db_engine.connect() as conn:
                disc_users = (
                    'SELECT pg_terminate_backend(pg_stat_activity.pid) '  # noqa: S608
                    'FROM pg_stat_activity '
                    f"WHERE pg_stat_activity.datname = '{original_db_name}' "
                    'AND pid <> pg_backend_pid();'
                )
                await conn.execute(text(disc_users))
                await conn.execute(text(f'DROP DATABASE "{original_db_name}"'))
