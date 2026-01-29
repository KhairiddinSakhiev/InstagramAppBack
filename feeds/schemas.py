from pydantic import BaseModel
from datetime import datetime


class FeedItemResponseSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReelCreateSchema(BaseModel):
    author_id: int

class ReelResponseSchema(BaseModel):
    id: int
    author_id: int
    video_path: str
    duration: float
    created_at: datetime

    class Config:
        from_attributes = True