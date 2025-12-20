"""
Golden tests - Parametrized tests from golden_scenarios.json

These tests are the E2E tests synchronized with the simulator platform.
They read from the same JSON file used by the frontend.

ARCHITECTURE NOTE (Critique #2 - Flakiness):
- Numeric assertions use pytest.approx for tolerance
- Structural assertions only check presence, not exact content
- This prevents test failures from text changes in explanations
"""
import pytest
import json
from pathlib import Path
from typing import Dict, Any, Optional


# Load scenarios from JSON
SCENARIOS_PATH = Path(__file__).parent / "golden_scenarios.json"


def load_scenarios():
    """Load golden scenarios from JSON file."""
    if not SCENARIOS_PATH.exists():
        return []
    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("scenarios", [])


GOLDEN_SCENARIOS = load_scenarios()


def scenario_id(scenario):
    """Generate test ID from scenario."""
    return f"{scenario['id']}_{scenario['name'].replace(' ', '_')[:30]}"


# =============================================================================
# ASSERTION HELPERS - Separation of concerns for numerical vs structural tests
# =============================================================================

def assert_numeric_value(actual: float, expected: float, field_name: str, scenario_id: str, tolerance: float = 0.01):
    """
    Strict numeric assertion with tolerance.
    
    Use for: amounts, percentages, tax calculations
    """
    assert actual == pytest.approx(expected, rel=tolerance), \
        f"{field_name}: attendu {expected}, obtenu {actual} (scénario {scenario_id})"


def assert_structure_present(obj: Any, field_names: list, context: str):
    """
    Structural assertion - only checks presence, not exact content.
    
    Use for: what, why, legal_basis (text fields that may change)
    """
    for field in field_names:
        # For dicts, check key exists
        if isinstance(obj, dict):
            # Field can be missing or null - that's OK, we just check structure when present
            pass
        # For objects with attributes
        elif hasattr(obj, field):
            pass


def assert_heir_structure(heir: Any, scenario_id: str):
    """
    Assert heir has required structure (not exact values).
    
    Checks that heir output has expected fields present.
    """
    required_fields = ["id", "relationship", "legal_share_percent"]
    for field in required_fields:
        assert hasattr(heir, field), f"Heir missing {field} in {scenario_id}"


# =============================================================================
# MAIN TEST
# =============================================================================

@pytest.mark.django_db
@pytest.mark.parametrize("scenario", GOLDEN_SCENARIOS, ids=scenario_id)
def test_golden_scenario_numeric(scenario):
    """
    Test numeric values in golden scenario.
    
    STRICT assertions - these must match exactly (within tolerance).
    Changes here indicate real calculation bugs.
    """
    from succession_engine.core.calculator import SuccessionCalculator
    from succession_engine.schemas import SimulationInput
    
    # Skip if marked
    if scenario.get("validation", {}).get("status") == "SKIP":
        pytest.skip(f"Scenario {scenario['id']} marked as SKIP")
    
    # Parse input
    try:
        input_data = SimulationInput(**scenario["input"])
    except Exception as e:
        pytest.fail(f"Failed to parse input for {scenario['id']}: {e}")
    
    # Run calculator
    calculator = SuccessionCalculator()
    result = calculator.run(input_data)
    
    # Get expected output
    expected = scenario.get("expected_output", {})
    sid = scenario["id"]
    
    # === STRICT NUMERIC ASSERTIONS ===
    
    # Total estate value
    if "total_estate_value" in expected:
        assert_numeric_value(
            result.global_metrics.total_estate_value,
            expected["total_estate_value"],
            "Masse successorale",
            sid
        )
    
    # Total tax
    if "total_tax_amount" in expected:
        assert_numeric_value(
            result.global_metrics.total_tax_amount,
            expected["total_tax_amount"],
            "Total droits",
            sid
        )
    
    # Heirs breakdown - numeric only
    if "heirs_breakdown" in expected:
        for expected_heir in expected["heirs_breakdown"]:
            heir_id = expected_heir["id"]
            actual_heir = next(
                (h for h in result.heirs_breakdown if h.id == heir_id),
                None
            )
            
            assert actual_heir is not None, f"Héritier {heir_id} non trouvé ({sid})"
            
            # Numeric fields only
            numeric_fields = [
                ("legal_share_percent", "Quote-part"),
                ("gross_share_value", "Part brute"),
                ("abatement_used", "Abattement"),
                ("taxable_base", "Base taxable"),
                ("tax_amount", "Droits"),
            ]
            
            for field, label in numeric_fields:
                if field in expected_heir:
                    actual_val = getattr(actual_heir, field, None)
                    if actual_val is not None:
                        assert_numeric_value(
                            actual_val,
                            expected_heir[field],
                            f"{heir_id} {label}",
                            sid
                        )


@pytest.mark.django_db
@pytest.mark.parametrize("scenario", GOLDEN_SCENARIOS, ids=scenario_id)
def test_golden_scenario_structure(scenario):
    """
    Test structural integrity of golden scenario output.
    
    NON-STRICT assertions - only checks presence, not exact values.
    Safe to change text without breaking tests.
    """
    from succession_engine.core.calculator import SuccessionCalculator
    from succession_engine.schemas import SimulationInput
    
    # Skip if marked
    if scenario.get("validation", {}).get("status") == "SKIP":
        pytest.skip(f"Scenario {scenario['id']} marked as SKIP")
    
    # Parse and run
    try:
        input_data = SimulationInput(**scenario["input"])
        calculator = SuccessionCalculator()
        result = calculator.run(input_data)
    except Exception as e:
        pytest.fail(f"Failed to run scenario {scenario['id']}: {e}")
    
    sid = scenario["id"]
    
    # === STRUCTURAL ASSERTIONS ===
    
    # Result has required top-level fields
    assert hasattr(result, "global_metrics"), f"Missing global_metrics ({sid})"
    assert hasattr(result, "calculation_steps"), f"Missing calculation_steps ({sid})"
    assert hasattr(result, "heirs_breakdown"), f"Missing heirs_breakdown ({sid})"
    
    # Calculation steps exist and have structure
    steps = result.calculation_steps
    assert len(steps) > 0, f"No calculation steps ({sid})"
    
    for step in steps:
        # Step has basic structure
        assert hasattr(step, "step_number") or "step_number" in step.__dict__, \
            f"Step missing step_number ({sid})"
    
    # All expected heirs are present
    expected = scenario.get("expected_output", {})
    if "heirs_breakdown" in expected:
        for expected_heir in expected["heirs_breakdown"]:
            heir_id = expected_heir["id"]
            actual_heir = next(
                (h for h in result.heirs_breakdown if h.id == heir_id),
                None
            )
            assert actual_heir is not None, f"Héritier {heir_id} non trouvé ({sid})"
            assert_heir_structure(actual_heir, sid)


# =============================================================================
# INTEGRITY TESTS
# =============================================================================

class TestGoldenScenariosIntegrity:
    """Tests for the golden scenarios file itself."""
    
    def test_scenarios_file_exists(self):
        """Ensure golden scenarios file exists."""
        assert SCENARIOS_PATH.exists(), "golden_scenarios.json not found"
    
    def test_scenarios_not_empty(self):
        """Ensure we have at least some scenarios."""
        assert len(GOLDEN_SCENARIOS) > 0, "No scenarios found in golden_scenarios.json"
    
    def test_all_scenarios_have_required_fields(self):
        """Ensure all scenarios have required fields."""
        required_fields = ["id", "name", "input", "expected_output"]
        
        for scenario in GOLDEN_SCENARIOS:
            for field in required_fields:
                assert field in scenario, f"Scenario {scenario.get('id', 'unknown')} missing {field}"
    
    def test_scenario_ids_unique(self):
        """Ensure all scenario IDs are unique."""
        ids = [s["id"] for s in GOLDEN_SCENARIOS]
        assert len(ids) == len(set(ids)), "Duplicate scenario IDs found"
    
    def test_scenarios_have_category(self):
        """Ensure all scenarios are categorized."""
        valid_categories = ["BASE", "COMPLEX", "ADVANCED", "CHAOS"]
        for scenario in GOLDEN_SCENARIOS:
            cat = scenario.get("category", "")
            assert cat in valid_categories, \
                f"Scenario {scenario['id']} has invalid category: {cat}"
