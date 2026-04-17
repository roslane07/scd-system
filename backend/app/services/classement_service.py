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
    Get Fam's ranking, grouped by P3's numero_fams (Fam's racine).

    Each Fam's score = sum of PC of all its conscrits under the same P3 root.
    Conscrits without a P3 chain are grouped as "Sans Fam's".
    Sorted by P3's numero_fams ascending.

    Returns:
        List of dicts with rang, p3_name, numero_fams, score_total, nb_membres, score_moyen
    """
    # Get all conscrits
    conscrits = Personne.select().where(Personne.role == ROLE_CONSCRIT)

    # Group by P3's numero_fams
    fams_data = {}
    for c in conscrits:
        # Find P3 (root) - climb the parent chain
        p3 = None
        current = c
        visited = set()
        
        while current.parent_id and current.id not in visited:
            visited.add(current.id)
            try:
                parent = Personne.get_by_id(current.parent_id)
                # Check if this parent is a P3 (no parent or role=P3)
                if parent.role == 'P3' or not parent.parent_id:
                    p3 = parent
                    break
                current = parent
            except Personne.DoesNotExist:
                break
        
        # Determine family key and name
        if p3:
            fam_key = p3.numero_fams or f"p3_{p3.id}"
            fam_name = p3.buque or f"{p3.prenom} {p3.nom}"
            fam_numero = p3.numero_fams or "—"
        else:
            fam_key = "sans_fams"
            fam_name = "Sans Fam's (usins en cours)"
            fam_numero = "—"
        
        # Aggregate data
        if fam_key not in fams_data:
            fams_data[fam_key] = {
                "pa2": fam_name,
                "numero_fams": fam_numero,
                "score_total": 0,
                "nb_membres": 0,
            }
        
        fams_data[fam_key]["score_total"] += c.points_actuels or 0
        fams_data[fam_key]["nb_membres"] += 1
    
    # Calculate averages and prepare for sorting
    raw_data = []
    for fam in fams_data.values():
        nb = fam["nb_membres"]
        score = fam["score_total"]
        fam["score_moyen"] = round(score / nb, 1) if nb > 0 else 0
        raw_data.append(fam)

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
