"""
Zone Service — Pure functions for zone calculation and hierarchy checks.

No side effects, no database access. Used by every other service.
"""
from app.utils.constants import ZONES, HIERARCHIE


def calculer_zone(points: int) -> str:
    """
    Determine the zone code based on current points.

    Args:
        points: Current PC value (can be negative)

    Returns:
        Zone code string, e.g. "ZONE_VERTE"
    """
    for zone_code, bounds in ZONES.items():
        if bounds["min"] <= points <= bounds["max"]:
            return zone_code
    return "ZONE_NOIRE"


def est_remontee(zone_avant: str, zone_apres: str) -> bool:
    """
    Check if the zone change is an improvement (climbing up).

    Args:
        zone_avant: Previous zone code
        zone_apres: New zone code

    Returns:
        True if the conscrit moved UP in the hierarchy
    """
    return HIERARCHIE.index(zone_apres) > HIERARCHIE.index(zone_avant)


def est_descente(zone_avant: str, zone_apres: str) -> bool:
    """
    Check if the zone change is a degradation (falling down).
    """
    return HIERARCHIE.index(zone_apres) < HIERARCHIE.index(zone_avant)


def get_restrictions(zone: str) -> list:
    """
    Get the list of active restrictions for a given zone.
    """
    return ZONES.get(zone, {}).get("restrictions", [])


def get_zone_info(zone: str) -> dict:
    """
    Get full zone metadata (nom, couleur, restrictions, privileges).
    """
    return ZONES.get(zone, {})


def get_malus_collectif(zone: str) -> dict | None:
    """
    Get the collective malus config for a zone, if any.

    Returns:
        {"type": "FAM"|"PROMO", "points": int} or None
    """
    return ZONES.get(zone, {}).get("malus_collectif")
