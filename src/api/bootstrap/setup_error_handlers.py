from functools import partial

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError as FastAPIResponseValidationError
from fastapi.responses import UJSONResponse
from pydantic import ValidationError as PydanticValidationError
from starlette.requests import Request
from starlette.responses import Response

from src.errors.api import (
    InputValidationError,
    NotFoundError,
    ResponseValidationError,
    ServerError,
    UnknownAnswerError,
    ValidationError,
)


def process_server_error(
    _request: Request,
    exc: ServerError,
    *,
    is_debug: bool,
    old_exc: Exception | None = None,
) -> Response:
    if old_exc and not exc.debug:
        exc.debug = str(old_exc)

    response: UJSONResponse = UJSONResponse(
        content=exc.as_dict(is_debug=is_debug),
        status_code=exc.status_code,
    )

    return response


def _redefine_error(
    _request: Request,
    exc: Exception,
    server_error_instance: ServerError,
    *,
    is_debug: bool,
) -> Response:
    return process_server_error(
        _request=_request,
        exc=server_error_instance,
        is_debug=is_debug,
        old_exc=exc,
    )


def _make_server_error_instance(
    exc_class_or_status_code: int | type[Exception],
    server_error_type: type[ServerError],
) -> ServerError:
    if isinstance(exc_class_or_status_code, int):
        debug_info = f'redefined internal http status {exc_class_or_status_code}'
        return ServerError(debug=debug_info) if not server_error_type else server_error_type(debug=debug_info)

    return ServerError() if not server_error_type else server_error_type()


def _cast_exc_class_or_status_code_to_list(
    exc_class_or_status_codes: int | list[int] | type[Exception] | list[type[Exception]],
) -> list[int | type[Exception]]:
    if not isinstance(exc_class_or_status_codes, list):
        exc_class_or_status_codes = [exc_class_or_status_codes]  # type: ignore
    return exc_class_or_status_codes  # type: ignore


def _redefine_internal_exception(
    app: FastAPI,
    exc_class_or_status_codes: int | list[int] | type[Exception] | list[type[Exception]],
    server_error_type: type[ServerError] | None,
    *,
    is_debug: bool,
) -> None:
    for exc_class_or_status_code in _cast_exc_class_or_status_code_to_list(exc_class_or_status_codes):
        if not server_error_type and isinstance(exc_class_or_status_code, int):
            raise ValueError
        if not server_error_type:
            app.add_exception_handler(
                exc_class_or_status_code=exc_class_or_status_code,
                handler=partial(
                    _redefine_error,
                    is_debug=is_debug,
                    server_error_instance=exc_class_or_status_codes,  # type: ignore
                ),
            )
            continue
        app.add_exception_handler(
            exc_class_or_status_code=exc_class_or_status_code,
            handler=partial(
                _redefine_error,
                is_debug=is_debug,
                server_error_instance=_make_server_error_instance(
                    exc_class_or_status_code=exc_class_or_status_code,
                    server_error_type=server_error_type,
                ),
            ),
        )


def setup_error_handlers(
    app: FastAPI,
    *,
    is_debug: bool,
) -> None:
    app.add_exception_handler(
        exc_class_or_status_code=ServerError,
        handler=partial(
            process_server_error,
            is_debug=is_debug,
        ),
    )
    _redefine_internal_exception(
        app=app,
        is_debug=is_debug,
        exc_class_or_status_codes=RequestValidationError,
        server_error_type=InputValidationError,
    )
    _redefine_internal_exception(
        app=app,
        is_debug=is_debug,
        exc_class_or_status_codes=FastAPIResponseValidationError,
        server_error_type=ResponseValidationError,
    )
    _redefine_internal_exception(
        app=app,
        is_debug=is_debug,
        exc_class_or_status_codes=PydanticValidationError,
        server_error_type=ValidationError,
    )
    _redefine_internal_exception(
        app=app,
        is_debug=is_debug,
        exc_class_or_status_codes=status.HTTP_404_NOT_FOUND,
        server_error_type=NotFoundError,
    )
    _redefine_internal_exception(
        app=app,
        is_debug=is_debug,
        exc_class_or_status_codes=[
            status.HTTP_405_METHOD_NOT_ALLOWED,
        ],
        server_error_type=UnknownAnswerError,
    )
