from pydantic import BaseModel
from datetime import datetime


class FeedItemResponse(BaseModel):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True
