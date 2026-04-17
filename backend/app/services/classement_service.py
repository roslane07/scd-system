"""
Classement Service — Individual and Fam's rankings.

Individual: All conscrits ranked by points DESC.
Fam's: Grouped by parent_id (pa²), sum of PC, ranked DESC.
  - Conscrits with parent_id=null (usins) grouped as "Sans Fam's".
"""
from peewee import fn

from app.models.personne import Personne
from app.utils.constants import ROLE_CONSCRIT, ZONES


def classement_individuel() -> list[dict]:
    """
    Get individual ranking of all conscrits, sorted by points DESC.

    Returns:
        List of dicts with rang, id, nom, prenom, buque, points, zone, couleur
    """
    conscrits = (
        Personne.select()
        .where(Personne.role == ROLE_CONSCRIT)
        .order_by(Personne.points_actuels.desc())
    )

    classement = []
    for rang, c in enumerate(conscrits, 1):
        zone_info = ZONES.get(c.zone, {})
        classement.append({
            "rang": rang,
            "id": c.id,
            "nom": c.nom,
            "prenom": c.prenom,
            "buque": c.buque,
            "numero_fams": c.numero_fams,
            "points_actuels": c.points_actuels,
            "zone": c.zone,
            "couleur": zone_info.get("couleur", "#888888"),
        })

    return classement


def classement_fams() -> list[dict]:
    """
    Get Fam's ranking, grouped by parent_id.

    Each Fam's score = sum of PC of all its conscrits.
    Conscrits with parent_id=null are grouped as "Sans Fam's".
    Sorted by numero_fams (family number) ascending.

    Returns:
        List of dicts with rang, pa2 info, score_total, nb_membres, score_moyen
    """
    # Query: group conscrits by parent_id, sum points, count members
    resultats = (
        Personne.select(
            Personne.parent_id,
            fn.SUM(Personne.points_actuels).alias("score_fam"),
            fn.COUNT(Personne.id).alias("nb_membres"),
        )
        .where(Personne.role == ROLE_CONSCRIT)
        .group_by(Personne.parent_id)
    )

    # Collect data first, then sort by numero_fams
    raw_data = []
    for row in resultats:
        if row.parent_id:
            try:
                pa2 = Personne.get_by_id(row.parent_id)
                label = pa2.buque or f"{pa2.prenom} {pa2.nom}"
                numero = pa2.numero_fams or "—"
            except Personne.DoesNotExist:
                label = "Pa² inconnu"
                numero = "—"
        else:
            label = "Sans Fam's (usins en cours)"
            numero = "—"

        nb = row.nb_membres
        score = row.score_fam or 0
        raw_data.append({
            "pa2": label,
            "numero_fams": numero,
            "score_total": score,
            "nb_membres": nb,
            "score_moyen": round(score / nb, 1) if nb > 0 else 0,
        })

    # Sort by numero_fams (put "—" at the end)
    def sort_key(item):
        num = item["numero_fams"]
        if num == "—" or num is None:
            return (1, "")  # Sans Fam's at the end
        return (0, num)  # Sort by numero_fams ascending

    raw_data.sort(key=sort_key)

    # Assign rang after sorting
    classement = []
    for rang, item in enumerate(raw_data, 1):
        item["rang"] = rang
        classement.append(item)

    return classement


def stats_globales() -> dict:
    """
    Get promo-wide statistics (P3 only).

    Returns:
        dict with count per zone, average points, danger list, total conscrits
    """
    conscrits = (
        Personne.select()
        .where(Personne.role == ROLE_CONSCRIT)
    )

    total = 0
    somme_points = 0
    par_zone = {}
    danger = []  # conscrits in Orange, Rouge, or Noire

    for c in conscrits:
        total += 1
        somme_points += c.points_actuels or 0
        zone = c.zone or "UNKNOWN"

        par_zone[zone] = par_zone.get(zone, 0) + 1

        if zone in ("ZONE_ORANGE", "ZONE_ROUGE", "ZONE_NOIRE"):
            danger.append({
                "id": c.id,
                "nom": c.nom,
                "prenom": c.prenom,
                "buque": c.buque,
                "points": c.points_actuels,
                "zone": c.zone,
            })

    return {
        "total_conscrits": total,
        "moyenne_points": round(somme_points / total, 1) if total > 0 else 0,
        "par_zone": par_zone,
        "danger": sorted(danger, key=lambda x: x["points"]),
    }
