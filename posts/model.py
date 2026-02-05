from typing import List, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import BaseModel


class Post(BaseModel):
    
    author_id: Mapped[int] = mapped_column(ForeignKey("userauths.id"))
    image: Mapped[Optional[str]] = mapped_column(nullable=True)  
    content: Mapped[str] = mapped_column()
    is_deleted: Mapped[bool] = mapped_column(default=False)

