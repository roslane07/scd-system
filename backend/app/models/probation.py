"""
PROBATION — 7-day restriction lock after zone upgrade.

When a conscrit climbs UP in zone (e.g. Orange → Jaune via TIG),
they remain subject to the restrictions of the LOWER zone for 7 days.

Rules:
  - A DIRECT malus during probation resets the 7-day counter to 0.
  - If the conscrit drops DOWN in zone, probation is closed immediately.
  - After 7 clean days, probation ends and normal zone restrictions apply.
"""
from datetime import datetime

from peewee import (
    AutoField,
    CharField,
    ForeignKeyField,
    DateTimeField,
    BooleanField,
)

from app.database import BaseModel
from app.models.personne import Personne


class ProbationLog(BaseModel):
    id = AutoField()

    # ── Who ───────────────────────────────────────────────
    conscrit = ForeignKeyField(
        Personne, backref="probations", on_delete="CASCADE"
    )

    # ── Lock details ──────────────────────────────────────
    # The zone whose restrictions remain active during probation
    zone_verrouillee = CharField(max_length=20)

    # ── Duration ──────────────────────────────────────────
    date_debut = DateTimeField(default=datetime.now)
    date_fin = DateTimeField()  # date_debut + 7 days

    # ── Status ────────────────────────────────────────────
    active = BooleanField(default=True)

    # ── Timestamp ─────────────────────────────────────────
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "probation"

    def __repr__(self):
        return (
            f"<ProbationLog id={self.id} conscrit={self.conscrit_id} "
            f"zone_lock={self.zone_verrouillee} active={self.active}>"
        )
