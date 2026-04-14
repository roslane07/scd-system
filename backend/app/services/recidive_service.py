"""
Récidive Service — Auto-detection of repeated infractions.

Currently handles COM-003 → COM-004 escalation:
If a conscrit already has a COM-003 or COM-004 (DIRECT, non-annulé)
in the last 30 days, any new "COM-003" is auto-upgraded to "COM-004".
"""
from datetime import datetime, timedelta

from app.models.log import Log
from app.config import settings
from app.utils.constants import SOURCE_DIRECT


def check_recidive_respect(conscrit_id: int) -> str:
    """
    Check if the conscrit has a recent respect violation.

    If there is a COM-003 or COM-004 (DIRECT, not cancelled) in the
    last 30 days, return "COM-004" (récidive). Otherwise "COM-003".

    Args:
        conscrit_id: ID of the conscrit

    Returns:
        "COM-003" or "COM-004"
    """
    window = datetime.now() - timedelta(days=settings.RECIDIVE_WINDOW_JOURS)

    count = (
        Log.select()
        .where(
            Log.conscrit == conscrit_id,
            Log.code_infraction.in_(["COM-003", "COM-004"]),
            Log.source_type == SOURCE_DIRECT,
            Log.annule == False,
            Log.timestamp >= window,
        )
        .count()
    )

    return "COM-004" if count >= 1 else "COM-003"
