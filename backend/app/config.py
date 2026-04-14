"""
SCD Configuration — Settings loaded from environment or defaults.
"""
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────
    DATABASE_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scd.db"
    )

    # ── JWT Auth ──────────────────────────────────────────
    JWT_SECRET: str = "scd-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480  # 8 hours

    # ── SCD Rules ─────────────────────────────────────────
    POINTS_INITIAUX: int = 100
    PLAFOND_POINTS: int = 150
    TOTAL_CONSCRITS: int = 43
    PROBATION_JOURS: int = 7
    RECIDIVE_WINDOW_JOURS: int = 30

    # ── Rodage Mode ───────────────────────────────────────
    # When True, collective malus (Fam's + Promo) are suspended.
    # Infractions still apply individually.
    # Set to False after the 2-week learning period.
    RODAGE_ACTIF: bool = True

    class Config:
        env_prefix = "SCD_"


settings = Settings()
