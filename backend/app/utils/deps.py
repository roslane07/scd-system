"""
FastAPI Dependencies — get_current_user and role guards.

Usage in routers:
    @router.get("/protected")
    def protected(user: Personne = Depends(get_current_user)):
        ...

    @router.post("/ancien-only")
    def ancien_only(user: Personne = Depends(require_ancien)):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.personne import Personne
from app.utils.auth import decode_access_token
from app.utils.constants import ROLE_ANCIEN, ROLE_P3

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Personne:
    """Extract and validate the current user from the JWT token."""
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
        )

    personne_id = payload.get("sub")
    if personne_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide : identifiant manquant",
        )

    try:
        user = Personne.get_by_id(int(personne_id))
    except Personne.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
        )

    return user


def require_ancien(user: Personne = Depends(get_current_user)) -> Personne:
    """Require at least ANCIEN role (ANCIEN or P3)."""
    if user.role not in (ROLE_ANCIEN, ROLE_P3):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux Anciens et P3",
        )
    return user


def require_p3(user: Personne = Depends(get_current_user)) -> Personne:
    """Require P3 role specifically."""
    if user.role != ROLE_P3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux P3 uniquement",
        )
    return user
