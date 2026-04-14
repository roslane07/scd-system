"""
WebSocket Router — Real-time notification push.

Clients connect with their JWT token as a query parameter:
    ws://localhost:8000/ws/notifications?token=eyJ...

The ConnectionManager maintains active connections keyed by personne_id.
When a zone change or collective malus occurs, notifications are pushed
instantly to connected clients without page reload.
"""
import json
import asyncio
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.utils.auth import decode_access_token
from app.models.personne import Personne

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """
    Manages active WebSocket connections.
    Maps personne_id → WebSocket for instant notification push.
    """

    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, personne_id: int, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[personne_id] = websocket

    def disconnect(self, personne_id: int):
        """Remove a disconnected client."""
        self.active_connections.pop(personne_id, None)

    async def send_to_user(self, personne_id: int, data: dict):
        """Send a JSON message to a specific connected user."""
        ws = self.active_connections.get(personne_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(personne_id)

    async def broadcast_to_users(self, personne_ids: list[int], data: dict):
        """Send a JSON message to multiple connected users."""
        for pid in personne_ids:
            await self.send_to_user(pid, data)

    async def broadcast_to_all(self, data: dict):
        """Send a JSON message to ALL connected users."""
        disconnected = []
        for pid, ws in self.active_connections.items():
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(pid)
        for pid in disconnected:
            self.disconnect(pid)

    @property
    def connected_count(self) -> int:
        return len(self.active_connections)


# Global singleton — imported by other modules to push notifications
manager = ConnectionManager()


@router.websocket("/ws/notifications")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time notifications.

    Connect with: ws://host:port/ws/notifications?token=<JWT>

    Server → Client messages:
        {"type": "zone_change", "titre": "...", "message": "..."}
        {"type": "malus_fam", "titre": "...", "message": "..."}
        {"type": "malus_promo", "titre": "...", "message": "..."}
        {"type": "new_notification", ...}
        {"type": "pong"}

    Client → Server messages:
        {"type": "ping"}
    """
    # ── Auth: verify JWT token ────────────────────────────
    if not token:
        await websocket.close(code=4001, reason="Token manquant")
        return

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Token invalide ou expiré")
        return

    personne_id = int(payload["sub"])

    try:
        Personne.get_by_id(personne_id)
    except Personne.DoesNotExist:
        await websocket.close(code=4001, reason="Utilisateur introuvable")
        return

    # ── Connect ───────────────────────────────────────────
    await manager.connect(personne_id, websocket)

    try:
        # Send a welcome message
        await websocket.send_json({
            "type": "connected",
            "message": f"Connecté au SCD. {manager.connected_count} utilisateur(s) en ligne.",
        })

        # ── Listen for client messages (keepalive ping) ───
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(personne_id)
