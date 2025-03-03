from enum import StrEnum

from pydantic import BaseModel


class UserStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    GUEST = 'GUEST'


class UserContext(BaseModel):
    user_id: int
    status: UserStatus
    subscription: int
