from typing import Optional, List
from pydantic import BaseModel


class PostBase(BaseModel):
    image: Optional[str] = None
    content: str
    is_deleted: bool = False

class PostCreate(PostBase):
    author_id: int


class PostUpdate(BaseModel):
    image: Optional[str] = None
    content: Optional[str] = None
    is_deleted: Optional[bool] = None

class PostRead(PostBase):
    id: int
    author_id: int

    class Config:
        orm_mode = True
