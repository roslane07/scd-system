"""
Conscrits Router — CRUD, profile, history, restrictions, and post-usins patches.
"""
from fastapi import APIRouter, HTTPException, Depends, status

from app.models.personne import Personne
from app.models.log import Log
from app.models.notification import Notification
from app.models.probation import ProbationLog
from app.services.probation_service import verifier_restrictions_effectives
from app.utils.deps import get_current_user, require_ancien
from app.utils.constants import ROLE_CONSCRIT, ZONES
from app.schemas.schemas import (
    PersonneOut,
    PersonneDetail,
    BuqueUpdate,
    Pa2Update,
    NumeroFamsUpdate,
    LogOut,
    NotificationOut,
    RestrictionsOut,
)

router = APIRouter(prefix="/conscrits", tags=["Conscrits"])


@router.get("/", response_model=list[PersonneOut])
def list_conscrits(user: Personne = Depends(require_ancien)):
    """List all conscrits (Anciens/P3 only)."""
    conscrits = (
        Personne.select()
        .where(Personne.role == ROLE_CONSCRIT)
        .order_by(Personne.nom)
    )
    return [_personne_to_dict(c) for c in conscrits]


@router.get("/zone/{zone}", response_model=list[PersonneOut])
def list_by_zone(zone: str, user: Personne = Depends(require_ancien)):
    """Filter conscrits by zone."""
    if zone not in ZONES:
        raise HTTPException(status_code=400, detail=f"Zone inconnue : {zone}")

    conscrits = (
        Personne.select()
        .where(Personne.role == ROLE_CONSCRIT, Personne.zone == zone)
        .order_by(Personne.points_actuels.desc())
    )
    return [_personne_to_dict(c) for c in conscrits]


@router.get("/{conscrit_id}", response_model=PersonneDetail)
def get_conscrit(conscrit_id: int, user: Personne = Depends(get_current_user)):
    """
    Get full profile of a conscrit.
    Conscrits can only view their own profile. Anciens/P3 can view any.
    """
    try:
        conscrit = Personne.get_by_id(conscrit_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=404, detail="Conscrit introuvable")

    # Access control: conscrits can only see their own profile
    if user.role == ROLE_CONSCRIT and user.id != conscrit_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    data = _personne_to_dict(conscrit)

    # Add pa² info
    if conscrit.parent_id:
        try:
            pa2 = Personne.get_by_id(conscrit.parent_id)
            data["pa2_nom"] = f"{pa2.prenom} {pa2.nom}"
            data["pa2_buque"] = pa2.buque
        except Personne.DoesNotExist:
            data["pa2_nom"] = None
            data["pa2_buque"] = None
    else:
        data["pa2_nom"] = None
        data["pa2_buque"] = None

    data["created_at"] = conscrit.created_at
    data["updated_at"] = conscrit.updated_at

    return data


@router.get("/{conscrit_id}/historique", response_model=list[LogOut])
def get_historique(conscrit_id: int, user: Personne = Depends(get_current_user)):
    """Get full log history for a conscrit."""
    # Access control
    if user.role == ROLE_CONSCRIT and user.id != conscrit_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    logs = (
        Log.select()
        .where(Log.conscrit == conscrit_id)
        .order_by(Log.timestamp.desc())
    )
    return [_log_to_dict(log) for log in logs]


@router.get("/{conscrit_id}/restrictions", response_model=RestrictionsOut)
def get_restrictions(conscrit_id: int, user: Personne = Depends(get_current_user)):
    """
    Get effective restrictions for a conscrit, accounting for probation.
    """
    try:
        conscrit = Personne.get_by_id(conscrit_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=404, detail="Conscrit introuvable")

    restrictions = verifier_restrictions_effectives(conscrit_id)

    # Check if there's an active probation
    en_probation = (
        ProbationLog.select()
        .where(
            ProbationLog.conscrit == conscrit_id,
            ProbationLog.active == True,
        )
        .exists()
    )

    return RestrictionsOut(
        conscrit_id=conscrit_id,
        zone=conscrit.zone,
        en_probation=en_probation,
        restrictions=restrictions,
    )


@router.get("/{conscrit_id}/fam", response_model=list[PersonneOut])
def get_fam(conscrit_id: int, user: Personne = Depends(get_current_user)):
    """Get Fam's siblings (same parent_id, role=CONSCRIT)."""
    try:
        conscrit = Personne.get_by_id(conscrit_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=404, detail="Conscrit introuvable")

    if not conscrit.parent_id:
        return []  # No pa² yet (usins)

    siblings = (
        Personne.select()
        .where(
            Personne.parent_id == conscrit.parent_id,
            Personne.role == ROLE_CONSCRIT,
        )
        .order_by(Personne.nom)
    )
    return [_personne_to_dict(s) for s in siblings]


@router.get("/{conscrit_id}/notifications", response_model=list[NotificationOut])
def get_notifications(conscrit_id: int, user: Personne = Depends(get_current_user)):
    """Get notifications for a conscrit."""
    if user.role == ROLE_CONSCRIT and user.id != conscrit_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    notifs = (
        Notification.select()
        .where(Notification.destinataire == conscrit_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    return [
        {
            "id": n.id,
            "type": n.type,
            "titre": n.titre,
            "message": n.message,
            "lu": n.lu,
            "created_at": n.created_at,
        }
        for n in notifs
    ]


@router.post("/{notif_id}/notification/lu")
def mark_notification_read(notif_id: int, user: Personne = Depends(get_current_user)):
    """Mark a notification as read."""
    try:
        notif = Notification.get_by_id(notif_id)
    except Notification.DoesNotExist:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    if user.role == ROLE_CONSCRIT and notif.destinataire_id != user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    notif.lu = True
    notif.save()
    return {"status": "ok"}


# ── Post-usins patches ───────────────────────────────────

@router.patch("/{conscrit_id}/buque")
def set_buque(
    conscrit_id: int,
    body: BuqueUpdate,
    user: Personne = Depends(require_ancien),
):
    """Assign or update a conscrit's buque (post-usins)."""
    try:
        conscrit = Personne.get_by_id(conscrit_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=404, detail="Conscrit introuvable")

    # Check uniqueness
    existing = (
        Personne.select()
        .where(Personne.buque == body.buque, Personne.id != conscrit_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Buque '{body.buque}' déjà utilisée par {existing.prenom} {existing.nom}",
        )

    conscrit.buque = body.buque
    conscrit.save()
    return {"status": "ok", "buque": conscrit.buque}


@router.patch("/{conscrit_id}/pa2")
def set_pa2(
    conscrit_id: int,
    body: Pa2Update,
    user: Personne = Depends(require_ancien),
):
    """Assign the pa² (parent_id) for a conscrit (post-usins)."""
    try:
        conscrit = Personne.get_by_id(conscrit_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=404, detail="Conscrit introuvable")

    # Verify parent exists and is ANCIEN or P3
    try:
        parent = Personne.get_by_id(body.parent_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=404, detail="Pa² introuvable")

    if parent.role == ROLE_CONSCRIT:
        raise HTTPException(
            status_code=400,
            detail="Le pa² doit être un Ancien ou P3, pas un Conscrit",
        )

    conscrit.parent_id = body.parent_id
    conscrit.save()
    return {
        "status": "ok",
        "parent_id": conscrit.parent_id,
        "pa2_nom": f"{parent.prenom} {parent.nom}",
    }


@router.patch("/{conscrit_id}/numero_fams")
def set_numero_fams(
    conscrit_id: int,
    body: NumeroFamsUpdate,
    user: Personne = Depends(require_ancien),
):
    """Assign the numéro de Fam's for a conscrit (post-usins)."""
    try:
        conscrit = Personne.get_by_id(conscrit_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=404, detail="Conscrit introuvable")

    conscrit.numero_fams = body.numero_fams
    conscrit.save()
    return {"status": "ok", "numero_fams": conscrit.numero_fams}


# ── Helpers ───────────────────────────────────────────────

def _personne_to_dict(p: Personne) -> dict:
    return {
        "id": p.id,
        "nom": p.nom,
        "prenom": p.prenom,
        "buque": p.buque,
        "numero_fams": p.numero_fams,
        "role": p.role,
        "parent_id": p.parent_id,
        "points_actuels": p.points_actuels,
        "zone": p.zone,
    }


def _log_to_dict(log: Log) -> dict:
    return {
        "id": log.id,
        "conscrit_id": log.conscrit_id,
        "ancien_id": log.ancien_id,
        "code_infraction": log.code_infraction,
        "points": log.points,
        "source_type": log.source_type,
        "type_action": log.type_action,
        "points_avant": log.points_avant,
        "points_apres": log.points_apres,
        "zone_avant": log.zone_avant,
        "zone_apres": log.zone_apres,
        "commentaire": log.commentaire,
        "annule": log.annule,
        "timestamp": log.timestamp,
    }
