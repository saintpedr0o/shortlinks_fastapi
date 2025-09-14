from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime


class BaseLink(BaseModel):
    original_link: HttpUrl


class LinkCreate(BaseLink):
    pass


class LinkListOut(BaseLink):
    short_code: str
    short_url: str

    model_config = {"from_attributes": True}


class LinkOut(BaseLink):
    id: int
    created_at: datetime
    user_id: UUID
    short_code: str
    short_url: str

    model_config = {"from_attributes": True}
