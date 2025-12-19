"""
Unit tests for devolution module.

Tests:
- Legal reserve calculation (Art. 913 CC)
- Heir share calculation
- Representation (Art. 751+ CC)
- Spouse options (Art. 757 CC)
"""
import pytest
from datetime import date


class TestLegalReserve:
    """Tests for calculate_legal_reserve function."""
    
    def test_reserve_one_child(self):
        """1 enfant = réserve 1/2."""
        from succession_engine.core.devolution import calculate_legal_reserve
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        heirs = [
            FamilyMember(id="child1", birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD)
        ]
        
        reserve_fraction, _ = calculate_legal_reserve(heirs)
        assert reserve_fraction == 0.5
    
    def test_reserve_two_children(self):
        """2 enfants = réserve 2/3."""
        from succession_engine.core.devolution import calculate_legal_reserve
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        heirs = [
            FamilyMember(id="child1", birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD),
            FamilyMember(id="child2", birth_date=date(1992, 1, 1), relationship=HeirRelation.CHILD),
        ]
        
        reserve_fraction, _ = calculate_legal_reserve(heirs)
        assert reserve_fraction == pytest.approx(2/3, rel=0.01)
    
    def test_reserve_three_children(self):
        """3+ enfants = réserve 3/4."""
        from succession_engine.core.devolution import calculate_legal_reserve
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        heirs = [
            FamilyMember(id="child1", birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD),
            FamilyMember(id="child2", birth_date=date(1992, 1, 1), relationship=HeirRelation.CHILD),
            FamilyMember(id="child3", birth_date=date(1994, 1, 1), relationship=HeirRelation.CHILD),
        ]
        
        reserve_fraction, _ = calculate_legal_reserve(heirs)
        assert reserve_fraction == 0.75
    
    def test_reserve_no_children_no_parents(self):
        """Pas d'enfants ni de parents = pas de réserve."""
        from succession_engine.core.devolution import calculate_legal_reserve
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        heirs = [
            FamilyMember(id="spouse", birth_date=date(1960, 1, 1), relationship=HeirRelation.SPOUSE),
        ]
        
        reserve_fraction, _ = calculate_legal_reserve(heirs)
        assert reserve_fraction == 0.0
    
    def test_reserve_spouse_with_one_parent(self):
        """Conjoint + 1 parent = réserve 1/4."""
        from succession_engine.core.devolution import calculate_legal_reserve
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        heirs = [
            FamilyMember(id="spouse", birth_date=date(1960, 1, 1), relationship=HeirRelation.SPOUSE),
            FamilyMember(id="parent1", birth_date=date(1940, 1, 1), relationship=HeirRelation.PARENT),
        ]
        
        reserve_fraction, _ = calculate_legal_reserve(heirs)
        assert reserve_fraction == 0.25


class TestHeirShareCalculator:
    """Tests for HeirShareCalculator class."""
    
    def test_single_child_gets_100_percent(self):
        """Enfant unique hérite de 100%."""
        from succession_engine.core.devolution import HeirShareCalculator
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        calculator = HeirShareCalculator()
        heirs = [
            FamilyMember(id="child1", birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD),
        ]
        
        shares = calculator.calculate(heirs, None, 500000)
        
        assert shares["child1"] == 1.0
    
    def test_two_children_equal_shares(self):
        """2 enfants = 50% chacun."""
        from succession_engine.core.devolution import HeirShareCalculator
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        calculator = HeirShareCalculator()
        heirs = [
            FamilyMember(id="child1", birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD),
            FamilyMember(id="child2", birth_date=date(1992, 1, 1), relationship=HeirRelation.CHILD),
        ]
        
        shares = calculator.calculate(heirs, None, 500000)
        
        assert shares["child1"] == 0.5
        assert shares["child2"] == 0.5
    
    def test_spouse_alone_gets_100_percent(self):
        """Conjoint seul = 100%."""
        from succession_engine.core.devolution import HeirShareCalculator
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        calculator = HeirShareCalculator()
        heirs = [
            FamilyMember(id="spouse", birth_date=date(1960, 1, 1), relationship=HeirRelation.SPOUSE),
        ]
        
        shares = calculator.calculate(heirs, None, 500000)
        
        assert shares["spouse"] == 1.0
    
    def test_spouse_with_siblings(self):
        """Conjoint + frères = 50% conjoint, 50% frères."""
        from succession_engine.core.devolution import HeirShareCalculator
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        calculator = HeirShareCalculator()
        heirs = [
            FamilyMember(id="spouse", birth_date=date(1960, 1, 1), relationship=HeirRelation.SPOUSE),
            FamilyMember(id="sibling1", birth_date=date(1965, 1, 1), relationship=HeirRelation.SIBLING),
            FamilyMember(id="sibling2", birth_date=date(1967, 1, 1), relationship=HeirRelation.SIBLING),
        ]
        
        shares = calculator.calculate(heirs, None, 500000)
        
        assert shares["spouse"] == 0.5
        assert shares["sibling1"] == 0.25
        assert shares["sibling2"] == 0.25
    
    def test_three_children_equal_shares(self):
        """3 enfants = 1/3 chacun."""
        from succession_engine.core.devolution import HeirShareCalculator
        from succession_engine.schemas import FamilyMember, HeirRelation
        
        calculator = HeirShareCalculator()
        heirs = [
            FamilyMember(id="child1", birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD),
            FamilyMember(id="child2", birth_date=date(1992, 1, 1), relationship=HeirRelation.CHILD),
            FamilyMember(id="child3", birth_date=date(1994, 1, 1), relationship=HeirRelation.CHILD),
        ]
        
        shares = calculator.calculate(heirs, None, 500000)
        
        assert shares["child1"] == pytest.approx(1/3, rel=0.01)
        assert shares["child2"] == pytest.approx(1/3, rel=0.01)
        assert shares["child3"] == pytest.approx(1/3, rel=0.01)
    
    def test_rule_tracking_initialized(self):
        """Vérifier que le tracking des règles est initialisé."""
        from succession_engine.core.devolution import HeirShareCalculator
        
        calculator = HeirShareCalculator()
        
        assert calculator.applied_rule_ids == []
        assert calculator.excluded_rule_ids == []


class TestExcessiveLiberalities:
    """Tests for check_excessive_liberalities function."""
    
    def test_no_excess_returns_no_warning(self):
        """Pas d'excès = pas d'alerte."""
        from succession_engine.core.devolution import check_excessive_liberalities
        
        warnings = check_excessive_liberalities(
            reportable_donations_value=50000,
            bequests_total_value=50000,
            disposable_quota=150000,
            legal_reserve=350000,
            reserve_fraction=0.7
        )
        
        assert len(warnings) == 0
    
    def test_excess_returns_warning(self):
        """Libéralités excessives = alerte."""
        from succession_engine.core.devolution import check_excessive_liberalities
        
        warnings = check_excessive_liberalities(
            reportable_donations_value=100000,
            bequests_total_value=100000,
            disposable_quota=100000,  # Total 200k > QD 100k
            legal_reserve=400000,
            reserve_fraction=0.8
        )
        
        assert len(warnings) > 0
