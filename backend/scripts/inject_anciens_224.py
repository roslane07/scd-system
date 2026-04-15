#!/usr/bin/env python3
"""Script d'injection des nouveaux Anciens 224."""
import sys
sys.path.insert(0, '/app')

from app.database import db
from app.models.personne import Personne
from app.utils.auth import hash_password
from app.utils.constants import ROLE_ANCIEN

NOUVEAUX_ANCIENS = [
    {"nom": "eljamiai",  "prenom": "Yasser",        "display_nom": "EL JAMIAI"},
    {"nom": "gainou",    "prenom": "Maroua",         "display_nom": "GAINOU"},
    {"nom": "elfilali",  "prenom": "Yassine",        "display_nom": "EL FILALI"},
    {"nom": "elhicho",   "prenom": "Ahmed",          "display_nom": "EL HICHO"},
    {"nom": "korchi",    "prenom": "Rana",           "display_nom": "KORCHI"},
    {"nom": "targui",    "prenom": "Marouane",       "display_nom": "TARGUI"},
    {"nom": "assmina",   "prenom": "Mohamed Amine",  "display_nom": "ASSMINA"},
    {"nom": "elabibi",   "prenom": "Saffa",          "display_nom": "ELABIBI"},
]

added = 0
skipped = 0

for a in NOUVEAUX_ANCIENS:
    mdp = f"{a['nom']}224"
    try:
        existing = Personne.get(Personne.nom == a["nom"])
        print(f"  SKIP (déjà présent): {a['display_nom']} {a['prenom']}")
        skipped += 1
    except Personne.DoesNotExist:
        Personne.create(
            nom=a["nom"],
            prenom=a["prenom"],
            role=ROLE_ANCIEN,
            password_hash=hash_password(mdp),
            points_actuels=100,
            zone="ZONE_VERTE",
            first_login=True,
        )
        print(f"  OK: {a['display_nom']} {a['prenom']} | mdp: {mdp}")
        added += 1

print(f"\nTerminé — {added} ajouté(s), {skipped} ignoré(s).")
