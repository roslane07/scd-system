"""
Probation Service — 7-day restriction lock management.

When a conscrit remounts (climbs UP in zone), they remain subject to
the restrictions of the lower zone for 7 days. A new DIRECT malus
during probation resets the counter. A descente closes probation.
"""
from datetime import datetime, timedelta

from app.models.probation import ProbationLog
from app.models.log import Log
from app.config import settings
from app.utils.constants import SOURCE_DIRECT, ZONES


def declencher_probation(conscrit_id: int, zone_verrou: str):
    """
    Start a new probation period for a conscrit.

    Closes any existing active probation first, then creates a new one.

    Args:
        conscrit_id: ID of the conscrit
        zone_verrou: The lower zone whose restrictions remain active
    """
    # Close any existing active probation
    ProbationLog.update(active=False).where(
        ProbationLog.conscrit == conscrit_id,
        ProbationLog.active == True,
    ).execute()

    # Create new probation
    now = datetime.now()
    ProbationLog.create(
        conscrit_id=conscrit_id,
        zone_verrouillee=zone_verrou,
        date_debut=now,
        date_fin=now + timedelta(days=settings.PROBATION_JOURS),
        active=True,
    )


def clore_probation_active(conscrit_id: int):
    """
    Close all active probations for a conscrit.
    Called when the conscrit drops DOWN in zone (probation becomes irrelevant).
    """
    ProbationLog.update(active=False).where(
        ProbationLog.conscrit == conscrit_id,
        ProbationLog.active == True,
    ).execute()


def verifier_restrictions_effectives(conscrit_id: int) -> list:
    """
    Get the effective restrictions for a conscrit, accounting for probation.

    If probation is active:
      - Check for recent DIRECT malus → reset counter if found
      - If 7 days elapsed cleanly → close probation
      - Otherwise → return restrictions of the locked zone

    If no active probation → return restrictions of the conscrit's current zone.

    Args:
        conscrit_id: ID of the conscrit

    Returns:
        List of restriction strings
    """
    from app.models.personne import Personne

    conscrit = Personne.get_by_id(conscrit_id)
    probation = (
        ProbationLog.select()
        .where(
            ProbationLog.conscrit == conscrit_id,
            ProbationLog.active == True,
        )
        .order_by(ProbationLog.date_debut.desc())
        .first()
    )

    if probation:
        # Check for DIRECT malus received during probation
        infraction_recente = (
            Log.select()
            .where(
                Log.conscrit == conscrit_id,
                Log.source_type == SOURCE_DIRECT,
                Log.type_action == "Malus",
                Log.annule == False,
                Log.timestamp >= probation.date_debut,
            )
            .first()
        )

        if infraction_recente:
            # Reset the 7-day counter
            now = datetime.now()
            probation.date_debut = now
            probation.date_fin = now + timedelta(days=settings.PROBATION_JOURS)
            probation.save()

        # Check if 7 days have elapsed cleanly
        jours = (datetime.now() - probation.date_debut).days
        if jours >= settings.PROBATION_JOURS:
            probation.active = False
            probation.save()
        else:
            # Probation still active → return locked zone restrictions
            return ZONES.get(probation.zone_verrouillee, {}).get("restrictions", [])

    # No active probation → return current zone restrictions
    return ZONES.get(conscrit.zone, {}).get("restrictions", [])
