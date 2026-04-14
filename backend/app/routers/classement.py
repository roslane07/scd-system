"""
Classement Router — Individual rankings, Fam's rankings, and global stats.
"""
from fastapi import APIRouter, Depends

from app.models.personne import Personne
from app.services.classement_service import (
    classement_individuel,
    classement_fams,
    stats_globales,
)
from app.utils.deps import get_current_user, require_p3
from app.schemas.schemas import (
    ClassementIndividuelItem,
    ClassementFamsItem,
    StatsGlobales,
)

router = APIRouter(prefix="/classement", tags=["Classement"])


@router.get("/individuel", response_model=list[ClassementIndividuelItem])
def get_classement_individuel(user: Personne = Depends(get_current_user)):
    """
    Individual ranking — all conscrits, sorted by points DESC.
    Accessible to everyone (Conscrits, Anciens, P3).
    """
    return classement_individuel()


@router.get("/fams", response_model=list[ClassementFamsItem])
def get_classement_fams(user: Personne = Depends(get_current_user)):
    """
    Fam's ranking — grouped by parent_id (pa²), sum of PC.
    Accessible to everyone.
    """
    return classement_fams()


@router.get("/stats", response_model=StatsGlobales)
def get_stats_globales(user: Personne = Depends(require_p3)):
    """
    Global promo statistics — P3 only.
    Shows count per zone, average points, and danger list.
    """
    return stats_globales()
