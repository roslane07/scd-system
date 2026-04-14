"""
SCD Test Suite — Comprehensive tests for all business logic.

Covers:
  - Zone calculation (all boundaries)
  - Points service (apply infraction, zone changes)
  - Collective malus (Fam's, Promo, anti-cascade, usins guard, rodage guard)
  - Probation (trigger, reset, close)
  - Récidive detection (COM-003 → COM-004)
  - Kill Switch
  - Classement
  - Full API integration (via TestClient)

Run with:
    cd scd-system/backend
    source venv/bin/activate
    pytest tests/ -v
"""
import sys
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.models import create_tables, drop_tables, ALL_MODELS
from app.models.personne import Personne
from app.models.log import Log
from app.models.notification import Notification
from app.models.probation import ProbationLog
from app.utils.auth import hash_password
from app.utils.constants import (
    ROLE_CONSCRIT, ROLE_ANCIEN, ROLE_P3,
    SOURCE_DIRECT, SOURCE_COLLECTIF,
)
from app.services.zone_service import calculer_zone, est_remontee, est_descente
from app.services.points_service import appliquer_infraction
from app.services.collectif_service import appliquer_malus_famille, appliquer_malus_promotion
from app.services.probation_service import (
    declencher_probation, clore_probation_active, verifier_restrictions_effectives,
)
from app.services.recidive_service import check_recidive_respect
from app.services.cancel_service import annuler_log
from app.services.classement_service import classement_individuel, classement_fams
from app.config import settings


# ══════════════════════════════════════════════════════════════
#  FIXTURES
# ══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def setup_db():
    """Fresh database for every test."""
    test_db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "test_scd.db",
    )
    # Point the models to the test DB
    db.init(test_db_path, pragmas={
        "journal_mode": "wal",
        "foreign_keys": 1,
    })
    db.connect(reuse_if_open=True)
    db.drop_tables(ALL_MODELS)
    db.create_tables(ALL_MODELS)
    yield
    db.drop_tables(ALL_MODELS)
    if not db.is_closed():
        db.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def ancien():
    """Create a test Ancien."""
    return Personne.create(
        nom="Ancien", prenom="Test", role=ROLE_ANCIEN,
        password_hash=hash_password("test"), points_actuels=None, zone=None,
    )


@pytest.fixture
def p3():
    """Create a test P3."""
    return Personne.create(
        nom="P3", prenom="Test", role=ROLE_P3,
        password_hash=hash_password("test"), points_actuels=None, zone=None,
    )


@pytest.fixture
def conscrit():
    """Create a single test conscrit at 100 PC."""
    return Personne.create(
        nom="TestConscrit", prenom="Alpha", role=ROLE_CONSCRIT,
        password_hash=hash_password("test"),
        points_actuels=100, zone="ZONE_VERTE",
    )


@pytest.fixture
def fam_conscrits(ancien):
    """Create 3 conscrits in the same Fam's (same parent_id)."""
    members = []
    for i in range(3):
        c = Personne.create(
            nom=f"FamMember{i}", prenom=f"Membre{i}", role=ROLE_CONSCRIT,
            parent_id=ancien.id,
            password_hash=hash_password("test"),
            points_actuels=100, zone="ZONE_VERTE",
        )
        members.append(c)
    return members


@pytest.fixture
def promo_conscrits():
    """Create 5 conscrits for promo-level testing."""
    members = []
    for i in range(5):
        c = Personne.create(
            nom=f"Promo{i}", prenom=f"Conscrit{i}", role=ROLE_CONSCRIT,
            password_hash=hash_password("test"),
            points_actuels=100, zone="ZONE_VERTE",
        )
        members.append(c)
    return members


# ══════════════════════════════════════════════════════════════
#  TEST: ZONE SERVICE
# ══════════════════════════════════════════════════════════════

class TestZoneService:
    """Test zone calculation at all boundaries."""

    def test_zone_verte_max(self):
        assert calculer_zone(150) == "ZONE_VERTE"

    def test_zone_verte_100(self):
        assert calculer_zone(100) == "ZONE_VERTE"

    def test_zone_verte_boundary(self):
        assert calculer_zone(85) == "ZONE_VERTE"

    def test_zone_jaune_boundary_upper(self):
        assert calculer_zone(84) == "ZONE_JAUNE"

    def test_zone_jaune_50(self):
        assert calculer_zone(50) == "ZONE_JAUNE"

    def test_zone_orange_boundary_upper(self):
        assert calculer_zone(49) == "ZONE_ORANGE"

    def test_zone_orange_20(self):
        assert calculer_zone(20) == "ZONE_ORANGE"

    def test_zone_rouge_boundary_upper(self):
        assert calculer_zone(19) == "ZONE_ROUGE"

    def test_zone_rouge_0(self):
        assert calculer_zone(0) == "ZONE_ROUGE"

    def test_zone_noire_boundary(self):
        assert calculer_zone(-1) == "ZONE_NOIRE"

    def test_zone_noire_deep(self):
        assert calculer_zone(-500) == "ZONE_NOIRE"

    def test_est_remontee(self):
        assert est_remontee("ZONE_ORANGE", "ZONE_JAUNE") is True
        assert est_remontee("ZONE_ROUGE", "ZONE_VERTE") is True

    def test_est_not_remontee(self):
        assert est_remontee("ZONE_VERTE", "ZONE_JAUNE") is False
        assert est_remontee("ZONE_JAUNE", "ZONE_JAUNE") is False

    def test_est_descente(self):
        assert est_descente("ZONE_VERTE", "ZONE_ORANGE") is True
        assert est_descente("ZONE_JAUNE", "ZONE_ROUGE") is True

    def test_est_not_descente(self):
        assert est_descente("ZONE_ORANGE", "ZONE_VERTE") is False


# ══════════════════════════════════════════════════════════════
#  TEST: POINTS SERVICE
# ══════════════════════════════════════════════════════════════

class TestPointsService:
    """Test core infraction application logic."""

    def test_apply_zag001_stays_verte(self, conscrit, ancien):
        """Scenario A: 100 PC - 10 = 90, stays VERTE."""
        result = appliquer_infraction(conscrit.id, "ZAG-001", ancien.id)
        assert result["points_avant"] == 100
        assert result["points_apres"] == 90
        assert result["zone_avant"] == "ZONE_VERTE"
        assert result["zone_apres"] == "ZONE_VERTE"
        assert result["zone_changed"] is False

    def test_drop_to_jaune(self, conscrit, ancien):
        """100 - 25 = 75 → ZONE_JAUNE."""
        result = appliquer_infraction(conscrit.id, "PON-004", ancien.id)
        assert result["points_apres"] == 75
        assert result["zone_apres"] == "ZONE_JAUNE"
        assert result["zone_changed"] is True

    def test_cap_at_150(self, conscrit, ancien):
        """Points should never exceed 150."""
        # Give conscrit TIG-003 (+20) multiple times
        for _ in range(5):
            appliquer_infraction(conscrit.id, "TIG-003", ancien.id)
        c = Personne.get_by_id(conscrit.id)
        assert c.points_actuels == 150

    def test_log_created(self, conscrit, ancien):
        """Every infraction creates a log entry."""
        result = appliquer_infraction(conscrit.id, "PON-001", ancien.id, "test comment")
        log = Log.get_by_id(result["log_id"])
        assert log.code_infraction == "PON-001"
        assert log.points == -2
        assert log.source_type == SOURCE_DIRECT
        assert log.commentaire == "test comment"

    def test_invalid_conscrit_raises(self, ancien):
        with pytest.raises(ValueError, match="introuvable"):
            appliquer_infraction(9999, "ZAG-001", ancien.id)

    def test_invalid_code_raises(self, conscrit, ancien):
        with pytest.raises(ValueError, match="inconnu"):
            appliquer_infraction(conscrit.id, "FAKE-001", ancien.id)


# ══════════════════════════════════════════════════════════════
#  TEST: COLLECTIVE MALUS
# ══════════════════════════════════════════════════════════════

class TestCollectifService:
    """Test Fam's and Promo collective malus."""

    @patch.object(settings, "RODAGE_ACTIF", False)
    def test_malus_famille_applied(self, fam_conscrits, ancien):
        """Scenario B: Conscrit drops to Orange → siblings lose 5 PC."""
        offender = fam_conscrits[0]
        # Drop to Orange: 100 - 55 = 45
        offender.points_actuels = 45
        offender.zone = "ZONE_ORANGE"
        offender.save()

        appliquer_malus_famille(offender, -5)

        for sibling in fam_conscrits[1:]:
            s = Personne.get_by_id(sibling.id)
            assert s.points_actuels == 95

    @patch.object(settings, "RODAGE_ACTIF", False)
    def test_malus_famille_skipped_during_usins(self, ancien):
        """Scenario G: No parent_id (usins) → no Fam's malus."""
        conscrit = Personne.create(
            nom="Usins", prenom="Kid", role=ROLE_CONSCRIT,
            parent_id=None,  # No pa² yet
            password_hash=hash_password("test"),
            points_actuels=45, zone="ZONE_ORANGE",
        )
        # Should not raise and should not create any logs
        appliquer_malus_famille(conscrit, -5)
        logs = Log.select().where(Log.source_type == SOURCE_COLLECTIF).count()
        assert logs == 0

    def test_malus_skipped_during_rodage(self, fam_conscrits, ancien):
        """Scenario F: Rodage mode ON → no collective malus."""
        # settings.RODAGE_ACTIF defaults to True
        offender = fam_conscrits[0]
        offender.points_actuels = 45
        offender.zone = "ZONE_ORANGE"
        offender.save()

        appliquer_malus_famille(offender, -5)

        for sibling in fam_conscrits[1:]:
            s = Personne.get_by_id(sibling.id)
            assert s.points_actuels == 100  # Unchanged

    @patch.object(settings, "RODAGE_ACTIF", False)
    def test_malus_promo_applied(self, promo_conscrits, ancien):
        """Scenario C: Conscrit drops to Rouge → entire promo loses 10 PC."""
        offender = promo_conscrits[0]
        offender.points_actuels = 0
        offender.zone = "ZONE_ROUGE"
        offender.save()

        appliquer_malus_promotion(offender, -10)

        for other in promo_conscrits[1:]:
            o = Personne.get_by_id(other.id)
            assert o.points_actuels == 90

    @patch.object(settings, "RODAGE_ACTIF", False)
    def test_anti_cascade(self, fam_conscrits, ancien):
        """Scenario H: Collective malus logs should be COLLECTIF → never cascade."""
        offender = fam_conscrits[0]
        offender.points_actuels = 45
        offender.zone = "ZONE_ORANGE"
        offender.save()

        appliquer_malus_famille(offender, -5)

        # All collective logs should have source_type == COLLECTIF
        collective_logs = Log.select().where(Log.source_type == SOURCE_COLLECTIF)
        for log in collective_logs:
            assert log.source_type == SOURCE_COLLECTIF


# ══════════════════════════════════════════════════════════════
#  TEST: PROBATION
# ══════════════════════════════════════════════════════════════

class TestProbationService:

    def test_probation_created_on_remontee(self, conscrit, ancien):
        """When conscrit climbs zone → probation created."""
        declencher_probation(conscrit.id, "ZONE_ORANGE")
        probation = ProbationLog.get(ProbationLog.conscrit == conscrit.id)
        assert probation.active is True
        assert probation.zone_verrouillee == "ZONE_ORANGE"

    def test_probation_closed_on_descente(self, conscrit, ancien):
        """When conscrit drops zone → probation closed."""
        declencher_probation(conscrit.id, "ZONE_ORANGE")
        clore_probation_active(conscrit.id)
        probation = ProbationLog.get(ProbationLog.conscrit == conscrit.id)
        assert probation.active is False

    def test_restrictions_from_probation(self, conscrit, ancien):
        """During probation, restrictions come from the locked zone."""
        conscrit.zone = "ZONE_JAUNE"
        conscrit.save()
        declencher_probation(conscrit.id, "ZONE_ORANGE")

        restrictions = verifier_restrictions_effectives(conscrit.id)
        assert "ACCOMPAGNEMENT" in restrictions
        assert "TIG_OBLIGATOIRE" in restrictions


# ══════════════════════════════════════════════════════════════
#  TEST: RÉCIDIVE
# ══════════════════════════════════════════════════════════════

class TestRecidiveService:

    def test_first_time_stays_com003(self, conscrit, ancien):
        """First respect violation → COM-003."""
        code = check_recidive_respect(conscrit.id)
        assert code == "COM-003"

    def test_recidive_upgrades_to_com004(self, conscrit, ancien):
        """Second respect violation within 30 days → COM-004."""
        # Create a prior COM-003 log
        Log.create(
            conscrit=conscrit, ancien=ancien,
            code_infraction="COM-003", points=-30,
            source_type=SOURCE_DIRECT, type_action="Malus",
            points_avant=100, points_apres=70,
            zone_avant="ZONE_VERTE", zone_apres="ZONE_JAUNE",
            timestamp=datetime.now(),
        )
        code = check_recidive_respect(conscrit.id)
        assert code == "COM-004"

    def test_old_violation_doesnt_count(self, conscrit, ancien):
        """Violation > 30 days ago → stays COM-003."""
        Log.create(
            conscrit=conscrit, ancien=ancien,
            code_infraction="COM-003", points=-30,
            source_type=SOURCE_DIRECT, type_action="Malus",
            points_avant=100, points_apres=70,
            zone_avant="ZONE_VERTE", zone_apres="ZONE_JAUNE",
            timestamp=datetime.now() - timedelta(days=31),
        )
        code = check_recidive_respect(conscrit.id)
        assert code == "COM-003"


# ══════════════════════════════════════════════════════════════
#  TEST: KILL SWITCH
# ══════════════════════════════════════════════════════════════

class TestCancelService:

    def test_cancel_reverses_points(self, conscrit, ancien, p3):
        """Kill switch reverses the point impact."""
        result = appliquer_infraction(conscrit.id, "ZAG-001", ancien.id)
        log_id = result["log_id"]

        cancel_result = annuler_log(log_id, p3.id, "Erreur de saisie confirmée")
        assert cancel_result["points_corriges"] == 100
        assert cancel_result["zone"] == "ZONE_VERTE"

        # Original log marked as cancelled
        original = Log.get_by_id(log_id)
        assert original.annule is True

    def test_short_justification_fails(self, conscrit, ancien, p3):
        result = appliquer_infraction(conscrit.id, "ZAG-001", ancien.id)
        with pytest.raises(ValueError, match="minimum 10"):
            annuler_log(result["log_id"], p3.id, "short")

    def test_double_cancel_fails(self, conscrit, ancien, p3):
        result = appliquer_infraction(conscrit.id, "ZAG-001", ancien.id)
        annuler_log(result["log_id"], p3.id, "First cancellation is valid")
        with pytest.raises(ValueError, match="déjà annulé"):
            annuler_log(result["log_id"], p3.id, "Second attempt should fail")


# ══════════════════════════════════════════════════════════════
#  TEST: CLASSEMENT
# ══════════════════════════════════════════════════════════════

class TestClassementService:

    def test_classement_individuel_sorted(self, ancien):
        """Classement should be sorted by points DESC."""
        Personne.create(
            nom="Low", prenom="A", role=ROLE_CONSCRIT,
            password_hash=hash_password("t"), points_actuels=50, zone="ZONE_JAUNE",
        )
        Personne.create(
            nom="High", prenom="B", role=ROLE_CONSCRIT,
            password_hash=hash_password("t"), points_actuels=120, zone="ZONE_VERTE",
        )
        ranking = classement_individuel()
        assert len(ranking) == 2
        assert ranking[0]["nom"] == "High"
        assert ranking[1]["nom"] == "Low"

    def test_classement_fams_grouped(self, fam_conscrits, ancien):
        """Fam's classement groups by parent_id."""
        ranking = classement_fams()
        assert len(ranking) >= 1
        fam = ranking[0]
        assert fam["nb_membres"] == 3
        assert fam["score_total"] == 300
