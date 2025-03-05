from datetime import datetime
from uuid import UUID

from enum import StrEnum

from pydantic import BaseModel

from helpers.enums.auth import TokenType


class UserStatus(StrEnum):
    NOT_REGISTERED = 'NOT_REGISTERED'
    NOT_VERIFIED = 'NOT_VERIFIED'
    VERIFIED = 'VERIFIED'
    SUSPECTED = 'SUSPECTED'
    BANNED = 'BANNED'


AVAILABLE_USER_STATUSES = [UserStatus.NOT_VERIFIED, UserStatus.VERIFIED, UserStatus.SUSPECTED]


class UserContext(BaseModel):
    user_id: UUID | None
    status: UserStatus | None
    type: TokenType
    exp: datetime
