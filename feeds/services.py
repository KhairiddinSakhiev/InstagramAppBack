from feeds.models import FeedItem
from feeds.models import Reel
from feeds.models import ReelLike
from database import AsyncSession
from fastapi import UploadFile
from feeds.helpers import save_uploaded_video
from fastapi import HTTPException, status
from sqlalchemy import select

class FeedService:  
    @staticmethod
    def get_home_feed(items: list[FeedItem], subscriptions: set[int], limit: int) -> list[FeedItem]:
        filtered_items = [
            item for item in items
            if item.user_id in subscriptions
        ]
        
        sorted_items = sorted(
            filtered_items,
            key=lambda x: x.created_at,
            reverse=True
        )
        
        return sorted_items[:limit]


async def create_reel(
    db: AsyncSession,
    author_id: int,
    file: UploadFile,
) -> Reel:
    """
    Create a reel from uploaded video.
    Calls save_uploaded_video ONCE (which validates and returns duration).
    Returns ORM Reel object.
    """
    video_path, duration = await save_uploaded_video(file)

    reel = Reel(
        author_id=author_id,
        video_path=video_path,
        duration=duration,
    )

    db.add(reel)
    await db.commit()
    await db.refresh(reel)

    return reel

async def get_reel(db: AsyncSession, reel_id: int) -> Reel:
    reel = await db.get(Reel, reel_id)
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found"
        )
    return reel

async def delete_reel(db: AsyncSession, reel_id: int) -> None:
    reel = await db.get(Reel, reel_id)
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found"
        )
    await db.delete(reel)
    await db.commit()

async def reel_like_toggle(db: AsyncSession, reel_id: int, user_id: int) -> ReelLike:
    result = await db.execute(
        select(ReelLike).where(
            ReelLike.reel_id == reel_id,
            ReelLike.user_id == user_id
        )
    )
    reel_like = result.scalar_one_or_none()
    if not reel_like:
        reel_like = ReelLike(reel_id=reel_id, user_id=user_id)
        db.add(reel_like)
        await db.commit()
        await db.refresh(reel_like)
    else:
        like_data = {
            'id': reel_like.id,
            'reel_id': reel_like.reel_id,
            'user_id': reel_like.user_id,
            'created_at': reel_like.created_at,
            'updated_at': reel_like.updated_at
        }
        await db.delete(reel_like)
        await db.commit()
        reel_like = ReelLike(**like_data)
    return reel_like