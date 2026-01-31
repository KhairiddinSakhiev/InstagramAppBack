from fastapi import APIRouter, Depends, Form, UploadFile
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from feeds.models import FeedItem
from feeds.schemas import FeedItemResponseSchema, ReelResponseSchema, DeleteResponseSchema, ReelLikeResponseSchema
from feeds.services import FeedService, create_reel, delete_reel, get_reel, reel_like_toggle
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


@feed_router.delete("/reels/{reel_id}", response_model=DeleteResponseSchema)
async def delete_reel_endpoint(
    reel_id: int,
    db: AsyncSession = Depends(get_db),
):
    await delete_reel(db=db, reel_id=reel_id)
    return DeleteResponseSchema(message="Reel deleted successfully")


@feed_router.get("/reels/{reel_id}", response_model=ReelResponseSchema)
async def get_reel_endpoint(
    reel_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_reel(db=db, reel_id=reel_id)

@feed_router.post("/reels/{reel_id}/like", response_model=ReelLikeResponseSchema)
async def reel_like_toggle_endpoint(
    reel_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await reel_like_toggle(db=db, reel_id=reel_id, user_id=user_id)