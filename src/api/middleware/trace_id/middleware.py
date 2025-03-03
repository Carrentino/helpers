from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.api.middleware.trace_id.constants import DEFAULT_TRACE_ID_HEADER_NAME
from src.contextvars import TRACE_ID


class TraceIdMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        trace_id_header_name: str = DEFAULT_TRACE_ID_HEADER_NAME,
    ) -> None:
        super().__init__(app=app)
        self.trace_id_header_name = trace_id_header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        current_trace = request.headers.get(self.trace_id_header_name, str(uuid4()))
        TRACE_ID.set(current_trace)

        response = await call_next(request)

        response.headers[self.trace_id_header_name] = current_trace
        return response
