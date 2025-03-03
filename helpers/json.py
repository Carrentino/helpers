from typing import Any

import orjson


def dump_json(
    data: str | dict[str, Any] | list[dict[str, Any]],
    default: Any = None,
) -> str:
    if isinstance(data, str):
        return data

    option = orjson.OPT_NON_STR_KEYS | orjson.OPT_SORT_KEYS
    return orjson.dumps(
        data,
        default=default,
        option=option,
    ).decode()
