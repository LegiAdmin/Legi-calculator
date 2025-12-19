"""
Unit tests for fiscal calculations.

Tests for:
- Allowances (abatements)
- Tax brackets
- Professional exemptions
"""
import pytest
from decimal import Decimal


class TestAllowances:
    """Tests for tax allowances (abattements)."""
    
    def test_child_allowance_value(self):
        """Child allowance should be 100,000€."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['CHILD'] == 100_000.0
    
    def test_sibling_allowance_value(self):
        """Sibling allowance should be 15,932€."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['SIBLING'] == 15_932.0
    
    def test_other_allowance_value(self):
        """Other allowance should be 1,594€."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['OTHER'] == 1_594.0
    
    def test_nephew_niece_allowance_value(self):
        """Nephew/niece allowance should be 7,967€."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['NEPHEW_NIECE'] == 7_967.0
    
    def test_spouse_exempt(self):
        """Spouse should be fully exempt (infinite allowance)."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['SPOUSE'] == float('inf')
    
    def test_disability_allowance_value(self):
        """Disability allowance should be 159,325€."""
        from succession_engine.constants import DISABILITY_ALLOWANCE
        assert DISABILITY_ALLOWANCE == 159_325.0


class TestLegalReserve:
    """Tests for legal reserve fractions (réserve héréditaire)."""
    
    def test_one_child_reserve(self):
        """1 child = 1/2 reserve."""
        from succession_engine.constants import RESERVE_CHILDREN
        assert RESERVE_CHILDREN[1] == 1/2
    
    def test_two_children_reserve(self):
        """2 children = 2/3 reserve."""
        from succession_engine.constants import RESERVE_CHILDREN
        assert RESERVE_CHILDREN[2] == 2/3
    
    def test_three_children_reserve(self):
        """3+ children = 3/4 reserve."""
        from succession_engine.constants import RESERVE_CHILDREN
        assert RESERVE_CHILDREN[3] == 3/4


class TestLifeInsuranceThresholds:
    """Tests for life insurance thresholds."""
    
    def test_before_70_allowance(self):
        """Before 70 allowance should be 152,500€ per beneficiary."""
        from succession_engine.constants import LIFE_INSURANCE_ALLOWANCE_BEFORE_70
        assert LIFE_INSURANCE_ALLOWANCE_BEFORE_70 == 152_500.0
    
    def test_after_70_allowance(self):
        """After 70 allowance should be 30,500€ global."""
        from succession_engine.constants import LIFE_INSURANCE_ALLOWANCE_AFTER_70
        assert LIFE_INSURANCE_ALLOWANCE_AFTER_70 == 30_500.0


class TestDutreilExemption:
    """Tests for Dutreil exemption rate."""
    
    def test_dutreil_rate(self):
        """Dutreil exemption should be 75%."""
        from succession_engine.constants import DUTREIL_EXEMPTION_RATE
        assert DUTREIL_EXEMPTION_RATE == 0.75
