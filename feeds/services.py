from feeds.models import FeedItem


class FeedService:
    @staticmethod
    def get_home_feed(items: list[FeedItem], subscriptions: set[int], limit: int) -> list[FeedItem]:

        filtered_items = [
            item for item in items
            if item.author_id in subscriptions
        ]
        
        sorted_items = sorted(
            filtered_items,
            key=lambda x: x.created_at,
            reverse=True
        )
        
        return sorted_items[:limit]
