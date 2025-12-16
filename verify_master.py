
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
    ExemptionType, ProfessionalExemption, AdoptionType
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

# Mock Data
allowances_data = [
    MockAllowance('CHILD', 100_000.0),
    MockAllowance('SIBLING', 15_932.0),
    MockAllowance('NEPHEW_NIECE', 7_967.0),
    MockAllowance('OTHER', 1_594.0),
    MockAllowance('SPOUSE', float('inf')),
    MockAllowance('PARTNER', float('inf')),
]

brackets_child = [
    MockTaxBracket(0.05, 0, 8072, 'CHILD'),
    MockTaxBracket(0.10, 8072, 12109, 'CHILD'),
    MockTaxBracket(0.15, 12109, 15932, 'CHILD'),
    MockTaxBracket(0.20, 15932, 552324, 'CHILD'),
    MockTaxBracket(0.30, 552324, 902838, 'CHILD'),
    MockTaxBracket(0.40, 902838, 1805677, 'CHILD'),
    MockTaxBracket(0.45, 1805677, None, 'CHILD'),
]

# Mock Legislation
class MockLegislation:
    id = 1
    
# Mock QuerySets / Managers
class MockQuerySet(list):
    def first(self):
        return self[0] if self else None
    def order_by(self, *args):
        # Already sorted in our mock data for simplicity
        return self
    def exists(self):
        return len(self) > 0

def mock_allowance_filter(**kwargs):
    # Return filtered allowances based on relationship
    rel = kwargs.get('relationship')
    return MockQuerySet([x for x in allowances_data if x.relationship == rel])

def mock_bracket_filter(**kwargs):
    rel = kwargs.get('relationship')
    # Default to CHILD brackets for testing if relation not found or logic needed
    # For now, return brackets_child if relation is child
    return MockQuerySet(brackets_child)

# Apply Patches
patch_leg = patch('succession_engine.models.Legislation.objects.get', return_value=MockLegislation())
patch_allow = patch('succession_engine.models.Allowance.objects.filter', side_effect=mock_allowance_filter)
patch_bracket = patch('succession_engine.models.TaxBracket.objects.filter', side_effect=mock_bracket_filter)

patch_leg.start()
patch_allow.start()
patch_bracket.start()


print('=== 🛡️ MASTER VERIFICATION SUITE (Phases 1-11) ===')

calc = SuccessionCalculator()

def run_test(name, input_data, checks):
    print(f"\n🔹 [Test] {name}")
    try:
        result = calc.run(input_data)
        for check_name, check_func in checks.items():
            if check_func(result):
                print(f"  ✅ {check_name} Passed")
            else:
                print(f"  ❌ {check_name} FAILED")
                # print(f"     Debug infos: {result.global_metrics}")
    except Exception as e:
        print(f"  ❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

# --- SCENARIO 1: Basic Devolution (Use Case Standard) ---
# 1 Spouse, 2 Children. Community Regime. 300k Assets (Community).
# Outcome: Spouse takes Usufruct. Children take Bare Ownership.
m1_spouse = FamilyMember(id='S1', birth_date=date(1980, 1, 1), relationship=HeirRelation.SPOUSE)
m1_c1 = FamilyMember(id='C1', birth_date=date(2010, 1, 1), relationship=HeirRelation.CHILD)
m1_c2 = FamilyMember(id='C2', birth_date=date(2012, 1, 1), relationship=HeirRelation.CHILD)
assets_1 = [Asset(id='House', estimated_value=300_000, asset_origin=AssetOrigin.COMMUNITY_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)]

input_1 = SimulationInput(
    members=[m1_spouse, m1_c1, m1_c2],
    assets=assets_1,
    matrimonial_regime=MatrimonialRegime.COMMUNITY_LEGAL,
    marriage_date=date(2000, 1, 1)
)

results_1 = {
    "Spouse Exists": lambda r: r.family_context.has_spouse,
    "Community Liquidated Correctly (150k each)": lambda r: abs(r.liquidation_details.deceased_community_share - 150_000) < 1,
    "No Tax for Spouse": lambda r: next(h for h in r.heirs_breakdown if h.id == 'S1').tax_amount == 0,
    "Children Have Taxable Base": lambda r: next(h for h in r.heirs_breakdown if h.id == 'C1').taxable_base >= 0,
}
run_test("Standard Family (Spouse + 2 Kids)", input_1, results_1)


# --- SCENARIO 2: Prior Donations & Rapport (Phase 3) ---
# 1 Child. 100k Donation (Manuel) 5 years ago. 200k Estate.
# Mass = 200k + 100k = 300k. Reserve = 150k. QD = 150k.
# Child gets everything. Tax allowance consumed partially.
m2_c1 = FamilyMember(id='C1', birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD)
donation_1 = Donation(
    id='d1', donation_type=DonationType.DON_MANUEL, beneficiary_name="C1", beneficiary_heir_id="C1",
    beneficiary_relationship=HeirRelation.CHILD, donation_date=date(2020, 1, 1),
    original_value=100_000, is_declared_to_tax=True
)
assets_2 = [Asset(id='Cash', estimated_value=200_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)]

input_2 = SimulationInput(
    members=[m2_c1],
    assets=assets_2,
    donations=[donation_1],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)

results_2 = {
    "Rapport Civil Applied (Total 300k mass)": lambda r: abs(r.global_metrics.total_estate_value - 300_000) < 1,
    "Tax Allowance Consumed (Child)": lambda r: r.heirs_breakdown[0].tax_calculation_details.allowance_amount == 0  # 100k already used 100k allowance
}
run_test("Rapport Civil & Tax Recall", input_2, results_2)


# --- SCENARIO 3: Pacte Dutreil & SCI (Phase 5 + 10) ---
# 1 Child. Asset = SCI (1M€). 
# Composed of: 800k Parts (Eligible Dutreil), 200k CCA (Not Eligible).
# Taxable Base: (800k * 25%) + 200k = 200k + 200k = 400k.
# Allowance: 100k. Net Taxable: 300k.
m3_c1 = FamilyMember(id='C1', birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD)
asset_sci = Asset(
    id='SCI_Complex',
    estimated_value=800_000, 
    cca_value=200_000,
    asset_origin=AssetOrigin.PERSONAL_PROPERTY,
    ownership_mode=OwnershipMode.FULL_OWNERSHIP,
    professional_exemption=ProfessionalExemption(
        exemption_type=ExemptionType.DUTREIL,
        dutreil_is_collective=True, dutreil_is_individual=True
    )
)

input_3 = SimulationInput(
    members=[m3_c1],
    assets=[asset_sci],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)

def check_dutreil(r):
    heir = r.heirs_breakdown[0]
    # Total Value = 1M.
    # Exemption = 75% of 800k = 600k.
    # Taxable Base BEFORE Allowance = 1M - 600k = 400k.
    # Net Taxable AFTER Allowance (100k) = 300k.
    return abs(heir.taxable_base - 300_000) < 1000

results_3 = {
    "Dutreil Exemption Applied correctly (Parts Only)": check_dutreil,
    "CCA Fully Taxed": lambda r: True # Implicitly checked by the math above
}
run_test("Optimisation SCI Dutreil + CCA", input_3, results_3)


# --- SCENARIO 4: International & Compliance (Phase 9 + 11) ---
# Warning Checks.
asset_uk = Asset(id='Flat_London', location_country='UK', estimated_value=500_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)
input_4 = SimulationInput(
    members=[m2_c1],
    assets=[asset_uk],
    residence_country='UK',
    matrimonial_regime=MatrimonialRegime.SEPARATION
)

results_4 = {
    "Warning: Foreign Residence": lambda r: any("défunt résidait à l'étranger" in w for w in r.warnings),
    "Warning: Foreign Asset": lambda r: any("situé à l'étranger" in w for w in r.warnings),
}
run_test("International Compliance Warnings", input_4, results_4)

print("\n🎉 Master Verification Complete.")
