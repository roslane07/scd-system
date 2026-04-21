"""
Collectif Service — Collective malus for Fam's and Promo.

When a conscrit drops to Zone Orange → Fam's siblings lose 5 PC each.
When a conscrit drops to Zone Rouge → entire promo loses 10 PC each.

CRITICAL RULES:
  1. Collective logs use source_type="COLLECTIF" → NEVER cascade
  2. If parent_id is null (usins), Fam's malus is SKIPPED
  3. If RODAGE_ACTIF is True, ALL collective malus are SKIPPED
  4. Zone/points of affected members are updated but do NOT trigger
     further _handle_zone_change calls
"""
from datetime import datetime

from app.models.personne import Personne
from app.models.log import Log
from app.services.zone_service import calculer_zone
from app.config import settings
from app.utils.constants import (
    ROLE_CONSCRIT,
    ROLE_COMITE,
    SOURCE_COLLECTIF,
    ACTION_MALUS_COLLECTIF,
)


def appliquer_malus_famille(conscrit_responsable: Personne, points: int):
    """
    Apply collective malus to Fam's siblings.

    Siblings = conscrits with same parent_id as the offender.
    Only applies to role=CONSCRIT, excludes the offender.

    Args:
        conscrit_responsable: The conscrit who triggered the malus
        points: Negative points to apply (e.g. -5)
    """
    # Guard: usins — no pa² means no siblings identifiable
    if not conscrit_responsable.parent_id:
        return

    # Guard: rodage mode
    if settings.RODAGE_ACTIF:
        return

    # Find siblings: same pa², role=CONSCRIT or COMITE, exclude self
    freres_soeurs = (
        Personne.select()
        .where(
            Personne.parent_id == conscrit_responsable.parent_id,
            Personne.role.in_([ROLE_CONSCRIT, ROLE_COMITE]),
            Personne.id != conscrit_responsable.id,
        )
    )

    nom_responsable = conscrit_responsable.display_name

    for membre in freres_soeurs:
        points_avant = membre.points_actuels
        zone_avant = membre.zone

        # Apply malus (floor at -9999, no cap needed for negative)
        nouveaux_points = max(-9999, membre.points_actuels + points)
        nouvelle_zone = calculer_zone(nouveaux_points)

        membre.points_actuels = nouveaux_points
        membre.zone = nouvelle_zone
        membre.save()

        # Create COLLECTIF log — will NEVER cascade
        Log.create(
            conscrit=membre,
            ancien=None,  # System auto-generated
            code_infraction="SYS-MALUS-FAM",
            points=points,
            source_type=SOURCE_COLLECTIF,
            type_action=ACTION_MALUS_COLLECTIF,
            points_avant=points_avant,
            points_apres=nouveaux_points,
            zone_avant=zone_avant,
            zone_apres=nouvelle_zone,
            commentaire=f"Solidarité Fam's — {nom_responsable} en Zone Orange",
            timestamp=datetime.now(),
        )


def appliquer_malus_promotion(conscrit_responsable: Personne, points: int):
    """
    Apply collective malus to the entire promo.

    Affects ALL conscrits except the offender.

    Args:
        conscrit_responsable: The conscrit who triggered the malus
        points: Negative points to apply (e.g. -10)
    """
    # Guard: rodage mode
    if settings.RODAGE_ACTIF:
        return

    tous_conscrits = (
        Personne.select()
        .where(
            Personne.role.in_([ROLE_CONSCRIT, ROLE_COMITE]),
            Personne.id != conscrit_responsable.id,
        )
    )

    nom_responsable = conscrit_responsable.display_name

    for conscrit in tous_conscrits:
        points_avant = conscrit.points_actuels
        zone_avant = conscrit.zone

        nouveaux_points = max(-9999, conscrit.points_actuels + points)
        nouvelle_zone = calculer_zone(nouveaux_points)

        conscrit.points_actuels = nouveaux_points
        conscrit.zone = nouvelle_zone
        conscrit.save()

        # Create COLLECTIF log — will NEVER cascade
        Log.create(
            conscrit=conscrit,
            ancien=None,
            code_infraction="SYS-MALUS-PROMO",
            points=points,
            source_type=SOURCE_COLLECTIF,
            type_action=ACTION_MALUS_COLLECTIF,
            points_avant=points_avant,
            points_apres=nouveaux_points,
            zone_avant=zone_avant,
            zone_apres=nouvelle_zone,
            commentaire=f"Solidarité Promo — {nom_responsable} en Zone Rouge",
            timestamp=datetime.now(),
        )
