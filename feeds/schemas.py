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
    views_count: int
    likes_count: int
    comments_count: int

    class Config:
        from_attributes = True

class DeleteResponseSchema(BaseModel):
    message: str

class ReelLikeCreateSchema(BaseModel):
    reel_id: int
    user_id: int

class ReelCommentCreateSchema(BaseModel):
    reel_id: int
    user_id: int
    comment: str

class ReelCommentResponseSchema(BaseModel):
    id: int
    reel_id: int
    user_id: int
    comment: str

    class Config:
        from_attributes = True

class ReelLikeResponseSchema(BaseModel):
    id: int
    reel_id: int
    user_id: int

    class Config:
        from_attributes = True