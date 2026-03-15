import redis.asyncio as aioredis

from app.models.circle import SavingsCircle


class EventPublisher:
    """
    Publishes domain events to Redis Streams (XADD).
    Consumers use XREADGROUP for at-least-once, acknowledged delivery.
    """

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def _publish(self, stream: str, payload: dict) -> None:
        await self.redis.xadd(stream, payload)

    async def circle_created(self, circle: SavingsCircle) -> None:
        await self._publish(
            "circle.created",
            {
                "circle_id": str(circle.id),
                "circle_name": circle.name,
                "creator_user_id": str(circle.creator_id),
                "topic": f"Save ₦{circle.amount} {circle.frequency}",
            },
        )

    async def member_joined(self, circle_id: str, user_id: str) -> None:
        await self._publish(
            "member.joined",
            {
                "circle_id": str(circle_id),
                "user_id": str(user_id),
            },
        )

    async def member_left(self, circle_id: str, user_id: str) -> None:
        await self._publish(
            "member.left",
            {
                "circle_id": str(circle_id),
                "user_id": str(user_id),
            },
        )

    async def circle_closed(self, circle_id: str) -> None:
        await self._publish(
            "circle.closed",
            {"circle_id": str(circle_id)},
        )
