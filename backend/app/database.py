"""
SCD Database — Peewee ORM connection with SQLite WAL mode.
"""
from peewee import SqliteDatabase, Model
from app.config import settings

db = SqliteDatabase(settings.DATABASE_PATH, pragmas={
    "journal_mode": "wal",         # Better concurrent reads
    "cache_size": -1024 * 64,      # 64 MB cache
    "foreign_keys": 1,             # Enforce FK constraints
    "busy_timeout": 5000,          # Wait 5s on lock instead of failing
})


class BaseModel(Model):
    """Base model — all SCD models inherit from this."""
    class Meta:
        database = db
