"""
Cancel Service — Kill Switch (P3 only).

Reverses a log's point impact, marks it as annulé, and creates
a SYS-CANCEL counter-log. Does NOT undo collective malus that
were triggered by the original log.
"""
from datetime import datetime

from app.models.personne import Personne
from app.models.log import Log
from app.models.notification import Notification
from app.services.zone_service import calculer_zone
from app.config import settings
from app.utils.constants import SOURCE_CANCEL, ACTION_ANNULATION, NOTIFICATION_MESSAGES


def annuler_log(log_id: int, p3_id: int, justification: str) -> dict:
    """
    Cancel a log entry (Kill Switch).

    Reverses the point impact on the conscrit, marks the original
    log as annulé, and creates a new SYS-CANCEL log entry.

    Args:
        log_id: ID of the log to cancel
        p3_id: ID of the P3 executing the cancellation
        justification: Mandatory reason (min 10 chars)

    Returns:
        dict with corrected points and zone

    Raises:
        ValueError: If log doesn't exist, is already cancelled,
                     or justification is too short
    """
    # ── Validate ──────────────────────────────────────────
    if not justification or len(justification.strip()) < 10:
        raise ValueError("Justification obligatoire — minimum 10 caractères")

    try:
        log_original = Log.get_by_id(log_id)
    except Log.DoesNotExist:
        raise ValueError(f"Log #{log_id} introuvable")

    if log_original.annule:
        raise ValueError(f"Log #{log_id} est déjà annulé")

    # ── Reverse points ────────────────────────────────────
    conscrit = Personne.get_by_id(log_original.conscrit_id)
    points_avant = conscrit.points_actuels

    # Subtract the original points (reverse the effect)
    points_corriges = conscrit.points_actuels - log_original.points
    points_corriges = max(-9999, min(points_corriges, settings.PLAFOND_POINTS))

    zone_apres = calculer_zone(points_corriges)

    conscrit.points_actuels = points_corriges
    conscrit.zone = zone_apres
    conscrit.save()

    # ── Create cancellation log ───────────────────────────
    Log.create(
        conscrit=conscrit,
        ancien_id=p3_id,
        code_infraction="SYS-CANCEL",
        points=-log_original.points,  # Inverse of original
        source_type=SOURCE_CANCEL,
        type_action=ACTION_ANNULATION,
        points_avant=points_avant,
        points_apres=points_corriges,
        zone_avant=conscrit.zone,
        zone_apres=zone_apres,
        commentaire=f"Annulation log #{log_id} par P3 — {justification}",
        ref_log_annule=log_original,
        timestamp=datetime.now(),
    )

    # ── Mark original as cancelled ────────────────────────
    log_original.annule = True
    log_original.save()

    # ── Notify conscrit ───────────────────────────────────
    msg = NOTIFICATION_MESSAGES.get("CANCEL", {})
    Notification.create(
        destinataire=conscrit,
        type="CANCEL",
        titre=msg.get("titre", "↩️ Log annulé"),
        message=msg.get("body", "").format(
            log_id=log_id,
            date=log_original.timestamp.strftime("%d/%m/%Y"),
        ),
    )

    return {
        "status": "ok",
        "log_id_annule": log_id,
        "points_avant": points_avant,
        "points_corriges": points_corriges,
        "zone": zone_apres,
    }
