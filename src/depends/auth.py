from typing import Annotated

from fastapi import Depends
from pydantic import ValidationError
from starlette.requests import Request

from src.contextvars import USER_CTX
from src.errors.auth import AccessForbiddenError, InvalidTokenError
from src.models.user import UserContext, UserStatus


async def get_current_user(request: Request) -> UserContext:
    payload = request.scope.get('auth_token_payload')

    if not payload:
        raise InvalidTokenError

    try:
        user_model = UserContext.model_validate(payload)
    except ValidationError as err:
        raise InvalidTokenError from err

    USER_CTX.set(user_model)

    return user_model


async def get_active_user(user: Annotated[UserContext, Depends(get_current_user)]) -> UserContext | None:
    if user.status != UserStatus.ACTIVE:
        raise AccessForbiddenError

    return user
