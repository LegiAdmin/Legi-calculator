"""
Unit tests for usufruct valuation.

Tests for:
- Age-based usufruct rates (Art. 669 CGI)
- Value calculations
"""
import pytest
from datetime import date


class TestUsufructRates:
    """Tests for usufruct rates by age (Art. 669 CGI)."""
    
    def test_under_21_rate(self):
        """Under 21 years = 90% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(20) == 0.90
    
    def test_21_to_30_rate(self):
        """21-30 years = 80% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(25) == 0.80
    
    def test_31_to_40_rate(self):
        """31-40 years = 70% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(35) == 0.70
    
    def test_41_to_50_rate(self):
        """41-50 years = 60% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(45) == 0.60
    
    def test_51_to_60_rate(self):
        """51-60 years = 50% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(55) == 0.50
    
    def test_61_to_70_rate(self):
        """61-70 years = 40% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(65) == 0.40
    
    def test_71_to_80_rate(self):
        """71-80 years = 30% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(75) == 0.30
    
    def test_81_to_90_rate(self):
        """81-90 years = 20% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(85) == 0.20
    
    def test_over_91_rate(self):
        """Over 91 years = 10% usufruct."""
        from succession_engine.rules.usufruct import UsufructValuator
        assert UsufructValuator.get_usufruct_rate(92) == 0.10


class TestUsufructValueCalculation:
    """Tests for usufruct value calculations."""
    
    def test_calculate_value_65_years_old(self):
        """Test usufruct calculation for 65-year-old."""
        from succession_engine.rules.usufruct import UsufructValuator
        
        usufruct_value, bare_ownership_value, rate = UsufructValuator.calculate_value(
            total_value=100000,
            usufructuary_birth_date=date(1960, 1, 1),
            reference_date=date(2025, 1, 1)
        )
        
        # 65 years old = 40% usufruct
        assert rate == 0.40
        assert usufruct_value == pytest.approx(40000, rel=0.01)
        assert bare_ownership_value == pytest.approx(60000, rel=0.01)
    
    def test_bare_ownership_rate_complement(self):
        """Bare ownership rate should be complement of usufruct rate."""
        from succession_engine.rules.usufruct import UsufructValuator
        
        for age in [20, 30, 40, 50, 60, 70, 80, 90, 95]:
            usufruct_rate = UsufructValuator.get_usufruct_rate(age)
            bare_ownership_rate = UsufructValuator.get_bare_ownership_rate(age)
            assert usufruct_rate + bare_ownership_rate == 1.0
