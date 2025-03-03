from abc import ABC
from collections.abc import Awaitable, Callable, Sequence
from contextlib import suppress
from time import time

from loguru import logger

from helpers.api.middleware.logging.constants import (
    LOGGING_SUBSTRINGS_OF_ROUTES_FOR_SKIP,
)
from helpers.api.middleware.logging.request_wrappers import FastAPIRequestWrapper, FastAPIResponseWrapper
from helpers.errors import ServerError


class LoggingMiddlewareBase(
    ABC,
):
    request_cls: type[FastAPIRequestWrapper]  # type: ignore
    response_cls: type[FastAPIResponseWrapper]  # type: ignore
    logging_substrings_of_routes_for_skip: Sequence[str] = ()
    destination: str = 'UNSET'

    async def __call__(
        self,
        request: object,
        call_next: Callable[[object], Awaitable[object]],
    ) -> object:
        wrapped_request: FastAPIRequestWrapper = self.request_cls(request)  # type: ignore
        wrapped_response: FastAPIResponseWrapper | None = None  # type: ignore
        http_status_code = None
        start_time = time()
        error = None

        try:
            response = await call_next(request)
            wrapped_response = self.response_cls(response)  # type: ignore
            http_status_code = wrapped_response.status_code  # type: ignore
            return response  # noqa: TRY300
        except ServerError as exc:
            error = exc
            if not http_status_code:
                http_status_code = exc.status_code
            raise
        except Exception as exc:
            error = exc  # type: ignore
            raise
        finally:
            with suppress(Exception):
                if error:
                    error_title = error.title if isinstance(error, ServerError) else error.__class__.__name__
                    error_message = error.message if isinstance(error, ServerError) else str(error)

                if not any(
                    substring
                    for substring in self.logging_substrings_of_routes_for_skip
                    if substring in wrapped_request.path
                ):
                    logger.info(
                        {
                            'destination': self.destination,
                            'http_method': wrapped_request.http_method,
                            'method': wrapped_request.method,
                            'processing_time': time() - start_time,
                            'http_status_code': http_status_code,
                            'input_data': await wrapped_request.get_input_data(),
                            'output_data': wrapped_response.output_data if wrapped_response else None,
                            'request_headers': wrapped_request.headers,
                            'response_headers': wrapped_response.headers if wrapped_response else None,
                            'error_title': error_title,
                            'error_message': error_message,
                        },
                    )


class FastAPILoggingMiddleware(
    LoggingMiddlewareBase,
):
    logging_substrings_of_routes_for_skip = LOGGING_SUBSTRINGS_OF_ROUTES_FOR_SKIP  # type: ignore
    request_cls = FastAPIRequestWrapper
    response_cls = FastAPIResponseWrapper


def setup_logger_middleware(
    destination: str,
    logging_substrings_of_routes_for_skip: Sequence[str],
) -> None:
    FastAPILoggingMiddleware.destination = destination
    FastAPILoggingMiddleware.logging_substrings_of_routes_for_skip = logging_substrings_of_routes_for_skip  # type: ignore
