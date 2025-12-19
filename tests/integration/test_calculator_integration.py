
import pytest
from datetime import date
from succession_engine.core.calculator import SuccessionCalculator
from succession_engine.schemas import (
    SimulationInput, FamilyMember, Asset, Donation, Wishes,
    HeirRelation, SpouseChoice, SpouseChoiceType, 
    AssetOrigin, OwnershipMode, SpecificBequest,
    MatrimonialRegime
)

@pytest.mark.django_db
class TestCalculatorIntegration:
    """
    Tests d'intégration pour le calculateur de succession.
    Vérifie le flux complet de calculate_succession() avec des objets Python.
    """
    
    @pytest.fixture
    def calculator(self):
        return SuccessionCalculator()

    def test_simple_succession_one_child(self, calculator):
        """Cas simple : 1 enfant, 1 bien propre."""
        assets = [
            Asset(
                id="maison",
                estimated_value=200000,
                ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                asset_origin=AssetOrigin.PERSONAL_PROPERTY
            )
        ]
        members = [
            FamilyMember(id="enfant1", relationship=HeirRelation.CHILD, birth_date=date(1990, 1, 1))
        ]
        input_data = SimulationInput(assets=assets, members=members, matrimonial_regime="SEPARATION")
        
        result = calculator.run(input_data)
        
        assert len(result.heirs_breakdown) == 1
        heir = result.heirs_breakdown[0]
        assert heir.id == "enfant1"
        assert heir.legal_share_percent == 100.0
        assert heir.gross_share_value == 200000.0
        # Abattement 100k -> Taxable 100k -> Droits ~18k
        assert heir.taxable_base == 100000.0
        assert heir.tax_amount > 0

    def test_spouse_usufruct_option(self, calculator):
        """Cas conjoint : Option Usufruit (avec enfants communs)."""
        assets = [
            Asset(id="cash", estimated_value=100000, ownership_mode=OwnershipMode.FULL_OWNERSHIP, asset_origin=AssetOrigin.PERSONAL_PROPERTY)
        ]
        spouse = FamilyMember(id="conjoint", relationship=HeirRelation.SPOUSE, birth_date=date(1960, 1, 1)) # 65 ans -> 40% usufruit
        child = FamilyMember(id="enfant", relationship=HeirRelation.CHILD, birth_date=date(1990, 1, 1), is_from_current_union=True)
        
        wishes = Wishes(
            spouse_choice=SpouseChoice(choice=SpouseChoiceType.USUFRUCT)
        )
        
        input_data = SimulationInput(
            assets=assets,
            members=[spouse, child],
            matrimonial_regime="SEPARATION",
            wishes=wishes
        )
        
        result = calculator.run(input_data)
        
        spouse_res = next(h for h in result.heirs_breakdown if h.id == "conjoint")
        child_res = next(h for h in result.heirs_breakdown if h.id == "enfant")
        
        # Conjoint a 0 en PP mais a l'usufruit
        assert spouse_res.legal_share_percent == 0.0 # Part en PP
        assert result.spouse_details.has_usufruct is True
        assert result.spouse_details.choice_made == "USUFRUCT"
        # Usufruit 65 ans = 40%
        assert result.spouse_details.usufruct_rate == 0.40
        assert result.spouse_details.usufruct_value == 40000.0
        
        # Enfant a 100% en NP
        assert child_res.legal_share_percent == 100.0
        assert child_res.gross_share_value == 60000.0 # 100k - 40k usufruit

    def test_fiscal_recall_donations(self, calculator):
        """Rappel fiscal : Donation < 15 ans."""
        assets = [
            Asset(id="cash", estimated_value=200000, ownership_mode=OwnershipMode.FULL_OWNERSHIP, asset_origin=AssetOrigin.PERSONAL_PROPERTY)
        ]
        child = FamilyMember(id="enfant", relationship=HeirRelation.CHILD, birth_date=date(1990, 1, 1))
        
        # Donation de 50k il y a 2 ans (consomme abattement)
        donations = [
            Donation(
                id="don1",
                user_id="user1", # Dummy UUID
                donation_type="don_manuel",
                beneficiary_name="Enfant",
                beneficiary_heir_id="enfant",
                beneficiary_relationship=HeirRelation.CHILD,
                donation_date=date.today().replace(year=date.today().year - 2),
                description="Don cash",
                original_value=50000,
                is_declared_to_tax=True,
                current_estimated_value=50000
            )
        ]
        
        input_data = SimulationInput(assets=assets, members=[child], donations=donations, matrimonial_regime="SEPARATION")
        result = calculator.run(input_data)
        
        heir = result.heirs_breakdown[0]
        # Abattement total 100k. Déjà utilisé 50k. Reste 50k.
        # Taxable = 200k - 50k = 150k.
        assert heir.abatement_used == 50000.0
        assert heir.taxable_base == 150000.0

    def test_renunciation_rescrewing(self, calculator):
        """Renonciation d'un héritier (part redistribuée)."""
        assets = [
            Asset(id="maison", estimated_value=300000, ownership_mode=OwnershipMode.FULL_OWNERSHIP, asset_origin=AssetOrigin.PERSONAL_PROPERTY)
        ]
        # 3 enfants, dont 1 renonçant
        c1 = FamilyMember(id="c1", relationship=HeirRelation.CHILD, birth_date=date(1990, 1, 1))
        c2 = FamilyMember(id="c2", relationship=HeirRelation.CHILD, birth_date=date(1992, 1, 1))
        c3 = FamilyMember(id="c3", relationship=HeirRelation.CHILD, birth_date=date(1994, 1, 1), acceptance_option="RENUNCIATION", has_renounced=True)
        
        input_data = SimulationInput(assets=assets, members=[c1, c2, c3], matrimonial_regime="SEPARATION")
        result = calculator.run(input_data)
        
        # c3 doit avoir 0
        h3 = next(h for h in result.heirs_breakdown if h.id == "c3")
        assert h3.legal_share_percent == 0.0
        assert h3.gross_share_value == 0.0
        
        # c1 et c2 doivent avoir 50% chacun (au lieu de 33%)
        h1 = next(h for h in result.heirs_breakdown if h.id == "c1")
        h2 = next(h for h in result.heirs_breakdown if h.id == "c2")
        
        assert h1.legal_share_percent == 50.0
        assert h2.legal_share_percent == 50.0
        assert h1.gross_share_value == 150000.0

    def test_indignity_exclusion(self, calculator):
        """Exclusion pour indignité (traitée comme renonciation)."""
        # Feature 'is_indigne' not yet implemented in schema.
        pass
