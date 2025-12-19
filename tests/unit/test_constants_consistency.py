"""
Test de cohérence entre constants.py et les données fiscales attendues.

Ce test s'assure que les valeurs hardcodées dans constants.py
correspondent bien à la législation en vigueur (2025).

Si ce test échoue, il faut synchroniser :
- constants.py (fallback pour les tests)
- scripts/seed_legislation_2025.py (données BDD prod)
"""
import pytest


class TestFiscalDataConsistency:
    """Vérifie la cohérence des données fiscales hardcodées."""
    
    def test_child_allowance_2025(self):
        """Abattement enfant = 100 000€ (Art. 779 CGI)."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['CHILD'] == 100_000.0
    
    def test_sibling_allowance_2025(self):
        """Abattement frère/sœur = 15 932€ (Art. 779 CGI)."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['SIBLING'] == 15_932.0
    
    def test_nephew_niece_allowance_2025(self):
        """Abattement neveu/nièce = 7 967€ (Art. 779 CGI)."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['NEPHEW_NIECE'] == 7_967.0
    
    def test_other_allowance_2025(self):
        """Abattement autres = 1 594€ (Art. 779 CGI)."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['OTHER'] == 1_594.0
    
    def test_spouse_exempt(self):
        """Conjoint/PACS exonéré (Loi TEPA 2007)."""
        from succession_engine.constants import ALLOWANCES
        assert ALLOWANCES['SPOUSE'] == float('inf')
        assert ALLOWANCES['PARTNER'] == float('inf')
    
    def test_disability_allowance_2025(self):
        """Abattement handicap = 159 325€ (Art. 779-II CGI)."""
        from succession_engine.constants import DISABILITY_ALLOWANCE
        assert DISABILITY_ALLOWANCE == 159_325.0
    
    def test_reserve_one_child(self):
        """Réserve 1 enfant = 1/2 (Art. 913 CC)."""
        from succession_engine.constants import RESERVE_CHILDREN
        assert RESERVE_CHILDREN[1] == 0.5
    
    def test_reserve_two_children(self):
        """Réserve 2 enfants = 2/3 (Art. 913 CC)."""
        from succession_engine.constants import RESERVE_CHILDREN
        assert RESERVE_CHILDREN[2] == pytest.approx(2/3, rel=0.001)
    
    def test_reserve_three_children(self):
        """Réserve 3+ enfants = 3/4 (Art. 913 CC)."""
        from succession_engine.constants import RESERVE_CHILDREN
        assert RESERVE_CHILDREN[3] == 0.75
    
    def test_life_insurance_before_70(self):
        """AV avant 70 ans = 152 500€/bénéficiaire (Art. 990 I CGI)."""
        from succession_engine.constants import LIFE_INSURANCE_ALLOWANCE_BEFORE_70
        assert LIFE_INSURANCE_ALLOWANCE_BEFORE_70 == 152_500.0
    
    def test_life_insurance_after_70(self):
        """AV après 70 ans = 30 500€ global (Art. 757 B CGI)."""
        from succession_engine.constants import LIFE_INSURANCE_ALLOWANCE_AFTER_70
        assert LIFE_INSURANCE_ALLOWANCE_AFTER_70 == 30_500.0
    
    def test_dutreil_exemption_rate(self):
        """Pacte Dutreil = 75% exonération (Art. 787 B CGI)."""
        from succession_engine.constants import DUTREIL_EXEMPTION_RATE
        assert DUTREIL_EXEMPTION_RATE == 0.75
    
    def test_funeral_deduction_cap(self):
        """Forfait funéraire = 1 500€ max (Art. 775 CGI)."""
        from succession_engine.constants import MAX_FUNERAL_DEDUCTION
        assert MAX_FUNERAL_DEDUCTION == 1_500.0
