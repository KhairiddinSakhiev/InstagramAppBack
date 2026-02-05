from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from accounts.dependencies import get_current_user
from accounts.models import UserAuth

from .models import (
    Follow, Comment, PostLike, CommentLike, SavedPost
)
from .schemas import *

app = FastAPI()


@app.post("/follow/", response_model=FollowResponse, status_code=201)
def follow_user(
    data: FollowCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    if data.following_id == current_user.id:
        raise HTTPException(400, "Нельзя подписаться на себя")

    exists = db.query(Follow).filter_by(
        follower_id=current_user.id,
        following_id=data.following_id
    ).first()

    if exists:
        raise HTTPException(400, "Вы уже подписаны")

    follow = Follow(
        follower_id=current_user.id,
        following_id=data.following_id
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow


@app.delete("/follow/{user_id}", status_code=204)
def unfollow(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    follow = db.query(Follow).filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if not follow:
        raise HTTPException(404, "Подписка не найдена")

    db.delete(follow)
    db.commit()


@app.get("/users/{user_id}/stats", response_model=UserStatsResponse)
def user_stats(user_id: int, db: Session = Depends(get_db)):
    followers = db.query(Follow).filter(
        Follow.following_id == user_id
    ).count()

    following = db.query(Follow).filter(
        Follow.follower_id == user_id
    ).count()

    return {
        "followers": followers,
        "following": following,
    }


@app.post("/comments/", response_model=CommentResponse, status_code=201)
def create_comment(
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    if data.parent_id:
        parent = db.query(Comment).filter_by(id=data.parent_id).first()
        if not parent:
            raise HTTPException(404, "Комментарий не найден")
        if parent.post_id != data.post_id:
            raise HTTPException(400, "Неверный post_id")

    comment = Comment(
        post_id=data.post_id,
        user_id=current_user.id,
        parent_id=data.parent_id,
        text=data.text
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    comment.likes_count = 0
    return comment


@app.get("/comments/{post_id}", response_model=List[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    def build_tree(comment):
        replies = db.query(Comment).filter(
            Comment.parent_id == comment.id
        ).all()

        comment.replies = [build_tree(r) for r in replies]
        comment.likes_count = db.query(CommentLike).filter(
            CommentLike.comment_id == comment.id
        ).count()
        return comment

    roots = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.parent_id.is_(None)
    ).all()

    return [build_tree(c) for c in roots]


@app.post("/posts/{post_id}/like/", response_model=PostLikeResponse, status_code=201)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    exists = db.query(PostLike).filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if exists:
        raise HTTPException(400, "Пост уже лайкнут")

    like = PostLike(user_id=current_user.id, post_id=post_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


@app.delete("/posts/{post_id}/like/", status_code=204)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    like = db.query(PostLike).filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if not like:
        raise HTTPException(404, "Лайк не найден")

    db.delete(like)
    db.commit()


@app.post("/posts/{post_id}/save/", response_model=SavedPostResponse, status_code=201)
def save_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    exists = db.query(SavedPost).filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if exists:
        raise HTTPException(400, "Пост уже сохранён")

    saved = SavedPost(
        user_id=current_user.id,
        post_id=post_id
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@app.get("/posts/saved/", response_model=List[SavedPostResponse])
def get_saved_posts(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    return db.query(SavedPost).filter(
        SavedPost.user_id == current_user.id
    ).all()


@app.delete("/posts/{post_id}/save/", status_code=204)
def unsave_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user),
):
    saved = db.query(SavedPost).filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if not saved:
        raise HTTPException(404, "Сохранение не найдено")

    db.delete(saved)
    db.commit()
