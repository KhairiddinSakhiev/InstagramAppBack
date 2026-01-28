from fastapi import APIRouter
from datetime import datetime, timedelta
from feeds.models import FeedItem
from feeds.schemas import FeedItemResponse
from feeds.services import FeedService

router = APIRouter(prefix="/feed", tags=["feed"])


mock_feed_items = [
    FeedItem(id=1, author_id=101, created_at=datetime.now() - timedelta(hours=1)),
    FeedItem(id=2, author_id=102, created_at=datetime.now() - timedelta(hours=2)),
    FeedItem(id=3, author_id=101, created_at=datetime.now() - timedelta(hours=3)),
    FeedItem(id=4, author_id=103, created_at=datetime.now() - timedelta(hours=4)),
    FeedItem(id=5, author_id=102, created_at=datetime.now() - timedelta(hours=5)),
    FeedItem(id=6, author_id=104, created_at=datetime.now() - timedelta(hours=6)),
]

mock_subscriptions = {101, 102, 103}


@router.get("/home", response_model=list[FeedItemResponse])
def get_home_feed():

    feed_items = FeedService.get_home_feed(
        items=mock_feed_items,
        subscriptions=mock_subscriptions,
        limit=10
    )
    return feed_items
