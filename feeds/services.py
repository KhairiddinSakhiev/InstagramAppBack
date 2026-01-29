from feeds.models import FeedItem
from feeds.schemas import ReelResponseSchema
from feeds.models import Reel
from database import AsyncSession
from fastapi import UploadFile
from feeds.helpers import save_uploaded_video, get_video_duration
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
    file: UploadFile,
) -> ReelResponseSchema:
    video_path = await save_uploaded_video(file)

    duration = get_video_duration(video_path)

    reel = Reel(
        video_path=video_path,
        duration=duration,
        author_id=1,
    )

    db.add(reel)
    await db.commit()
    await db.refresh(reel)

    return ReelResponseSchema(
        id=reel.id,
        author_id=reel.author_id,
        video_path=reel.video_path,
        duration=reel.duration,
        created_at=reel.created_at,
    )

async def get_reel(db: AsyncSession, reel_id: int) -> ReelResponseSchema:
    reel = await db.get(Reel, reel_id)
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found"
        )
    return ReelResponseSchema(
        id=reel.id,
        author_id=reel.author_id,
        video_path=reel.video_path,
        duration=reel.duration,
        created_at=reel.created_at,
    )
    