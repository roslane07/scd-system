"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ══════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════
class LoginRequest(BaseModel):
    nom: str = Field(..., min_length=1, description="Nom de famille")
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: int
    role: str
    nom: str
    prenom: str
    buque: Optional[str] = None


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ══════════════════════════════════════════════════════════════
#  PERSONNE
# ══════════════════════════════════════════════════════════════
class PersonneOut(BaseModel):
    id: int
    nom: str
    prenom: str
    buque: Optional[str] = None
    numero_fams: Optional[str] = None
    role: str
    parent_id: Optional[int] = None
    points_actuels: Optional[int] = None
    zone: Optional[str] = None

    class Config:
        from_attributes = True


class PersonneDetail(PersonneOut):
    """Extended view with pa² info and timestamps."""
    pa2_id: Optional[int] = None
    pa2_nom: Optional[str] = None
    pa2_buque: Optional[str] = None
    p3_id: Optional[int] = None
    p3_nom: Optional[str] = None
    p3_buque: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BuqueUpdate(BaseModel):
    buque: str = Field(..., min_length=1, max_length=100)


class Pa2Update(BaseModel):
    parent_id: int


class NumeroFamsUpdate(BaseModel):
    numero_fams: str = Field(..., min_length=1, max_length=50)


# ══════════════════════════════════════════════════════════════
#  INFRACTIONS
# ══════════════════════════════════════════════════════════════
class InfractionApplyRequest(BaseModel):
    conscrit_id: int
    code: str = Field(..., description="Infraction code, e.g. ZAG-001, TIG-001")
    commentaire: Optional[str] = None
    duree_heures: Optional[float] = Field(
        None, description="Duration in hours (for TIG-001)"
    )


class InfractionApplyResponse(BaseModel):
    log_id: int
    code_applique: str
    nom_infraction: str
    points_appliques: int
    points_avant: int
    points_apres: int
    zone_avant: str
    zone_apres: str
    zone_changed: bool


class CancelRequest(BaseModel):
    justification: str = Field(..., min_length=10)


class CancelResponse(BaseModel):
    status: str
    log_id_annule: int
    points_avant: int
    points_corriges: int
    zone: str


class InfractionTypeOut(BaseModel):
    code: str
    nom: str
    points: int
    categorie: str
    description: str


# ══════════════════════════════════════════════════════════════
#  LOG
# ══════════════════════════════════════════════════════════════
class LogOut(BaseModel):
    id: int
    conscrit_id: int
    ancien_id: Optional[int] = None
    code_infraction: str
    points: int
    source_type: str
    type_action: str
    points_avant: int
    points_apres: int
    zone_avant: str
    zone_apres: str
    commentaire: Optional[str] = None
    annule: bool
    timestamp: datetime


# ══════════════════════════════════════════════════════════════
#  CLASSEMENT
# ══════════════════════════════════════════════════════════════
class ClassementIndividuelItem(BaseModel):
    rang: int
    id: int
    nom: str
    prenom: str
    buque: Optional[str] = None
    numero_fams: Optional[str] = None
    points_actuels: int
    zone: str
    couleur: str


class ClassementFamsItem(BaseModel):
    rang: int
    pa2: str
    numero_fams: str
    score_total: int
    nb_membres: int
    score_moyen: float


class StatsGlobales(BaseModel):
    total_conscrits: int
    moyenne_points: float
    par_zone: dict
    danger: list


# ══════════════════════════════════════════════════════════════
#  NOTIFICATIONS
# ══════════════════════════════════════════════════════════════
class NotificationOut(BaseModel):
    id: int
    type: str
    titre: str
    message: str
    lu: bool
    created_at: datetime


# ══════════════════════════════════════════════════════════════
#  RESTRICTIONS
# ══════════════════════════════════════════════════════════════
class RestrictionsOut(BaseModel):
    conscrit_id: int
    zone: str
    en_probation: bool
    restrictions: list[str]
