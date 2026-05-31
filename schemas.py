from datetime import datetime, UTC

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class TodoBase(BaseModel):
    title: str  = Field(default = None, min_length=1, max_length=100)
    description: str = Field(default = None, min_length=1, max_length=100)
    urgency_level: Literal["low", "medium", "high"] = Field(default = None)

    

class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = Field(default = None, min_length=1, max_length=100)
    description: str | None = Field (default = None, min_length = 1)
    urgency_level: Literal["low", "medium", "high"] | None = Field(default= None)




class TodoResponse(TodoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date_created: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_completed: bool = False


