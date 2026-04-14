"""
NOTIFICATION — Message queue for conscrits and staff.

Notifications are created by the system when zone changes occur,
collective malus are applied, or logs are cancelled. They are
displayed in the frontend and marked as read by the user.
"""
from datetime import datetime

from peewee import (
    AutoField,
    CharField,
    ForeignKeyField,
    DateTimeField,
    TextField,
    BooleanField,
)

from app.database import BaseModel
from app.models.personne import Personne


class Notification(BaseModel):
    id = AutoField()

    # ── Recipient ─────────────────────────────────────────
    destinataire = ForeignKeyField(
        Personne, backref="notifications", on_delete="CASCADE"
    )

    # ── Content ───────────────────────────────────────────
    type = CharField(max_length=30)       # ZONE_CHANGE, MALUS_FAM, MALUS_PROMO, etc.
    titre = CharField(max_length=200)
    message = TextField()
    data = TextField(null=True, default=None)  # JSON string for extra payload

    # ── Status ────────────────────────────────────────────
    lu = BooleanField(default=False)

    # ── Timestamp ─────────────────────────────────────────
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "notification"

    def __repr__(self):
        return (
            f"<Notification id={self.id} dest={self.destinataire_id} "
            f"type={self.type} lu={self.lu}>"
        )
