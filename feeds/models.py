from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer
from datetime import datetime
from database import BaseModel


class FeedItem(BaseModel):
    __tablename__ = "feed_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class Reels(BaseModel):
    __tablename__ = "reels"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    video_url: Mapped[str] = mapped_column()
    caption: Mapped[str] = mapped_column()
    # max_size_video: Mapped[int] = mapped_column(Integer,default=59)