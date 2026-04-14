"""
Migration: Add `email` and `first_login` columns to PERSONNE table.

Usage:
    cd scd-system/backend
    source venv/bin/activate
    python -m scripts.migrate_email
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from peewee import CharField, BooleanField
from playhouse.migrate import SqliteMigrator, migrate as run_migrate
from app.database import db

db.connect(reuse_if_open=True)
migrator = SqliteMigrator(db)

print("🔄 Migration: Adding email and first_login to personne...")

try:
    run_migrate(
        migrator.add_column("personne", "email",
            CharField(max_length=200, unique=True, null=True, default=None)),
    )
    print("  ✅ email column added")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("  ⚠️  email column already exists, skipping")
    else:
        print(f"  ❌ {e}")

try:
    run_migrate(
        migrator.add_column("personne", "first_login",
            BooleanField(default=True)),
    )
    print("  ✅ first_login column added")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("  ⚠️  first_login column already exists, skipping")
    else:
        print(f"  ❌ {e}")

# Set first_login=False for existing Anciens and P3 (they don't need onboarding)
from app.models.personne import Personne
count = (
    Personne.update(first_login=False)
    .where(Personne.role.in_(["ANCIEN", "P3"]))
    .execute()
)
print(f"  ✅ Set first_login=False for {count} Anciens/P3")

print("\n✅ Migration complete")
db.close()
