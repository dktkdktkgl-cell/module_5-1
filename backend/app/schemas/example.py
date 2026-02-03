from datetime import datetime
from pydantic import BaseModel


class ExampleCreate(BaseModel):
    name: str
    description: str | None = None


class ExampleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
