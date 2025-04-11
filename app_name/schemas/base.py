import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def to_db(self, **kwargs):
        """Extra method for serialization data for the frontend"""
        return self.model_dump(exclude_unset=True, exclude_none=True)

    def to_front(self):
        """Extra method for serialization data for the frontend"""
        return self.model_dump(mode="json", by_alias=True)


class CreatedAtSchemaMixin(OrmModel):
    created_at: datetime.datetime


class LogTimeSchemaMixin(OrmModel):
    log_time: datetime.datetime


class IntIdSchemaMixin(OrmModel):
    id: int = Field(description="Primary Key")


class UuidIdSchemaMixin(OrmModel):
    id: UUID = Field(description="Primary Key")
