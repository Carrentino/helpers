from typing import Any

from helpers.models.response import PaginatedResponse


async def get_paginated_response(data: list[Any], limit: int = 100, offset: int = 0) -> PaginatedResponse:
    page = offset // limit
    return PaginatedResponse(
        page=page,
        size=limit,
        total=len(data),
        total_pages=len(data) // limit,
        data=data,
    )