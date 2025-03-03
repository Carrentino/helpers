from collections.abc import Generator
from uuid import uuid4

import pytest

from src.contextvars import TRACE_ID


@pytest.fixture(autouse=True)
def ensure_testing_trace_id() -> Generator[str, None, None]:
    token = TRACE_ID.set(str(uuid4()))
    yield TRACE_ID.get()
    TRACE_ID.reset(token)
