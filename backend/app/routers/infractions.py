"""
Infractions Router — Apply infractions/bonuses and Kill Switch.

Endpoints are async to flush WebSocket notification queue after
the sync service call completes.
"""
from fastapi import APIRouter, HTTPException, Depends

from app.models.personne import Personne
from app.services.points_service import appliquer_infraction
from app.services.cancel_service import annuler_log
from app.services.notification_push import flush_notifications
from app.utils.deps import require_ancien, require_p3
from app.utils.constants import INFRACTIONS
from app.schemas.schemas import (
    InfractionApplyRequest,
    InfractionApplyResponse,
    CancelRequest,
    CancelResponse,
    InfractionTypeOut,
)

router = APIRouter(prefix="/infractions", tags=["Infractions"])


@router.post("/apply", response_model=InfractionApplyResponse)
async def apply_infraction(
    body: InfractionApplyRequest,
    user: Personne = Depends(require_ancien),
):
    """
    Apply an infraction or bonus to a conscrit.

    For COM-003, the backend auto-detects récidive and may upgrade to COM-004.
    For TIG codes, use this same endpoint (duree_heures is used for TIG-001).
    """
    try:
        result = appliquer_infraction(
            conscrit_id=body.conscrit_id,
            code_infraction=body.code,
            ancien_id=user.id,
            commentaire=body.commentaire or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Flush WebSocket notifications to connected clients
    await flush_notifications()

    return InfractionApplyResponse(**result)


@router.post("/cancel/{log_id}", response_model=CancelResponse)
async def cancel_log(
    log_id: int,
    body: CancelRequest,
    user: Personne = Depends(require_p3),
):
    """
    Kill Switch — Cancel a log entry (P3 only).

    Reverses the point impact and marks the log as annulé.
    Requires justification (min 10 characters).
    """
    try:
        result = annuler_log(
            log_id=log_id,
            p3_id=user.id,
            justification=body.justification,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Flush WebSocket notifications
    await flush_notifications()

    return CancelResponse(**result)


@router.get("/types", response_model=list[InfractionTypeOut])
def list_infraction_types():
    """
    List all available infraction and bonus codes.
    Public endpoint — used by frontend to populate pickers.
    """
    types = []
    for code, info in INFRACTIONS.items():
        # Skip system-generated codes
        if info["categorie"] == "SYS":
            continue
        types.append(
            InfractionTypeOut(
                code=code,
                nom=info["nom"],
                points=info["points"],
                categorie=info["categorie"],
                description=info.get("description", ""),
            )
        )
    return types
