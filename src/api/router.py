from collections.abc import Callable, Coroutine
from functools import partial
from typing import Any

from fastapi import APIRouter
from fastapi.responses import UJSONResponse
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response

from src.api.middleware.logging.middleware import FastAPILoggingMiddleware


class FastAPILoggingRoute(
    APIRoute,
):
    def get_route_handler(
        self,
    ) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        middleware = FastAPILoggingMiddleware()
        original_route_handler = super().get_route_handler()
        return partial(  # type: ignore
            middleware,
            call_next=original_route_handler,  # type: ignore
        )


class FastAPILoggingRouter(APIRouter):
    route_class = FastAPILoggingRoute
    default_response_class = UJSONResponse

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not kwargs.get('default_response_class'):
            kwargs['default_response_class'] = UJSONResponse

        if not kwargs.get('route_class'):
            kwargs['route_class'] = FastAPILoggingRoute

        super().__init__(*args, **kwargs)
