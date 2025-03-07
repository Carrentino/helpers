from typing import Any

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int
    data: list[Any]
