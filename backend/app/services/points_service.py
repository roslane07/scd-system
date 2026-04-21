"""
Points Service — THE CORE of the SCD system.

Single entry point for ALL point mutations. Handles:
  - Atomic point update (prevents race conditions)
  - Zone recalculation
  - Zone change detection → triggers notifications, collective malus, probation
  - Récidive auto-detection (COM-003 → COM-004)

Every infraction/bonus flows through `appliquer_infraction()`.
"""
from datetime import datetime
from typing import Optional

from peewee import fn

from app.database import db
from app.models.personne import Personne
from app.models.log import Log
from app.models.notification import Notification
from app.config import settings
from app.services.zone_service import (
    calculer_zone,
    est_remontee,
    est_descente,
    get_malus_collectif,
)
from app.services.collectif_service import (
    appliquer_malus_famille,
    appliquer_malus_promotion,
)
from app.services.probation_service import (
    declencher_probation,
    clore_probation_active,
)
from app.services.recidive_service import check_recidive_respect
from app.services.notification_push import notification_queue
from app.utils.constants import (
    INFRACTIONS,
    SOURCE_DIRECT,
    ACTION_MALUS,
    ACTION_BONUS,
    NOTIFICATION_MESSAGES,
    ROLE_CONSCRIT,
    ROLE_COMITE,
)


def appliquer_infraction(
    conscrit_id: int,
    code_infraction: str,
    ancien_id: int,
    commentaire: str = "",
) -> dict:
    """
    Apply an infraction or bonus to a conscrit. This is the SINGLE ENTRY POINT
    for all point mutations in the SCD system.

    Flow:
      1. Validate inputs
      2. Auto-detect récidive (COM-003 → COM-004)
      3. Atomic SQL update (prevents race conditions)
      4. Create LOG with source_type=DIRECT
      5. Detect zone change → handle cascades

    Args:
        conscrit_id: Target conscrit ID
        code_infraction: Infraction code (e.g. "ZAG-001", "TIG-001")
        ancien_id: ID of the Ancien/P3 logging this
        commentaire: Optional comment

    Returns:
        dict with log details, zone change info, and applied code

    Raises:
        ValueError: If conscrit or infraction code is invalid
    """
    # ── 1. Validate ───────────────────────────────────────
    # Auto-detect récidive for COM-003
    if code_infraction == "COM-003":
        code_infraction = check_recidive_respect(conscrit_id)

    if code_infraction not in INFRACTIONS:
        raise ValueError(f"Code infraction inconnu : {code_infraction}")

    infraction = INFRACTIONS[code_infraction]

    try:
        conscrit = Personne.get_by_id(conscrit_id)
    except Personne.DoesNotExist:
        raise ValueError(f"Conscrit {conscrit_id} introuvable")

    if conscrit.role not in (ROLE_CONSCRIT, ROLE_COMITE):
        raise ValueError(f"Personne {conscrit_id} n'est pas un conscrit")

    if conscrit.points_actuels is None:
        raise ValueError(f"Conscrit {conscrit_id} n'a pas de points initialisés")

    # ── 2. Snapshot before ────────────────────────────────
    points_avant = conscrit.points_actuels
    zone_avant = conscrit.zone

    # ── 3. Atomic SQL update ──────────────────────────────
    # Use SQL-level MIN/MAX to prevent read-modify-write race condition
    # Two Anciens logging simultaneously won't corrupt points
    with db.atomic():
        Personne.update(
            points_actuels=fn.MIN(
                fn.MAX(Personne.points_actuels + infraction["points"], -9999),
                settings.PLAFOND_POINTS,
            )
        ).where(Personne.id == conscrit_id).execute()

        # Re-read after atomic update
        conscrit = Personne.get_by_id(conscrit_id)
        points_apres = conscrit.points_actuels

    # ── 4. Recalculate zone ───────────────────────────────
    zone_apres = calculer_zone(points_apres)
    conscrit.zone = zone_apres
    conscrit.save()

    # ── 5. Create LOG ─────────────────────────────────────
    type_action = ACTION_BONUS if infraction["points"] > 0 else ACTION_MALUS
    log = Log.create(
        conscrit=conscrit,
        ancien_id=ancien_id,
        code_infraction=code_infraction,
        points=infraction["points"],
        source_type=SOURCE_DIRECT,
        type_action=type_action,
        points_avant=points_avant,
        points_apres=points_apres,
        zone_avant=zone_avant,
        zone_apres=zone_apres,
        commentaire=commentaire,
        timestamp=datetime.now(),
    )

    # ── 6. Handle zone change ─────────────────────────────
    zone_changed = zone_avant != zone_apres
    if zone_changed:
        _handle_zone_change(conscrit, zone_avant, zone_apres, log)

    return {
        "log_id": log.id,
        "code_applique": code_infraction,
        "nom_infraction": infraction["nom"],
        "points_appliques": infraction["points"],
        "points_avant": points_avant,
        "points_apres": points_apres,
        "zone_avant": zone_avant,
        "zone_apres": zone_apres,
        "zone_changed": zone_changed,
    }


def _handle_zone_change(
    conscrit: Personne,
    zone_avant: str,
    zone_apres: str,
    log: Log,
):
    """
    Handle all side effects of a zone change:
      1. Create notifications
      2. Apply collective malus (if DIRECT and not rodage)
      3. Manage probation (remontée → start, descente → close)
    """
    nom = conscrit.display_name

    # ── 1. Notifications ──────────────────────────────────
    _create_zone_notification(conscrit, zone_apres, nom)

    # ── 2. Collective malus (only for DIRECT logs) ────────
    if log.source_type == SOURCE_DIRECT:
        malus_config = get_malus_collectif(zone_apres)
        if malus_config:
            if malus_config["type"] == "FAM":
                appliquer_malus_famille(conscrit, malus_config["points"])
                _create_malus_fam_notifications(conscrit, nom)
            elif malus_config["type"] == "PROMO":
                appliquer_malus_promotion(conscrit, malus_config["points"])
                _create_malus_promo_notifications(conscrit, nom)

    # ── 3. Probation management ───────────────────────────
    if est_remontee(zone_avant, zone_apres):
        declencher_probation(conscrit.id, zone_verrou=zone_avant)
        # Notification for remontée
        msg = NOTIFICATION_MESSAGES.get("REMONTEE", {})
        Notification.create(
            destinataire=conscrit,
            type="REMONTEE",
            titre=msg.get("titre", "").format(zone_nouvelle=zone_apres),
            message=msg.get("body", "").format(zone_nouvelle=zone_apres),
        )
    elif est_descente(zone_avant, zone_apres):
        clore_probation_active(conscrit.id)


def _create_zone_notification(conscrit: Personne, zone: str, nom: str):
    """Create a notification for the conscrit about their zone change."""
    msg = NOTIFICATION_MESSAGES.get(zone)
    if msg:
        titre = msg["titre"].format(nom=nom)
        message = msg["body"].format(nom=nom)
        Notification.create(
            destinataire=conscrit,
            type="ZONE_CHANGE",
            titre=titre,
            message=message,
        )
        # Push to WebSocket queue
        notification_queue.push_one(conscrit.id, {
            "type": "zone_change",
            "titre": titre,
            "message": message,
            "zone": zone,
        })


def _create_malus_fam_notifications(conscrit_responsable: Personne, nom: str):
    """Notify Fam's siblings about the collective malus."""
    if not conscrit_responsable.parent_id:
        return

    msg = NOTIFICATION_MESSAGES.get("MALUS_FAM", {})
    freres = (
        Personne.select()
        .where(
            Personne.parent_id == conscrit_responsable.parent_id,
            Personne.role == ROLE_CONSCRIT,
            Personne.id != conscrit_responsable.id,
        )
    )
    titre = msg.get("titre", "").format(nom=nom)
    message = msg.get("body", "").format(nom=nom)
    for frere in freres:
        Notification.create(
            destinataire=frere,
            type="MALUS_FAM",
            titre=titre,
            message=message,
        )
        # Push to WebSocket queue
        notification_queue.push_one(frere.id, {
            "type": "malus_fam",
            "titre": titre,
            "message": message,
        })


def _create_malus_promo_notifications(conscrit_responsable: Personne, nom: str):
    """Notify the entire promo about the collective malus."""
    msg = NOTIFICATION_MESSAGES.get("MALUS_PROMO", {})
    tous = (
        Personne.select()
        .where(
            Personne.role == ROLE_CONSCRIT,
            Personne.id != conscrit_responsable.id,
        )
    )
    titre = msg.get("titre", "").format(nom=nom)
    message = msg.get("body", "").format(nom=nom)
    for c in tous:
        Notification.create(
            destinataire=c,
            type="MALUS_PROMO",
            titre=titre,
            message=message,
        )
        # Push to WebSocket queue
        notification_queue.push_one(c.id, {
            "type": "malus_promo",
            "titre": titre,
            "message": message,
        })
