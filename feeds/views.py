from fastapi import APIRouter, Depends, Form, UploadFile
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from feeds.models import FeedItem
from feeds.schemas import FeedItemResponseSchema, ReelResponseSchema
from feeds.services import FeedService, create_reel
from database import get_db

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
async def create_reel_endpoint(
    author_id: int = Form(...),
    file: UploadFile = ...,
    db: AsyncSession = Depends(get_db),
):
    reel = await create_reel(
        db=db,
        author_id=author_id,
        file=file,
    )
    return reel
