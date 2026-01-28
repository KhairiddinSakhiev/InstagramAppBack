from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from datetime import datetime
from database import BaseModel


class FeedItem(BaseModel):
    __tablename__ = "feed_items"
    
    user_id: Mapped[int] = mapped_column(Integer)


class Reels(BaseModel):
    __tablename__ = "reels"
    author_id: Mapped[int] = mapped_column(Integer)
    video_url: Mapped[str] = mapped_column(String)
    caption: Mapped[str] = mapped_column(String)
    # max_size_video: Mapped[int] = mapped_column(Integer,default=59)