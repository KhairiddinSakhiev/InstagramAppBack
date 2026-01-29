from pydantic import BaseModel
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime,Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint, CheckConstraint
from datetime import datetime
from typing import Optional
from sqlalchemy.sql import func
# from accounts.models import User


class Follow(BaseModel):

    follower_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    following_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id"),
        CheckConstraint("follower_id != following_id"),
    )

class Comment(BaseModel):

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"),nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"),nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)



class PostLike(BaseModel):

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"),nullable=False)


    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_post_likes"),
    )


class CommentLike(BaseModel):

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"),nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "comment_id", name="uq_comment_likes"),
    )


