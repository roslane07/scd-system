"""
SCD Models — Package init.

Imports all models and exposes them + a helper to create all tables.
"""
from app.models.personne import Personne
from app.models.log import Log
from app.models.notification import Notification
from app.models.probation import ProbationLog
from app.database import db

ALL_MODELS = [Personne, Log, Notification, ProbationLog]


def create_tables():
    """Create all tables if they don't exist."""
    with db:
        db.create_tables(ALL_MODELS)


def drop_tables():
    """Drop all tables (for testing)."""
    with db:
        db.drop_tables(ALL_MODELS)
