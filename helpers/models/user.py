from datetime import datetime

from enum import StrEnum

from pydantic import BaseModel

from helpers.enums.auth import TokenType


class UserStatus(StrEnum):
    NOT_VERIFIED = 'Не верифицирован'
    VERIFIED = 'Верифицирован'
    SUSPECTED = 'Подозреваемый'
    BANNED = 'Заблокирован'


AVAILABLE_USER_STATUSES = [UserStatus.NOT_VERIFIED, UserStatus.VERIFIED, UserStatus.SUSPECTED]


class UserContext(BaseModel):
    user_id: str | None
    status: UserStatus | None
    type: TokenType
    exp: datetime
