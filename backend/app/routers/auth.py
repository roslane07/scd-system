"""
Auth Router — Login, token refresh, password management, and onboarding.

Endpoints:
  POST /auth/login       — Login by email or nom
  POST /auth/refresh     — Refresh JWT token
  PATCH /auth/password   — Change own password
  POST /auth/forgot      — Request password reset email
  POST /auth/reset       — Reset password with token
  POST /auth/setup       — First-login onboarding (change pwd + fill profile)
"""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
import os
import httpx
from pydantic import BaseModel, Field
from typing import Optional

from app.models.personne import Personne
from app.utils.auth import (
    verify_password,
    hash_password,
    create_access_token,
    decode_access_token,
)
from app.utils.deps import get_current_user
from app.utils.constants import ROLE_CONSCRIT, ROLE_ANCIEN, ROLE_P3

router = APIRouter(prefix="/auth", tags=["Authentification"])


# ══════════════════════════════════════════════════════════════
#  SCHEMAS
# ══════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    nom: Optional[str] = None
    email: Optional[str] = None
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: int
    role: str
    nom: str
    prenom: str
    buque: Optional[str] = None
    first_login: bool


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class SetupRequest(BaseModel):
    new_password: str = Field(..., min_length=8)
    email: str = Field(..., min_length=5)
    buque: Optional[str] = None
    numero_fams: Optional[str] = None
    parent_id: Optional[int] = None
    pa2_numero_fams: Optional[str] = None
    p3_numero_fams: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    email: Optional[str] = None
    buque: Optional[str] = None
    numero_fams: Optional[str] = None


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    """
    Authenticate by email or nom (case-insensitive).
    Returns JWT token and first_login flag.
    """
    user = None

    if body.email:
        try:
            user = Personne.get(Personne.email ** body.email)
        except Personne.DoesNotExist:
            pass

    if not user and body.nom:
        try:
            user = Personne.get(Personne.nom ** body.nom)
        except Personne.DoesNotExist:
            pass

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/nom ou mot de passe incorrect",
        )

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/nom ou mot de passe incorrect",
        )

    token = create_access_token(user.id, user.role)

    return LoginResponse(
        access_token=token,
        id=user.id,
        role=user.role,
        nom=user.nom,
        prenom=user.prenom,
        buque=user.buque,
        first_login=user.first_login,
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(user: Personne = Depends(get_current_user)):
    """Refresh the JWT token."""
    token = create_access_token(user.id, user.role)
    return TokenRefreshResponse(access_token=token)


@router.patch("/password")
def change_password(body: PasswordChangeRequest, user: Personne = Depends(get_current_user)):
    """
    Change own password. Requires old password verification.
    """
    if not verify_password(body.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")

    user.password_hash = hash_password(body.new_password)
    user.save()
    return {"status": "ok", "message": "Mot de passe modifié"}


@router.patch("/profile")
def update_profile(body: ProfileUpdateRequest, user: Personne = Depends(get_current_user)):
    """
    Update own profile (email, buque, numero_fams).
    Cannot change nom/prenom.
    """
    updated = []

    if body.email is not None:
        # Check uniqueness
        existing = (
            Personne.select()
            .where(Personne.email == body.email, Personne.id != user.id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Email '{body.email}' déjà utilisé",
            )
        user.email = body.email
        updated.append("email")

    if body.buque is not None:
        # Check uniqueness if not empty
        if body.buque.strip():
            existing = (
                Personne.select()
                .where(Personne.buque == body.buque, Personne.id != user.id)
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail=f"Buque '{body.buque}' déjà utilisée",
                )
        user.buque = body.buque if body.buque.strip() else None
        updated.append("buque")

    if body.numero_fams is not None:
        user.numero_fams = body.numero_fams if body.numero_fams.strip() else None
        updated.append("numero_fams")

    user.save()

    return {
        "status": "ok",
        "message": "Profil mis à jour",
        "updated_fields": updated,
        "email": user.email,
        "buque": user.buque,
        "numero_fams": user.numero_fams,
    }


# async email sending task
async def send_reset_email(email_to: str, token: str):
    resend_api_key = os.environ.get("RESEND_API_KEY")
    if not resend_api_key:
        print("Warning: RESEND_API_KEY is not set.")
        return

    frontend_url = os.environ.get("FRONTEND_URL", "https://scd-system.vercel.app")
    reset_link = f"{frontend_url}/reset?token={token}"
    sender_email = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")

    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Réinitialisation de ton mot d'axe (SCD)</h2>
        <p>Salut,</p>
        <p>Tu as demandé à réinitialiser ton mot d'axe sur le SCD Tabagn's. Clique sur le bouton ci-dessous pour le changer :</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #7c3aed; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">Changer mon mot d'axe</a>
        </div>
        <p style="color: #666; font-size: 0.9em;">Si tu n'as pas fait cette demande, ignore simplement cet e-mail.</p>
    </div>
    """

    async with httpx.AsyncClient() as client:
        payload = {
            "from": f"SCD Tabagn's <{sender_email}>",
            "to": [email_to],
            "subject": "🔑 SCD - Réinitialisation de ton mot d'axe",
            "html": html_content
        }
        headers = {
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json"
        }
        try:
            resp = await client.post("https://api.resend.com/emails", json=payload, headers=headers)
            print(f"Resend email status: {resp.status_code}")
        except Exception as e:
            print(f"Error sending email: {e}")

@router.post("/forgot")
def forgot_password(body: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """
    Request a password reset. Generates a reset token and sends an email via Resend if configured.
    """
    try:
        user = Personne.get(Personne.email == body.email)
    except Personne.DoesNotExist:
        # Don't reveal whether the email exists
        return {"status": "ok", "message": "Si cette babill's existe, un lien de réinitialisation a été F.C."}

    # Create a short-lived reset token (15 minutes)
    reset_token = create_access_token(
        user.id, "RESET",
        expires_delta=timedelta(minutes=15)
    )

    background_tasks.add_task(send_reset_email, user.email, reset_token)

    return {
        "status": "ok",
        "message": "Si cette babill's existe, un lien de réinitialisation a été F.C.",
        "dev_reset_token": reset_token,  # Kept for trailing backward compatibility if needed locally
    }


@router.post("/reset")
def reset_password(body: ResetPasswordRequest):
    """
    Reset password using a reset token from /auth/forgot.
    """
    payload = decode_access_token(body.token)
    if not payload or payload.get("role") != "RESET":
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")

    personne_id = int(payload["sub"])
    try:
        user = Personne.get_by_id(personne_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=400, detail="Utilisateur introuvable")

    user.password_hash = hash_password(body.new_password)
    user.save()

    return {"status": "ok", "message": "Mot de passe réinitialisé avec succès"}


@router.post("/setup")
def onboarding_setup(body: SetupRequest, user: Personne = Depends(get_current_user)):
    """
    First-login onboarding: change password + fill profile.

    This endpoint can only be called when first_login is True.
    After completion, first_login is set to False.
    """
    if not user.first_login:
        raise HTTPException(
            status_code=400,
            detail="Setup déjà effectué. Utilisez PATCH /auth/password pour changer le mot de passe.",
        )

    # Update password
    user.password_hash = hash_password(body.new_password)

    # Update email (check uniqueness)
    existing = (
        Personne.select()
        .where(Personne.email == body.email, Personne.id != user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Email '{body.email}' déjà utilisé",
        )
    user.email = body.email

    # Update buque (check uniqueness if provided)
    if body.buque:
        existing = (
            Personne.select()
            .where(Personne.buque == body.buque, Personne.id != user.id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Buque '{body.buque}' déjà utilisée",
            )
        user.buque = body.buque

    # Update numero_fams
    if body.numero_fams:
        user.numero_fams = body.numero_fams

    # Update parent_id (pa²) - obligatoire
    if body.parent_id:
        try:
            parent = Personne.get_by_id(body.parent_id)
            if parent.role == ROLE_CONSCRIT:
                raise HTTPException(
                    status_code=400,
                    detail="Le pa² doit être un Ancien ou P3",
                )
            user.parent_id = body.parent_id

            # Update pa²'s numero_fams if provided and not already set
            if body.pa2_numero_fams and not parent.numero_fams:
                parent.numero_fams = body.pa2_numero_fams
                parent.save()

            # Update P3's numero_fams if provided and not already set
            if body.p3_numero_fams and parent.parent_id:
                try:
                    p3 = Personne.get_by_id(parent.parent_id)
                    if not p3.numero_fams:
                        p3.numero_fams = body.p3_numero_fams
                        p3.save()
                except Personne.DoesNotExist:
                    pass

        except Personne.DoesNotExist:
            raise HTTPException(status_code=404, detail="Pa² introuvable")

    # Mark onboarding complete
    user.first_login = False
    user.save()

    return {
        "status": "ok",
        "message": "Profil configuré avec succès ! Bienvenue dans le SCD.",
        "id": user.id,
        "email": user.email,
        "buque": user.buque,
        "numero_fams": user.numero_fams,
        "parent_id": user.parent_id,
    }


@router.get("/anciens-list")
def list_anciens_for_setup():
    """
    Public endpoint: list Anciens and P3 for the pa² dropdown during onboarding.
    Returns only id, nom, prenom, buque, numero_fams.
    """
    anciens = (
        Personne.select()
        .where(Personne.role.in_([ROLE_ANCIEN, ROLE_P3]))
        .order_by(Personne.nom)
    )
    return [
        {
            "id": a.id,
            "nom": a.nom,
            "prenom": a.prenom,
            "buque": a.buque,
            "numero_fams": a.numero_fams,
            "role": a.role,
        }
        for a in anciens
    ]


class AdminUpdateNumeroFamsRequest(BaseModel):
    user_id: int
    numero_fams: str = Field(..., min_length=1, max_length=50)


@router.patch("/admin/numero-fams")
def admin_update_numero_fams(
    body: AdminUpdateNumeroFamsRequest,
    user: Personne = Depends(get_current_user),
):
    """
    Admin endpoint (P3 only): update numero_fams for any user.
    This is for setting the real family numbers (e.g., "36-154", "49-13").
    """
    # Only P3 can use this endpoint
    if user.role != ROLE_P3:
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux P3 (administrateurs)",
        )
    
    try:
        target_user = Personne.get_by_id(body.user_id)
    except Personne.DoesNotExist:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    old_numero = target_user.numero_fams
    target_user.numero_fams = body.numero_fams.strip()
    target_user.save()
    
    return {
        "status": "ok",
        "message": f"Numéro de Fam's mis à jour pour {target_user.prenom} {target_user.nom}",
        "user_id": target_user.id,
        "old_numero_fams": old_numero,
        "new_numero_fams": target_user.numero_fams,
    }
