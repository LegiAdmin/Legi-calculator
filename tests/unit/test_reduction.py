"""
Unit tests for reduction calculation (Art. 920+ CC).

Tests:
- No reduction when liberalities <= disposable quota
- Reduction calculation when excess
- Order of reduction (bequests first, then donations by date)
"""
import pytest
from datetime import date
from succession_engine.rules.reduction import Liberality, ReductionCalculator


class TestReductionCalculator:
    """Tests for ReductionCalculator class."""
    
    def test_no_reduction_under_quota(self):
        """Pas de réduction si libéralités <= quotité disponible."""
        liberalities = [
            Liberality(id="don1", type="DONATION", beneficiary_id="ami", value=50000, date=date(2020, 1, 1))
        ]
        
        result = ReductionCalculator.calculate_reduction(
            liberalities=liberalities,
            disposable_quota=100000,
            legal_reserve=300000
        )
        
        assert result.total_excess == 0.0
        assert len(result.reduced_liberalities) == 0
        assert result.reserve_restored == 0.0
    
    def test_reduction_simple_excess(self):
        """Réduction si donations > quotité disponible."""
        liberalities = [
            Liberality(id="don1", type="DONATION", beneficiary_id="ami", value=150000, date=date(2020, 1, 1))
        ]
        
        result = ReductionCalculator.calculate_reduction(
            liberalities=liberalities,
            disposable_quota=100000,
            legal_reserve=300000
        )
        
        assert result.total_excess == 50000.0
        assert len(result.reduced_liberalities) == 1
        assert result.reduced_liberalities[0]["reduction_amount"] == 50000.0
        assert result.reduced_liberalities[0]["reduced_value"] == 100000.0
    
    def test_reduction_order_bequests_first(self):
        """Les legs sont réduits avant les donations."""
        liberalities = [
            Liberality(id="don1", type="DONATION", beneficiary_id="ami", value=80000, date=date(2020, 1, 1)),
            Liberality(id="legs1", type="BEQUEST", beneficiary_id="asso", value=80000, date=date(2023, 1, 1)),
        ]
        
        result = ReductionCalculator.calculate_reduction(
            liberalities=liberalities,
            disposable_quota=100000,  # Total 160k > QD 100k = 60k excess
            legal_reserve=300000
        )
        
        assert result.total_excess == 60000.0
        # Le legs doit être réduit en premier
        assert result.reduced_liberalities[0]["liberality_id"] == "legs1"
        assert result.reduced_liberalities[0]["reduction_amount"] == 60000.0
    
    def test_reduction_donations_by_date(self):
        """Les donations sont réduites du plus récent au plus ancien."""
        liberalities = [
            Liberality(id="don_old", type="DONATION", beneficiary_id="ami1", value=50000, date=date(2010, 1, 1)),
            Liberality(id="don_new", type="DONATION", beneficiary_id="ami2", value=50000, date=date(2023, 1, 1)),
        ]
        
        result = ReductionCalculator.calculate_reduction(
            liberalities=liberalities,
            disposable_quota=50000,  # Total 100k > QD 50k = 50k excess
            legal_reserve=200000
        )
        
        assert result.total_excess == 50000.0
        # La donation la plus récente doit être réduite en premier
        assert result.reduced_liberalities[0]["liberality_id"] == "don_new"
        assert result.reduced_liberalities[0]["reduction_amount"] == 50000.0
    
    def test_generate_warning_when_excess(self):
        """Génération de warnings en cas d'excès."""
        liberalities = [
            Liberality(id="don1", type="DONATION", beneficiary_id="ami", value=150000, date=date(2020, 1, 1))
        ]
        
        result = ReductionCalculator.calculate_reduction(
            liberalities=liberalities,
            disposable_quota=100000,
            legal_reserve=300000
        )
        
        warnings = ReductionCalculator.generate_reduction_warning(result)
        
        assert len(warnings) > 0
        assert "RÉDUCTION NÉCESSAIRE" in warnings[0]
