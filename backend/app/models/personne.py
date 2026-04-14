"""
PERSONNE — Unified table for Conscrit, Ancien, and P3.

This is the single most important table in the SCD system.
The `role` field determines what applies to each person:
  - CONSCRIT: has points_actuels, zone, subject to infractions
  - ANCIEN:   can log infractions, validate TIG, assign buque/pa2
  - P3:       all Ancien powers + Kill Switch + stats access
"""
from datetime import datetime

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    IntegerField,
    ForeignKeyField,
    DateTimeField,
    TextField,
)

from app.database import BaseModel


class Personne(BaseModel):
    id = AutoField()

    # ── Identity ──────────────────────────────────────────
    nom = CharField(max_length=100)
    prenom = CharField(max_length=100)

    # ── Gadzarts identity (nullable during usins) ─────────
    # buque: surnom gadzarique, unique, null before usins end
    buque = CharField(max_length=100, unique=True, null=True, default=None)
    # numero_fams: free text, e.g. "15" or "36-154", set manually
    numero_fams = CharField(max_length=50, null=True, default=None)

    # ── Role ──────────────────────────────────────────────
    # CONSCRIT / ANCIEN / P3
    role = CharField(max_length=20)

    # ── Family tree (pa²) ─────────────────────────────────
    # parent_id: FK to self — the Ancien who is this conscrit's pa²
    # null during usins (no pa² assigned yet)
    # An Ancien can have multiple fillots (1:N)
    parent_id = ForeignKeyField(
        "self", backref="fillots", null=True, default=None,
        on_delete="SET NULL",
    )

    # ── Points & Zone (conscrits only) ────────────────────
    # null for non-conscrits (Anciens/P3 don't have points)
    points_actuels = IntegerField(null=True, default=None)
    zone = CharField(max_length=20, null=True, default=None)

    # ── Auth ──────────────────────────────────────────────
    email = CharField(max_length=200, unique=True, null=True, default=None)
    password_hash = TextField()
    first_login = BooleanField(default=True)

    # ── Timestamps ────────────────────────────────────────
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "personne"

    def save(self, *args, **kwargs):
        """Auto-update `updated_at` on every save."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Returns buque if set, otherwise prenom."""
        return self.buque if self.buque else self.prenom

    def __repr__(self):
        return (
            f"<Personne id={self.id} nom='{self.nom}' prenom='{self.prenom}' "
            f"role={self.role} buque={self.buque} pts={self.points_actuels} "
            f"zone={self.zone}>"
        )
