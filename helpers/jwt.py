from typing import Any

from jose import jwt


def decode_jwt(token: str, key: str, algorithm: str) -> dict[str, Any]:
    payload = jwt.decode(token, key, algorithms=[algorithm])

    return payload


def encode_jwt(key: str, payload: dict[str, Any], algorithm: str) -> str:
    token = jwt.encode(claims=payload, key=key, algorithm=algorithm)
    return token
