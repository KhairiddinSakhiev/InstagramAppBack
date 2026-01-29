from feeds.models import FeedItem
from feeds.models import Reel
from database import AsyncSession
from fastapi import UploadFile
from feeds.helpers import save_uploaded_video
from fastapi import HTTPException, status


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
    