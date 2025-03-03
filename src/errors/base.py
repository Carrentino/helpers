from typing import Any


class BaseError(Exception):
    message: str | None
    debug: str | None

    def __init__(
        self,
        message: str | None = None,
        debug: str | None = None,
    ):
        self.message = message or self.message
        self.debug = debug
        super().__init__()

    @property
    def title(self) -> str:
        return self.__class__.__name__

    def as_dict(self, *, is_debug: bool = False) -> dict[str, Any]:
        debug = {'debug': self.debug} if is_debug else {}
        return dict(
            title=self.title,
            message=self.message,
            **debug,
        )


class ServerError(BaseError):
    status_code: int = 520
    message: str = 'Внутренняя ошибка сервера'
