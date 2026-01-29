from fastapi import APIRouter
from datetime import datetime, timedelta
from feeds.models import FeedItem
from feeds.schemas import FeedItemResponseSchema,ReelsSchema
from feeds.services import FeedService
from fastapi import UploadFile
from database import AsyncSession
from feeds.helpers import save_uploaded_video, get_video_duration
from feeds.models import Reel
from feeds.schemas import ReelResponseSchema

feed_router = APIRouter(prefix="/feed", tags=["feed"])


mock_feed_items = [
    FeedItem(id=1, user_id=101, created_at=datetime.now() - timedelta(hours=1)),
    FeedItem(id=2, user_id=102, created_at=datetime.now() - timedelta(hours=2)),
    FeedItem(id=3, user_id=101, created_at=datetime.now() - timedelta(hours=3)),
    FeedItem(id=4, user_id=103, created_at=datetime.now() - timedelta(hours=4)),
    FeedItem(id=5, user_id=102, created_at=datetime.now() - timedelta(hours=5)),
    FeedItem(id=6, user_id=104, created_at=datetime.now() - timedelta(hours=6)),
]

mock_subscriptions = {101, 102}


@feed_router.get("/home", response_model=list[FeedItemResponseSchema])
def get_home_feed():

    feed_items = FeedService.get_home_feed(
        items=mock_feed_items,
        subscriptions=mock_subscriptions,
        limit=10
    )
    return feed_items


@feed_router.post(
    "/reels/create",
    response_model=ReelResponseSchema
)
async def create_reel(
    author_id: int,
    file: UploadFile,
    db: AsyncSession,
):
    video_path = await save_uploaded_video(file)
    duration = get_video_duration(video_path)

    reel = Reel(
        author_id=author_id,
        video_path=video_path,
        duration=duration,
    )

    db.add(reel)
    await db.commit()
    await db.refresh(reel)

    return reel
