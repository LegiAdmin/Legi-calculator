"""
Pytest configuration and fixtures for succession engine tests.
"""
import pytest
import json
from pathlib import Path

# Django setup
import django
from django.conf import settings


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure Django database for testing."""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


@pytest.fixture
def calculator():
    """Return an instance of SuccessionCalculator."""
    from succession_engine.core.calculator import SuccessionCalculator
    return SuccessionCalculator()


@pytest.fixture
def golden_scenarios():
    """Load golden scenarios from JSON file."""
    scenarios_path = Path(__file__).parent / "golden_scenarios.json"
    if scenarios_path.exists():
        with open(scenarios_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"scenarios": []}


@pytest.fixture
def fiscal_calculator():
    """Return FiscalCalculator for unit tests."""
    from succession_engine.rules.fiscal import FiscalCalculator
    return FiscalCalculator


@pytest.fixture
def usufruct_valuator():
    """Return UsufructValuator for unit tests."""
    from succession_engine.rules.usufruct import UsufructValuator
    return UsufructValuator


@pytest.fixture
def sample_child_heir():
    """Return a sample CHILD heir for testing."""
    from succession_engine.schemas import FamilyMember, HeirRelation
    from datetime import date
    return FamilyMember(
        id="test_child_1",
        birth_date=date(1990, 1, 1),
        relationship=HeirRelation.CHILD,
        is_from_current_union=True,
        is_disabled=False
    )


@pytest.fixture
def sample_spouse():
    """Return a sample SPOUSE for testing."""
    from succession_engine.schemas import FamilyMember, HeirRelation
    from datetime import date
    return FamilyMember(
        id="test_spouse",
        birth_date=date(1960, 5, 15),
        relationship=HeirRelation.SPOUSE,
        is_from_current_union=True,
        is_disabled=False
    )


@pytest.fixture
def sample_asset():
    """Return a sample Asset for testing."""
    from succession_engine.schemas import Asset, OwnershipMode, AssetOrigin
    return Asset(
        id="test_asset_1",
        estimated_value=500000,
        ownership_mode=OwnershipMode.FULL_OWNERSHIP,
        asset_origin=AssetOrigin.PERSONAL_PROPERTY
    )
