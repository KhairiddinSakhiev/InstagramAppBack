from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List



class FollowCreate(BaseModel):
    following_id: int


class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    post_id: int
    text: str
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    parent_id: Optional[int]
    text: str
    created_at: datetime

    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


class PostLikeCreate(BaseModel):
    post_id: int


class PostLikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentLikeCreate(BaseModel):
    comment_id: int


class CommentLikeResponse(BaseModel):
    id: int
    user_id: int
    comment_id: int
    created_at: datetime

    class Config:
        from_attributes = True



