from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from datetime import datetime
from database import BaseModel


class FeedItem(BaseModel):    
    user_id: Mapped[int] = mapped_column(Integer)


class Reel(BaseModel):

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer)
    video_path: Mapped[str] = mapped_column(String)
    duration: Mapped[float] = mapped_column(Float)
