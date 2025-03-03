from helpers.errors import ServerError


class TokenNotFoundError(ServerError):
    status_code: int = 401
    message: str = 'Auth token not found in request headers'


class InvalidTokenError(ServerError):
    status_code: int = 401
    message: str = 'Invalid auth token'


class AccessForbiddenError(ServerError):
    status_code: int = 403
    message: str = 'Access denied'
