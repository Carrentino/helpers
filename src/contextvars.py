from contextvars import ContextVar

from src.models.user import UserContext

TRACE_ID: ContextVar[str] = ContextVar('TRACE_ID', default='default_trace_id')
USER_CTX: ContextVar[UserContext | None] = ContextVar('USER_CTX', default=None)
