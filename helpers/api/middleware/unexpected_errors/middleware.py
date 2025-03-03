from traceback import format_exc, print_exc
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from helpers.api.bootstrap.setup_error_handlers import process_server_error
from helpers.errors import ServerError


class ErrorsHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        **kwargs: Any,
    ) -> None:
        super().__init__(app)
        self.is_debug = kwargs.get('is_debug', False)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        try:
            return await call_next(request)
        except ServerError as exc:
            return process_server_error(
                _request=request,
                exc=exc,
                is_debug=self.is_debug,
            )
        except Exception:
            print_exc()
            return process_server_error(
                _request=request,
                exc=ServerError(debug=format_exc()),
                is_debug=self.is_debug,
            )
