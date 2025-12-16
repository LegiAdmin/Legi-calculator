
import os
import django
from django.conf import settings
from datetime import date
from unittest.mock import MagicMock, patch

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=['succession_engine'],
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    )
    django.setup()

from succession_engine.schemas import (
    SimulationInput, FamilyMember, Asset, Debt, MatrimonialRegime, 
    HeirRelation, AssetOrigin, OwnershipMode, Donation, DonationType,
    ExemptionType, ProfessionalExemption, AdoptionType, LifeInsuranceContractType,
    Wishes, SpouseChoice, SpouseChoiceType, SpecificBequest, MatrimonialAdvantages, PreciputType
)
from succession_engine.core.calculator import SuccessionCalculator

# --------------------------------------------------------------------------------
# MOCKING DATABASE FOR FISCAL CALCULATOR
# --------------------------------------------------------------------------------
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MockTaxBracket:
    rate: float
    min_amount: float
    max_amount: Optional[float]
    relationship: str

@dataclass
class MockAllowance:
    relationship: str
    amount: float

# Mock Data (Barème 2024 simplifié)
allowances_data = [
    MockAllowance('CHILD', 100_000.0), # Enfants & Parents
    MockAllowance('SIBLING', 15_932.0),
    MockAllowance('NEPHEW_NIECE', 7_967.0), 
    MockAllowance('GrandParent', 1_594.0), # Défaut si pas spécifique
    MockAllowance('OTHER', 1_594.0),
    MockAllowance('SPOUSE', float('inf')),
    MockAllowance('PARTNER', float('inf')),
]

buckets_direct = [ # Ligne Directe (Enfants, Parents avec 100k abattement)
    MockTaxBracket(0.05, 0, 8072, 'CHILD'),
    MockTaxBracket(0.10, 8072, 12109, 'CHILD'),
    MockTaxBracket(0.15, 12109, 15932, 'CHILD'),
    MockTaxBracket(0.20, 15932, 552324, 'CHILD'),
    MockTaxBracket(0.30, 552324, 902838, 'CHILD'),
    MockTaxBracket(0.40, 902838, 1805677, 'CHILD'),
    MockTaxBracket(0.45, 1805677, None, 'CHILD'),
]

buckets_sibling = [ # Frères/Soeurs (Abattement 15932)
    MockTaxBracket(0.35, 0, 24430, 'SIBLING'),
    MockTaxBracket(0.45, 24430, None, 'SIBLING'),
]

buckets_other = [ # Autres (Oncles, Tantes, Cousins, Concubins, Adoption Simple sans soins)
    MockTaxBracket(0.60, 0, None, 'OTHER'),
]

buckets_nephew = [ # Neveux/Nièces (55%)
    MockTaxBracket(0.55, 0, None, 'NEPHEW_NIECE'),
]


# Mock Legislation
class MockLegislation:
    id = 1
    
# Mock QuerySets / Managers
class MockQuerySet(list):
    def first(self):
        return self[0] if self else None
    def order_by(self, *args):
        return self
    def exists(self):
        return len(self) > 0

def mock_allowance_filter(**kwargs):
    # Return filtered allowances based on relationship
    rel = kwargs.get('relationship')
    return MockQuerySet([x for x in allowances_data if x.relationship == rel])

def mock_bracket_filter(**kwargs):
    rel = kwargs.get('relationship')
    if rel == 'CHILD': return MockQuerySet(buckets_direct)
    if rel == 'SIBLING': return MockQuerySet(buckets_sibling)
    if rel == 'NEPHEW_NIECE': return MockQuerySet(buckets_nephew)
    return MockQuerySet(buckets_other) # Fallback

# Apply Patches
patch_leg = patch('succession_engine.models.Legislation.objects.get', return_value=MockLegislation())
patch_allow = patch('succession_engine.models.Allowance.objects.filter', side_effect=mock_allowance_filter)
patch_bracket = patch('succession_engine.models.TaxBracket.objects.filter', side_effect=mock_bracket_filter)

patch_leg.start()
patch_allow.start()
patch_bracket.start()


print('=== 🛡️ GOD MODE VERIFICATION SUITE (14 Scenarios) ===')

calc = SuccessionCalculator()

def run_test(name, input_data, checks):
    print(f"\n🔹 [Test] {name}")
    try:
        result = calc.run(input_data)
        all_passed = True
        for check_name, check_func in checks.items():
            if check_func(result):
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name} FAILED")
                all_passed = False
                # print(f"     DEBUG: {result.heirs_breakdown}")
        if not all_passed:
            pass # print(f"     Global Metrics: {result.global_metrics}")
    except Exception as e:
        print(f"  ❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

# -------------------------------------------------------------------------
# SCENARIO 1: Basic Devolution (Standard)
# -------------------------------------------------------------------------
m1_spouse = FamilyMember(id='S1', birth_date=date(1980, 1, 1), relationship=HeirRelation.SPOUSE)
m1_c1 = FamilyMember(id='C1', birth_date=date(2010, 1, 1), relationship=HeirRelation.CHILD)
assets_1 = [Asset(id='House', estimated_value=300_000, asset_origin=AssetOrigin.COMMUNITY_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)]
input_1 = SimulationInput(
    members=[m1_spouse, m1_c1], 
    assets=assets_1, 
    matrimonial_regime=MatrimonialRegime.COMMUNITY_LEGAL, 
    marriage_date=date(2000, 1, 1),
    wishes=Wishes(spouse_choice=SpouseChoice(choice=SpouseChoiceType.USUFRUCT))
)
run_test("Scenario 1: Standard Spouse + Child", input_1, {
    "Spouse Usufruct Option by default": lambda r: r.spouse_details and r.spouse_details.has_usufruct,
})

# -------------------------------------------------------------------------
# SCENARIO 2: Rapport Civil
# -------------------------------------------------------------------------
input_2 = SimulationInput(
    members=[FamilyMember(id='C1', birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD)],
    assets=[Asset(id='Cash', estimated_value=200_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)],
    donations=[Donation(id='d1', donation_type=DonationType.DON_MANUEL, beneficiary_name="C1", beneficiary_heir_id="C1", beneficiary_relationship=HeirRelation.CHILD, donation_date=date(2020, 1, 1), original_value=100_000, is_declared_to_tax=True)],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
run_test("Scenario 2: Rapport Civil", input_2, {
    "Total Mass = 300k": lambda r: abs(r.global_metrics.total_estate_value - 300_000) < 1,
    "Allowance Consumed": lambda r: r.heirs_breakdown[0].abatement_used == 0 # 100k used by donation
})

# -------------------------------------------------------------------------
# SCENARIO 3: Pacte Dutreil
# -------------------------------------------------------------------------
m3_c1 = FamilyMember(id='C1', birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD)
asset_sci = Asset(id='SCI', estimated_value=1_000_000, cca_value=0, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP, professional_exemption=ProfessionalExemption(exemption_type=ExemptionType.DUTREIL, dutreil_is_collective=True, dutreil_is_individual=True))
input_3 = SimulationInput(members=[m3_c1], assets=[asset_sci], matrimonial_regime=MatrimonialRegime.SEPARATION)
# Taxable: 250k. Allowance 100k. Net 150k. Tax ~28k.
run_test("Scenario 3: Pacte Dutreil (75% ex)", input_3, {
    "Taxable Base correct (~250k)": lambda r: abs(r.heirs_breakdown[0].taxable_base - 150_000) < 1000 # 250k - 100k allowance
})

# -------------------------------------------------------------------------
# SCENARIO 4: Deceased UK Resident (International)
# -------------------------------------------------------------------------
input_4 = SimulationInput(members=[m3_c1], assets=[asset_sci], residence_country='UK', matrimonial_regime=MatrimonialRegime.SEPARATION)
run_test("Scenario 4: International Warning", input_4, {
    "Has Warning": lambda r: "défunt résidait à l'étranger" in str(r.warnings)
})

# -------------------------------------------------------------------------
# SCENARIO 5: Assurance Vie
# -------------------------------------------------------------------------
assets_5 = [Asset(id="av1", estimated_value=0, premiums_before_70=50_000, life_insurance_contract_type=LifeInsuranceContractType.STANDARD, ownership_mode=OwnershipMode.FULL_OWNERSHIP, asset_origin=AssetOrigin.PERSONAL_PROPERTY)]
input_5 = SimulationInput(members=[m3_c1], assets=assets_5, matrimonial_regime=MatrimonialRegime.SEPARATION)
run_test("Scenario 5: Assurance Vie (Exempt under 152k)", input_5, {
    "No Tax on AV": lambda r: "Droits: 0.00€" in str(r.calculation_steps)
})

# -------------------------------------------------------------------------
# SCENARIO 6: Pro-rata Debt
# -------------------------------------------------------------------------
input_6 = SimulationInput(
    members=[m3_c1], 
    assets=[asset_sci], # 1M Dutreil
    debts=[Debt(id="D1", amount=100_000, is_deductible=True, linked_asset_id="SCI", debt_type="LOAN", asset_origin=AssetOrigin.PERSONAL_PROPERTY)],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
# Debt 100k -> 25% deductible = 25k. 
# Taxable (Parts) = 250k. Net Succession = 250k - 25k = 225k.
# WARNING: Current logic deducts debt from mass, THEN applies Dutreil? 
# NO, Dutreil applies to ASSET value. Estate Mass = Sum(Assets) - Debts.
# Calculator.py: total_professional_exemption calculated on assets.
# Taxable Base = Net Assets - Exemption.
# Net Assets = 1M - 25k = 975k.
# Exemption = 750k.
# Taxable = 975 - 750 = 225k. Correct.
run_test("Scenario 6: Pro-rata Debt", input_6, {
    "Warning Exists": lambda r: "plafonnée à 25%" in str(r.warnings)
})

# -------------------------------------------------------------------------
# SCENARIO 7: Adoption (Simple vs Plénière vs Care)
# -------------------------------------------------------------------------
# 3 kids. 1 Bio, 1 Simple (No Care), 1 Simple (With Care).
# Estate: 900k.
bio = FamilyMember(id='m_bio', birth_date=date(2000,1,1), relationship=HeirRelation.CHILD)
simple_no_care = FamilyMember(id='m_simple_nocare', birth_date=date(2000,1,1), relationship=HeirRelation.CHILD, adoption_type=AdoptionType.SIMPLE, has_received_continuous_care=False)
simple_care = FamilyMember(id='m_simple_care', birth_date=date(2000,1,1), relationship=HeirRelation.CHILD, adoption_type=AdoptionType.SIMPLE, has_received_continuous_care=True)
assets_7 = [Asset(id='Cash7', estimated_value=900_000+300_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)] # 1.2M -> 400k each
input_7 = SimulationInput(members=[bio, simple_no_care, simple_care], assets=assets_7, matrimonial_regime=MatrimonialRegime.SEPARATION)

def check_adoption(r):
    hb = {h.id: h for h in r.heirs_breakdown}
    bio_tax = hb['m_bio'].tax_amount
    care_tax = hb['m_simple_care'].tax_amount
    nocare_tax = hb['m_simple_nocare'].tax_amount
    
    # Bio and Care should have same tax (Child scale)
    # NoCare should have 60% tax (after 1.5k allowance) -> ~240k tax
    return (abs(bio_tax - care_tax) < 1) and (nocare_tax > bio_tax * 3)

run_test("Scenario 7: Adoption Types", input_7, {
    "Tax Differentiation Correct": check_adoption
})

# -------------------------------------------------------------------------
# SCENARIO 8: Représentation (Petits-enfants)
# -------------------------------------------------------------------------
# Child 1 (Alive). Child 2 (Dead) -> GC1, GC2. 
# Estate 300k.
# C1 gets 150k. GC1 gets 75k. GC2 gets 75k.
c1 = FamilyMember(id='C1', birth_date=date(1980,1,1), relationship=HeirRelation.CHILD)
gc1 = FamilyMember(id='GC1', birth_date=date(2010,1,1), relationship=HeirRelation.GRANDCHILD, represented_heir_id='C2_Dead')
gc2 = FamilyMember(id='GC2', birth_date=date(2012,1,1), relationship=HeirRelation.GRANDCHILD, represented_heir_id='C2_Dead')
# C2_Dead doesn't exist in members list, implied by representation logic?
# Wait, represented_heir_id MUST point to a valid ID in our logic?
# Logic: 'represented_heir_id' creates a souche bucket. We don't need the dead heir object if representation logic handles it.
assets_8 = [Asset(id='Cash8', estimated_value=300_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)]
input_8 = SimulationInput(members=[c1, gc1, gc2], assets=assets_8, matrimonial_regime=MatrimonialRegime.SEPARATION)

run_test("Scenario 8: Représentation", input_8, {
    "C1 Share 50%": lambda r: abs(next(h for h in r.heirs_breakdown if h.id=='C1').legal_share_percent - 50.0) < 0.1,
    "GC1 Share 25%": lambda r: abs(next(h for h in r.heirs_breakdown if h.id=='GC1').legal_share_percent - 25.0) < 0.1,
    "Abattement Shared (50k each for GC)": lambda r: next(h for h in r.heirs_breakdown if h.id=='GC1').abatement_used <= 50000 
    # Logic note: Abattement applies per Souche? Art 779 I: "Les enfants... ou les représentants... 100k".
    # In representation, the 100k is SPLIT between representatives. 
    # Current engine: FiscalCalculator uses 'CHILD' allowance for 'GRANDCHILD'?? 
    # Need to check fiscal rules map in engine. 
    # Actually fiscal.py maps relations. Does it handle split allowance?
    # Art 779-I: "abattement de 100 000 €... applicable aux ascendants et enfants vivants ou représentés".
    # Engine Check: Does `FiscalCalculator` split allowance? 
    # Probably not implemented yet. Let's see if test fails.
})

# -------------------------------------------------------------------------
# SCENARIO 9: Fente Successorale + SCENARIO 9b: Parents + Siblings
# -------------------------------------------------------------------------
# 9a: Parents (Père) + Siblings. Art 738.
father = FamilyMember(id='Father', birth_date=date(1950,1,1), relationship=HeirRelation.PARENT, paternal_line=True)
sibling = FamilyMember(id='Sibling', birth_date=date(1980,1,1), relationship=HeirRelation.SIBLING, paternal_line=True) # Line shouldn't matter for Art 738
assets_9 = [Asset(id='Cash9', estimated_value=100_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)]
input_9a = SimulationInput(members=[father, sibling], assets=assets_9, matrimonial_regime=MatrimonialRegime.SEPARATION)

run_test("Scenario 9a: Parents + Siblings (Art 738 Check)", input_9a, {
    "Father gets 25%": lambda r: abs(next(h for h in r.heirs_breakdown if h.id=='Father').legal_share_percent - 25.0) < 0.1,
    "Sibling gets 75%": lambda r: abs(next(h for h in r.heirs_breakdown if h.id=='Sibling').legal_share_percent - 75.0) < 0.1,
})

# 9b: Fente (No Parents, No Siblings, Only Uncles/Cousins)
uncle_pat = FamilyMember(id='UncleP', birth_date=date(1960,1,1), relationship=HeirRelation.OTHER, paternal_line=True) # OTHER or UNCLE? Using OTHER as relation generic
# Need to use OTHER but logic filters 'other_heirs'.
# Let's say Cousins.
cousin_mat = FamilyMember(id='CousinM', birth_date=date(1990,1,1), relationship=HeirRelation.OTHER, paternal_line=False)
input_9b = SimulationInput(members=[uncle_pat, cousin_mat], assets=assets_9, matrimonial_regime=MatrimonialRegime.SEPARATION)
run_test("Scenario 9b: Fente Pure (50/50)", input_9b, {
    "Paternal Line 50%": lambda r: abs(next(h for h in r.heirs_breakdown if h.id=='UncleP').legal_share_percent - 50.0) < 0.1,
    "Maternal Line 50%": lambda r: abs(next(h for h in r.heirs_breakdown if h.id=='CousinM').legal_share_percent - 50.0) < 0.1,
})

# -------------------------------------------------------------------------
# SCENARIO 10: Avantages Matrimoniaux (Préciput)
# -------------------------------------------------------------------------
# Community House 200k. Personal Cash 100k.
# Preciput on Main Residence (House).
# Spouse takes House (200k) BEFORE partition.
# Remaining Community: 0. Remaining Personal: 100k.
# Succession Mass: 0 (Community) + 100k (Personal) = 100k.
input_10 = SimulationInput(
    members=[m1_spouse, m1_c1], # Spouse + 1 Child
    assets=[
        Asset(id='HouseCom', estimated_value=200_000, asset_origin=AssetOrigin.COMMUNITY_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP, is_main_residence=True),
        Asset(id='CashPerso', estimated_value=100_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)
    ],
    matrimonial_regime=MatrimonialRegime.COMMUNITY_LEGAL,
    matrimonial_advantages=MatrimonialAdvantages(
        has_preciput=True,
        preciput_assets=[PreciputType.RESIDENCE_PRINCIPALE]
    )
)

run_test("Scenario 10: Préciput", input_10, {
    "Preciput Value Detected (200k)": lambda r: r.liquidation_details.preciput_value == 200_000,
    "Mass Reduced Correctly": lambda r: abs(r.global_metrics.total_estate_value - 100_000) < 1 
    # Community (200k) -> Half (100k) normally in succession.
    # Preciput (200k) taken. Deceased share (-100k).
    # Remaining Succession: Personal (100k). Total 100k.
})


# -------------------------------------------------------------------------
# SCENARIO 11: Droit de Retour Légal
# -------------------------------------------------------------------------
# No Descendants. Father alive. Asset received from Father.
father_11 = FamilyMember(id='Father11', birth_date=date(1950, 1, 1), relationship=HeirRelation.PARENT)
asset_gift = Asset(id='GiftLand', estimated_value=100_000, received_from_parent_id='Father11', asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)
asset_other = Asset(id='Other', estimated_value=300_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)
input_11 = SimulationInput(members=[father_11], assets=[asset_gift, asset_other], matrimonial_regime=MatrimonialRegime.SEPARATION)
# Return limited to 1/4 of estate? Estate = 400k. 1/4 = 100k.
# Asset is 100k. Return = 100k.
run_test("Scenario 11: Droit de Retour", input_11, {
    "Right of Return applied": lambda r: "Droit de retour" in str(r.warnings) or any("retourne au parent" in w for w in r.warnings)
})

# -------------------------------------------------------------------------
# SCENARIO 12: Abattement Résidence Principale
# -------------------------------------------------------------------------
spouse_occupying = Asset(id='MainRes', estimated_value=500_000, is_main_residence=True, spouse_occupies_property=True, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)
input_12 = SimulationInput(members=[m1_spouse], assets=[spouse_occupying], matrimonial_regime=MatrimonialRegime.SEPARATION)
run_test("Scenario 12: Abattement 20% RP", input_12, {
    "Value Reduced": lambda r: "abattement 20%" in str(r.liquidation_details.details)
})

# -------------------------------------------------------------------------
# SCENARIO 13: Mix Assurance Vie
# -------------------------------------------------------------------------
av_mix = [
    Asset(id="AV_Gen", estimated_value=0, premiums_before_70=100_000, life_insurance_contract_type=LifeInsuranceContractType.VIE_GENERATION, ownership_mode=OwnershipMode.FULL_OWNERSHIP, asset_origin=AssetOrigin.PERSONAL_PROPERTY),
    Asset(id="AV_Old", estimated_value=0, premiums_before_70=500_000, life_insurance_contract_type=LifeInsuranceContractType.ANCIEN_CONTRAT, ownership_mode=OwnershipMode.FULL_OWNERSHIP, asset_origin=AssetOrigin.PERSONAL_PROPERTY)
]
input_13 = SimulationInput(members=[m3_c1], assets=av_mix, matrimonial_regime=MatrimonialRegime.SEPARATION)
run_test("Scenario 13: Mix Assurance Vie", input_13, {
    "Ancien Free": lambda r: "Exonérée" in str(r.warnings),
    "Vie Gen Taxed (with 20% off base)": lambda r: "VIE_GENERATION" in str(r.warnings)
})

# -------------------------------------------------------------------------
# SCENARIO 14: Dettes Mixtes
# -------------------------------------------------------------------------
# Already covered in Scenario 6 partially but ensuring mixed debts
input_14 = SimulationInput(
    members=[m3_c1],
    assets=[asset_sci, Asset(id="Pool", estimated_value=50_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)],
    debts=[
        Debt(id="D_Dutreil", amount=100_000, is_deductible=True, linked_asset_id="SCI", debt_type="LOAN", asset_origin=AssetOrigin.PERSONAL_PROPERTY),
        Debt(id="D_Normal", amount=10_000, is_deductible=True, debt_type="TAX", asset_origin=AssetOrigin.PERSONAL_PROPERTY)
    ],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
run_test("Scenario 14: Dettes Mixtes", input_14, {
    "Total Deductible (25k + 10k = 35k)": lambda r: abs(r.global_metrics.total_estate_value - (1_050_000 - 35_000)) < 1
})
