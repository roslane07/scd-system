"""
SCD Constants — The brain of the system.

All zone definitions, infraction codes, hierarchy, and notification
message templates live here. This is the single source of truth for
all business rules that don't require database queries.
"""

# ══════════════════════════════════════════════════════════════
#  ZONE HIERARCHY (lowest → highest)
# ══════════════════════════════════════════════════════════════
HIERARCHIE = [
    "ZONE_NOIRE",
    "ZONE_ROUGE",
    "ZONE_ORANGE",
    "ZONE_JAUNE",
    "ZONE_VERTE",
]

# ══════════════════════════════════════════════════════════════
#  ZONE DEFINITIONS
# ══════════════════════════════════════════════════════════════
ZONES = {
    "ZONE_VERTE": {
        "min": 85,
        "max": 150,
        "nom": "Citoyen",
        "couleur": "#228B22",
        "restrictions": [],
        "privileges": ["DROIT_PAROLE", "ELIGIBLE_RESPONSABILITE"],
    },
    "ZONE_JAUNE": {
        "min": 50,
        "max": 84,
        "nom": "Sous Surveillance",
        "couleur": "#FFBF00",
        "restrictions": ["FAC_MANUSCRITE"],
        "privileges": [],
    },
    "ZONE_ORANGE": {
        "min": 20,
        "max": 49,
        "nom": "Probation",
        "couleur": "#FF4500",
        "restrictions": [
            "ACCOMPAGNEMENT",
            "ZAGRISE_P3_BOUTONNEE",
            "TIG_OBLIGATOIRE",
        ],
        "privileges": [],
        "malus_collectif": {"type": "FAM", "points": -5},
    },
    "ZONE_ROUGE": {
        "min": 0,
        "max": 19,
        "nom": "Mise à Pied",
        "couleur": "#8B0000",
        "restrictions": [
            "GHOSTING",
            "NAMING_PUBLIC",
            "EXCLUSION_ACTIVITES",
            "ZAGRISE_CAMPUS",
        ],
        "privileges": [],
        "malus_collectif": {"type": "PROMO", "points": -10},
    },
    "ZONE_NOIRE": {
        "min": -9999,
        "max": -1,
        "nom": "Conseil de Discipline",
        "couleur": "#000000",
        "restrictions": [
            "TRIBUNAL",
            "GHOSTING",
            "NAMING_PUBLIC",
            "EXCLUSION_ACTIVITES",
        ],
        "privileges": [],
    },
}

# ══════════════════════════════════════════════════════════════
#  INFRACTION & BONUS REFERENCE
# ══════════════════════════════════════════════════════════════
INFRACTIONS = {
    # ── Zagrise & Image ─────────────────────────────────────
    "ZAG-001": {
        "nom": "Non-port zagrise",
        "points": -10,
        "categorie": "ZAG",
        "description": "Non-port de la zagrise en zone obligatoire",
    },
    "ZAG-002": {
        "nom": "Zagrise non conforme",
        "points": -5,
        "categorie": "ZAG",
        "description": "Zagrise sale, dégradée ou non conforme",
    },
    "ZAG-003": {
        "nom": "Perte zagrise",
        "points": -25,
        "categorie": "ZAG",
        "description": "Perte physique de la zagrise",
    },
    "ZAG-004": {
        "nom": "Perte Carn's",
        "points": -25,
        "categorie": "ZAG",
        "description": "Perte physique du Carn's (symbole sacré)",
    },
    # ── Ponctualité ─────────────────────────────────────────
    "PON-001": {
        "nom": "Retard mineur (<10min)",
        "points": -2,
        "categorie": "PON",
        "description": "Retard inférieur à 10 minutes",
    },
    "PON-002": {
        "nom": "Retard majeur (≥10min)",
        "points": -10,
        "categorie": "PON",
        "description": "Retard supérieur ou égal à 10 minutes",
    },
    "PON-003": {
        "nom": "Retard majeur + consigne",
        "points": -10,
        "categorie": "PON",
        "description": "Retard majeur avec consigne non respectée",
    },
    "PON-004": {
        "nom": "Absence non justifiée",
        "points": -25,
        "categorie": "PON",
        "description": "Absence à une réunion ou activité Trad's sans justification",
    },
    "PON-005": {
        "nom": "Silence radio",
        "points": -20,
        "categorie": "PON",
        "description": "Non-réponse à une convocation formelle",
    },
    # ── Comportement ────────────────────────────────────────
    "COM-001": {
        "nom": "Attitude nonchalante",
        "points": -5,
        "categorie": "COM",
        "description": "Mains dans les poches, avachi, téléphone en réunion",
    },
    "COM-002": {
        "nom": "Désolidarisation",
        "points": -20,
        "categorie": "COM",
        "description": "Refus d'entraide ou abandon d'un camarade",
    },
    "COM-003": {
        "nom": "Manque de respect",
        "points": -30,
        "categorie": "COM",
        "description": "Envers un Ancien, P3 ou personnel de l'école",
    },
    "COM-004": {
        "nom": "Récidive manque de respect",
        "points": -40,
        "categorie": "COM",
        "description": "2ème manquement dans les 30 derniers jours",
    },
    "COM-005": {
        "nom": "Trahison / délation",
        "points": -9999,
        "categorie": "COM",
        "description": "Mensonge avéré ou délation — Conseil immédiat",
    },
    # ── Bonus TIG ───────────────────────────────────────────
    "TIG-001": {
        "nom": "TIG standard (1h)",
        "points": 5,
        "categorie": "TIG",
        "description": "1 heure de travail validée par un Ancien",
    },
    "TIG-002": {
        "nom": "Initiative spontanée",
        "points": 10,
        "categorie": "TIG",
        "description": "Action non commandée résolvant un problème",
    },
    "TIG-003": {
        "nom": "Mission Commando",
        "points": 20,
        "categorie": "TIG",
        "description": "Tâche exceptionnelle validée par un Ancien",
    },
    "TIG-004": {
        "nom": "Semaine Exemplaire",
        "points": 5,
        "categorie": "TIG",
        "description": "0 log malus DIRECT sur 7 jours glissants (calcul auto)",
    },
    "TIG-005": {
        "nom": "Représentation digne Phase 1",
        "points": 8,
        "categorie": "TIG",
        "description": "Représentation exemplaire en Phase 1 ou événement, validé par P3",
    },
    # ── Système (auto-generated logs) ───────────────────────
    "SYS-MALUS-FAM": {
        "nom": "Malus Fam's",
        "points": -5,
        "categorie": "SYS",
        "description": "Solidarité Fam's — un membre est tombé en Zone Orange",
    },
    "SYS-MALUS-PROMO": {
        "nom": "Malus Promo",
        "points": -10,
        "categorie": "SYS",
        "description": "Solidarité Promo — un membre est tombé en Zone Rouge",
    },
    "SYS-CANCEL": {
        "nom": "Annulation log",
        "points": 0,
        "categorie": "SYS",
        "description": "Log annulé par un P3 (Kill Switch)",
    },
}

# ══════════════════════════════════════════════════════════════
#  ROLES
# ══════════════════════════════════════════════════════════════
ROLE_CONSCRIT = "CONSCRIT"
ROLE_ANCIEN = "ANCIEN"
ROLE_P3 = "P3"
ROLES = [ROLE_CONSCRIT, ROLE_ANCIEN, ROLE_P3]

# ══════════════════════════════════════════════════════════════
#  SOURCE TYPES (for anti-cascade)
# ══════════════════════════════════════════════════════════════
SOURCE_DIRECT = "DIRECT"
SOURCE_COLLECTIF = "COLLECTIF"
SOURCE_CANCEL = "CANCEL"

# ══════════════════════════════════════════════════════════════
#  ACTION TYPES
# ══════════════════════════════════════════════════════════════
ACTION_MALUS = "Malus"
ACTION_BONUS = "Bonus"
ACTION_MALUS_COLLECTIF = "Malus_Collectif"
ACTION_ANNULATION = "Annulation"

# ══════════════════════════════════════════════════════════════
#  NOTIFICATION MESSAGE TEMPLATES
# ══════════════════════════════════════════════════════════════
NOTIFICATION_MESSAGES = {
    "ZONE_JAUNE": {
        "titre": "⚠️ Zone Jaune",
        "body": "Sous surveillance. Fac manuscrite requise. Redresse le cap.",
    },
    "ZONE_ORANGE": {
        "titre": "🔶 Zone Orange — Probation",
        "body": "Accompagnement obligatoire. Ta Fam's vient de perdre 5 PC.",
    },
    "MALUS_FAM": {
        "titre": "🔶 Malus Fam's — {nom}",
        "body": "{nom} est tombé en Zone Orange. Ta Fam's perd 5 PC.",
    },
    "ZONE_ROUGE": {
        "titre": "🔴 Zone Rouge — Mise à Pied",
        "body": "Ghosting actif. Toute la promo vient de perdre 10 PC.",
    },
    "MALUS_PROMO": {
        "titre": "🚨 Malus Promo — {nom}",
        "body": "{nom} est en Zone Rouge. Toute la promo perd 10 PC.",
    },
    "ZONE_NOIRE": {
        "titre": "⚫ CONSEIL DE DISCIPLINE — {nom}",
        "body": "Convocation dans les 48h. Présence obligatoire.",
    },
    "REMONTEE": {
        "titre": "✅ Remontée — {zone_nouvelle}",
        "body": "Bien. Probation 7 jours active — restrictions précédentes maintenues.",
    },
    "CANCEL": {
        "titre": "↩️ Log annulé",
        "body": "Le log #{log_id} du {date} a été annulé par un P3. Points corrigés.",
    },
}

# ══════════════════════════════════════════════════════════════
#  ZAGRISE OBLIGATIONS BY ZONE
# ══════════════════════════════════════════════════════════════
ZAGRISE_OBLIGATIONS = {
    "ZONE_VERTE": {
        "perimetre": "École (Phase 3) uniquement",
        "tenue": "ouverte",
        "malus_defaut": -10,
    },
    "ZONE_JAUNE": {
        "perimetre": "École (Phase 3) uniquement",
        "tenue": "ouverte",
        "malus_defaut": -10,
    },
    "ZONE_ORANGE": {
        "perimetre": "Toute la Phase 3",
        "tenue": "boutonnée",
        "malus_defaut": -15,
    },
    "ZONE_ROUGE": {
        "perimetre": "Tout le campus (Phase 1 + Phase 3 + École)",
        "tenue": "obligatoire",
        "malus_defaut": -20,
    },
}
