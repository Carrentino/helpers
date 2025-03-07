from typing import Any

from pydantic import BaseModel


class FilterOperator(BaseModel):
    eq: Any = None
    ne: Any = None
    gt: Any = None
    lt: Any = None
    gte: Any = None
    lte: Any = None