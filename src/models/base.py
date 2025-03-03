from abc import ABC

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_pascal


class CamelAliasBaseModel(BaseModel, ABC):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class BasePascalModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
