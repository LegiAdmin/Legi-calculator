
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
    HeirRelation, AssetOrigin, OwnershipMode, ProfessionalExemption, ExemptionType,
    TaxCalculationDetail
)
from succession_engine.core.calculator import SuccessionCalculator

print('=== Phase 10 Verification: SCI & Comptes Courants ===')

# Mock FiscalCalculator.calculate_inheritance_tax to avoid DB hits
patcher = patch('succession_engine.rules.fiscal.FiscalCalculator.calculate_inheritance_tax')
mock_calc_tax = patcher.start()

# Helper to verify input value passed to calculate_inheritance_tax
def side_effect(taxable_amount, *args, **kwargs):
    print(f"  -> Called tax calc with taxable_amount: {taxable_amount}€")
    return (0.0, TaxCalculationDetail(
        relationship="ENFANT",
        gross_amount=taxable_amount,
        allowance_name="Mock",
        allowance_amount=0.0,
        net_taxable=taxable_amount,
        brackets_applied=[],
        total_tax=0.0
    ))

mock_calc_tax.side_effect = side_effect

calc = SuccessionCalculator()

# Setup Scenario
heir = FamilyMember(id='h1', birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD)

# Asset: SCI Shares (100k) + CCA (50k) = 150k Total
# Dutreil active (75% exemption on shares only)
asset = Asset(
    id='sci_parts', 
    estimated_value=100_000, 
    cca_value=50_000,
    asset_origin=AssetOrigin.PERSONAL_PROPERTY, 
    ownership_mode=OwnershipMode.FULL_OWNERSHIP,
    professional_exemption=ProfessionalExemption(
        exemption_type=ExemptionType.DUTREIL,
        dutreil_is_collective=True,
        dutreil_is_individual=True
    )
)

input_data = SimulationInput(
    members=[heir],
    assets=[asset],
    debts=[],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)

print('\n[Test 1] Dutreil Exemption with CCA')
result = calc.run(input_data)

# Verification Logic
# Total Civil Value = 100k + 50k = 150k
# Exemption = 100k * 0.75 = 75k
# Taxable Base = 150k - 75k = 75k

# Check calculation steps summary
step_4 = next(s for s in result.calculation_steps if s.step_number == 4)
print("Step 4 Summary:", step_4.result_summary)

# Assertions
assert "75,000.00€" in step_4.result_summary, "Exemption amount not correctly displayed in summary"
# We check the arguments passed to the mock
# The mock is called once for the only heir
# call_args[0][0] is the first positional arg: taxable_amount
args, _ = mock_calc_tax.call_args
taxable_passed = args[0]

print(f"Taxable Amount Passed: {taxable_passed}€ (Expected: 75,000€)")
assert abs(taxable_passed - 75_000.0) < 0.01, f"Expected 75000, got {taxable_passed}"

print("✅ Test 1 Passed")

# Test 2: Without Dutreil (Standard)
print('\n[Test 2] No Exemption (Regression Check)')
asset_no_dutreil = Asset(
    id='sci_parts_no_dutreil', 
    estimated_value=100_000, 
    cca_value=50_000,
    asset_origin=AssetOrigin.PERSONAL_PROPERTY, 
    ownership_mode=OwnershipMode.FULL_OWNERSHIP
)
input_data_2 = SimulationInput(
    members=[heir],
    assets=[asset_no_dutreil],
    debts=[],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
calc.run(input_data_2)
args, _ = mock_calc_tax.call_args
taxable_passed_2 = args[0]
print(f"Taxable Amount Passed: {taxable_passed_2}€ (Expected: 150,000€)")
assert abs(taxable_passed_2 - 150_000.0) < 0.01, f"Expected 150000, got {taxable_passed_2}"
print("✅ Test 2 Passed")

print("\n🎉 Phase 10 Verification Successful!")
