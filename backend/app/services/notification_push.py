"""
Notification Push Service — Bridges sync business logic to async WebSocket.

Since the services (points_service, collectif_service) are synchronous,
this module provides a queue-based approach: sync code enqueues notifications,
and the async router drains the queue after the endpoint returns.
"""
import asyncio
from collections import deque
from typing import Optional


class NotificationQueue:
    """
    Thread-safe queue for pending WebSocket notifications.
    Sync services push here, async routers drain to WebSocket.
    """

    def __init__(self):
        self._queue: deque[tuple[list[int], dict]] = deque()

    def push(self, personne_ids: list[int], data: dict):
        """
        Enqueue a notification for one or more users.
        Called from sync service code.
        """
        self._queue.append((personne_ids, data))

    def push_one(self, personne_id: int, data: dict):
        """Enqueue a notification for a single user."""
        self._queue.append(([personne_id], data))

    def drain(self) -> list[tuple[list[int], dict]]:
        """
        Drain all pending notifications and return them.
        Called from async router code after service call completes.
        """
        items = list(self._queue)
        self._queue.clear()
        return items


# Global singleton — services push here, routers drain from here
notification_queue = NotificationQueue()


async def flush_notifications():
    """
    Send all queued notifications via WebSocket.
    Call this in the router after the sync service returns.
    """
    from app.routers.websocket import manager

    pending = notification_queue.drain()
    for personne_ids, data in pending:
        await manager.broadcast_to_users(personne_ids, data)
