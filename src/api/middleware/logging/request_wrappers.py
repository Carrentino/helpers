from contextlib import suppress
from json import JSONDecodeError

from fastapi import Request, Response
from starlette.datastructures import UploadFile

from src.api.middleware.logging.constants import (
    LOGGING_REQUEST_METHODS_WITHOUT_BODY,
)
from src.json import dump_json


class FastAPIRequestWrapper:
    _request_object: Request

    def __init__(
        self,
        request_object: Request,
    ) -> None:
        self._request_object = request_object

    @property
    def headers(
        self,
    ) -> str | None:
        return dump_json(dict(self._request_object.headers))

    async def get_input_data(
        self,
    ) -> str | None:
        input_data = None
        if self._request_object.method.upper() not in LOGGING_REQUEST_METHODS_WITHOUT_BODY:
            with suppress(
                UnicodeDecodeError,
                RuntimeError,
                JSONDecodeError,
            ):
                input_data = await self._request_object.json()
        if params := self._request_object.query_params:
            input_data = input_data or {}
            input_data.update(params._dict)  # noqa

        if form := await self._request_object.form():
            input_data = input_data or {}
            form_file_names = []
            for item in form._list:
                if isinstance(item[1], UploadFile):
                    form_file_names.append(str(item[1].filename))
                    continue
                input_data.update({item[0]: item[1]})
            input_data.update({'files': form_file_names})

        return dump_json(input_data) if input_data else None

    @property
    def http_method(
        self,
    ) -> str | None:
        return self._request_object.method.upper()

    @property
    def method(
        self,
    ) -> str | None:
        return str(self._request_object.url.path)

    @property
    def path(self) -> str:
        return self._request_object.url.path


class FastAPIResponseWrapper:
    _response_object: Response

    def __init__(
        self,
        response_object: Response,
    ) -> None:
        self._response_object = response_object

    @property
    def headers(
        self,
    ) -> str:
        return dump_json(dict(self._response_object.headers))

    @property
    def output_data(
        self,
    ) -> str | None:
        output_data = None
        if not self._response_object.body:
            return output_data
        with suppress(
            UnicodeDecodeError,
        ):
            output_data = self._response_object.body.decode()  # type: ignore
        return dump_json(output_data) if output_data else None

    @property
    def status_code(
        self,
    ) -> int:
        return self._response_object.status_code
