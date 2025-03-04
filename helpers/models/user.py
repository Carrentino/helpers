from enum import StrEnum

from pydantic import BaseModel


class UserStatus(StrEnum):
    NOT_REGISTERED = 'NOT_REGISTERED'
    NOT_VERIFIED = 'NOT_VERIFIED'
    VERIFIED = 'VERIFIED'
    SUSPECTED = 'SUSPECTED'
    BANNED = 'BANNED'


class UserContext(BaseModel):
    user_id: int
    status: UserStatus
