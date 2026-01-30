from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float, DateTime
from datetime import datetime
from database import BaseModel


class FeedItem(BaseModel):    
    user_id: Mapped[int] = mapped_column(Integer)


class Reel(BaseModel):
    author_id: Mapped[int] = mapped_column(Integer)
    video_path: Mapped[str] = mapped_column(String)
    duration: Mapped[float] = mapped_column(Float)
    views_count:Mapped[int] = mapped_column(Integer,default=0)
    likes_count:Mapped[int] = mapped_column(Integer,default=0)
    comments_count:Mapped[int] = mapped_column(Integer,default=0)


class ReelLike(BaseModel):
    reel_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)

class ReelComment(BaseModel):
    reel_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(String)
