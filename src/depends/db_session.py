from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.sqlalchemy.client import SQLAlchemyClient


async def get_db_client(request: Request) -> AsyncGenerator[SQLAlchemyClient, None]:
    yield request.state.db_client


async def get_db_session(
    db_client: Annotated[SQLAlchemyClient, Depends(get_db_client)],
) -> AsyncGenerator[AsyncSession, None]:
    session = db_client.get_session()

    try:
        yield session
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await db_client.close_ctx_session()
