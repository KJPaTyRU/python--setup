from functools import cache
from typing import TypeVar
from fastapi import Depends, Query, params
from pydantic import BaseModel, create_model
from pydantic_core import PydanticUndefined


def inject_query(schema: type[BaseModel]):
    """
    Just check default value types and force them into the fastapi.Query
    """
    for k, v in schema.model_fields.items():
        if v.default is not PydanticUndefined:
            if isinstance(v.default, params.Query):
                v.default = v.default
            else:
                v.default = Query(v.default)
        elif v.default_factory is None:
            continue
        elif v.default_factory is not PydanticUndefined:
            if isinstance(v.default_factory, params.Query):
                v.default_factory = v.default_factory
            else:
                v.default_factory = Query(default_factory=v.default_factory)


FilterT = TypeVar("FilterT", bound=BaseModel)


@cache
def FilterDepends(schema: type[FilterT]) -> FilterT:
    queried_schema = create_model("Query" + schema.__name__, __base__=schema)
    inject_query(queried_schema)

    def get_schema(filters: queried_schema = Depends()) -> FilterT:
        return filters

    return Depends(get_schema, use_cache=True)
