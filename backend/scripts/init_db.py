"""
Database initialisation & seed script.

Creates all tables, seeds 43 conscrits (all at 100 PC, ZONE_VERTE),
creates 3 test Anciens and 1 P3 for development.

Usage:
    cd scd-system/backend
    python -m scripts.init_db
"""
import sys
import os

# Add backend to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.models import create_tables, ALL_MODELS
from app.models.personne import Personne
from app.utils.auth import hash_password
from app.utils.constants import ROLE_CONSCRIT, ROLE_ANCIEN, ROLE_P3
from app.config import settings


# ══════════════════════════════════════════════════════════════
#  43 CONSCRITS — placeholder names (replace with real names)
# ══════════════════════════════════════════════════════════════
CONSCRITS_DATA = [
    ("Conscrit", f"{i+1}", ROLE_CONSCRIT)
    for i in range(settings.TOTAL_CONSCRITS)
]

# ══════════════════════════════════════════════════════════════
#  TEST ACCOUNTS — Anciens + P3
# ══════════════════════════════════════════════════════════════
STAFF_DATA = [
    # (nom, prenom, role, password)
    ("Ancien1", "Test", ROLE_ANCIEN, "ancien123"),
    ("Ancien2", "Test", ROLE_ANCIEN, "ancien123"),
    ("Ancien3", "Test", ROLE_ANCIEN, "ancien123"),
    ("P3-Admin", "Test", ROLE_P3, "p3admin123"),
]


def seed_database():
    """Create tables and seed initial data."""
    print("🗄️  Création des tables...")
    create_tables()
    print(f"   ✅ {len(ALL_MODELS)} tables créées")

    # Check if already seeded
    existing = Personne.select().count()
    if existing > 0:
        print(f"   ⚠️  Base déjà peuplée ({existing} personnes). Skipping seed.")
        return

    print(f"\n👥 Import de {settings.TOTAL_CONSCRITS} conscrits...")
    default_password = hash_password("conscrit123")

    with db.atomic():
        for nom, prenom, role in CONSCRITS_DATA:
            Personne.create(
                nom=nom,
                prenom=prenom,
                role=role,
                buque=None,           # null during usins
                numero_fams=None,     # null during usins
                parent_id=None,       # null during usins
                points_actuels=settings.POINTS_INITIAUX,
                zone="ZONE_VERTE",
                password_hash=default_password,
            )

    print(f"   ✅ {settings.TOTAL_CONSCRITS} conscrits créés (100 PC, ZONE_VERTE)")

    print(f"\n🔑 Création des comptes staff (Anciens + P3)...")
    with db.atomic():
        for nom, prenom, role, password in STAFF_DATA:
            Personne.create(
                nom=nom,
                prenom=prenom,
                role=role,
                buque=None,
                numero_fams=None,
                parent_id=None,
                points_actuels=None,  # Staff don't have points
                zone=None,           # Staff don't have zones
                password_hash=hash_password(password),
            )

    print(f"   ✅ {len(STAFF_DATA)} comptes staff créés")

    # Summary
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    print("=" * 50)
    total = Personne.select().count()
    conscrits = Personne.select().where(Personne.role == ROLE_CONSCRIT).count()
    anciens = Personne.select().where(Personne.role == ROLE_ANCIEN).count()
    p3s = Personne.select().where(Personne.role == ROLE_P3).count()
    print(f"   Total:     {total}")
    print(f"   Conscrits: {conscrits}")
    print(f"   Anciens:   {anciens}")
    print(f"   P3:        {p3s}")
    print(f"\n   🔐 Mot de passe conscrits: conscrit123")
    print(f"   🔐 Mot de passe anciens:   ancien123")
    print(f"   🔐 Mot de passe P3:        p3admin123")
    print(f"\n   📍 Base de données: {settings.DATABASE_PATH}")
    print(f"   🏁 Mode rodage: {'ACTIF ✅' if settings.RODAGE_ACTIF else 'INACTIF'}")


if __name__ == "__main__":
    seed_database()
