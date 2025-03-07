from typing import Any

from helpers.models.response import PaginatedResponse


async def get_paginated_response(data: list[Any], count: int, limit: int = 100, offset: int = 0) -> PaginatedResponse:
    return PaginatedResponse(
        page=offset // limit if offset % limit == 0 else offset // limit + 1,
        size=limit,
        total=count,
        total_pages=count // limit if count % limit == 0 else count // limit + 1,
        data=data,
    )