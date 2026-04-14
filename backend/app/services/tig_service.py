"""
TIG Service — Bonus validation for Travaux d'Intérêt Gadzarts.

All TIG require a validateur (Ancien or P3). TIG-004 is calculated
automatically (nightly cron, not in Phase 1 scope — but the logic
is here). TIG-005 requires a P3 validateur.
"""
from datetime import datetime, timedelta

from app.models.log import Log
from app.config import settings
from app.utils.constants import INFRACTIONS, SOURCE_DIRECT


def valider_tig(
    conscrit_id: int,
    code_tig: str,
    duree_heures: float = None,
    validateur_id: int = None,
) -> int:
    """
    Validate a TIG and calculate points to award.

    Args:
        conscrit_id: Target conscrit
        code_tig: TIG code (TIG-001 to TIG-005)
        duree_heures: Duration in hours (required for TIG-001)
        validateur_id: ID of the Ancien/P3 validating

    Returns:
        Number of points to award

    Raises:
        ValueError: If validation requirements are not met
    """
    if not validateur_id:
        raise ValueError("Tout TIG requiert un validateur (Ancien ou P3)")

    if code_tig not in INFRACTIONS:
        raise ValueError(f"Code TIG inconnu : {code_tig}")

    if not code_tig.startswith("TIG-"):
        raise ValueError(f"{code_tig} n'est pas un code TIG")

    if code_tig == "TIG-001":
        if not duree_heures or duree_heures <= 0:
            raise ValueError("TIG-001 requiert une durée en heures > 0")
        points = int(5 * duree_heures)

    elif code_tig == "TIG-002":
        points = 10

    elif code_tig == "TIG-003":
        points = 20

    elif code_tig == "TIG-004":
        # Semaine Exemplaire — check 0 DIRECT malus in last 7 days
        logs_7j = (
            Log.select()
            .where(
                Log.conscrit == conscrit_id,
                Log.source_type == SOURCE_DIRECT,
                Log.type_action == "Malus",
                Log.annule == False,
                Log.timestamp >= datetime.now() - timedelta(days=7),
            )
            .count()
        )
        if logs_7j > 0:
            raise ValueError(
                "Semaine non exemplaire — logs malus DIRECT présents "
                f"dans les 7 derniers jours ({logs_7j} trouvés)"
            )
        points = 5

    elif code_tig == "TIG-005":
        points = 8

    else:
        points = INFRACTIONS[code_tig]["points"]

    return points
