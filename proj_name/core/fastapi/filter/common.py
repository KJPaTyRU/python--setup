from dataclasses import dataclass, field as dc_field
from typing import Any
from sqlalchemy import Select, Table, ColumnExpressionArgument
from sqlalchemy.orm import DeclarativeBase

SQLWhereType = ColumnExpressionArgument[bool]
SQLOrderByType = ColumnExpressionArgument[Any]


class KeyType:
    def __init__(self, raw_key: str):
        self.raw_key = raw_key
        self.column_key: str = ""
        self.columns: list[str] = []
        self.operator: str = ""

        datas = self.raw_key.split("__")
        if len(datas) == 1:
            self.column_key = datas[0]
            self.columns = []
        elif len(datas) >= 2:
            self.column_key = datas[-2]
            self.columns = datas[:-1]
            self.operator = datas[-1]
        else:
            raise ValueError("Got bad raw_key `{}`", self.raw_key)


@dataclass
class FilterContext:
    # NOTE: If there is an easy way to convert untyped dict to object
    # u can pass it as Table :-D (I don't want making dict extra checking in
    # f_operators)
    m: type[Table | DeclarativeBase]
    stmt: Select
    wheres: list["SQLWhereType"] = dc_field(default_factory=list)
