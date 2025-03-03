import contextlib

from fastapi import FastAPI
from jose import JOSEError
from pydantic import SecretStr
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.api.middleware.auth.constants import DEFAULT_ALGORITHM, DEFAULT_TOKEN_HEADER_NAME
from src.jwt import decode_jwt


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        key: SecretStr,
        algorithm: str = DEFAULT_ALGORITHM,
        token_header_name: str = DEFAULT_TOKEN_HEADER_NAME,  # noqa: S107
    ) -> None:
        super().__init__(app=app)
        self.token_header_name = token_header_name
        self.key = key
        self.algorithm = algorithm

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = request.headers.get(self.token_header_name, '')

        with contextlib.suppress(JOSEError):
            payload = decode_jwt(token, self.key.get_secret_value(), self.algorithm)
            request.scope['auth_token_payload'] = payload

        response = await call_next(request)
        return response
