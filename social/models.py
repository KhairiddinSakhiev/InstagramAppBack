from database import BaseModel
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UniqueConstraint, CheckConstraint
from typing import Optional


class Follow(BaseModel):
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("userauths.id", ondelete="CASCADE"),
        nullable=False
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey("userauths.id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow"),
        CheckConstraint("follower_id != following_id", name="ck_not_self_follow"),
    )


class Comment(BaseModel):
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("userauths.id", ondelete="CASCADE"),
        nullable=False
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)


class PostLike(BaseModel):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("userauths.id", ondelete="CASCADE"),
        nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_post_likes"),
    )


class CommentLike(BaseModel):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("userauths.id", ondelete="CASCADE"),
        nullable=False
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "comment_id", name="uq_comment_likes"),
    )


class SavedPost(BaseModel):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("userauths.id", ondelete="CASCADE"),
        nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_saved_posts"),
    )
