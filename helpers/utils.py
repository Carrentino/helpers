from typing import Any

from helpers.models.response import PaginatedResponse


async def get_paginated_response(data: list[Any], limit: int = 100, offset: int = 0) -> PaginatedResponse:
    return PaginatedResponse(
        page=offset // limit + 1,
        size=limit,
        total=len(data),
        total_pages=len(data) // limit + 1,
        data=data,
    )