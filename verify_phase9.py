
import os
import django
from django.conf import settings
from datetime import date

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=['succession_engine'],
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    )
    django.setup()

from succession_engine.schemas import (
    SimulationInput, FamilyMember, Asset, Debt, MatrimonialRegime, 
    HeirRelation, AssetOrigin, OwnershipMode, Donation, TaxCalculationDetail
)
from succession_engine.core.calculator import SuccessionCalculator
from succession_engine.constants import MAX_FUNERAL_DEDUCTION
from unittest.mock import MagicMock, patch

print('=== Phase 9 Verification: Security & Compliance ===')

# Mock FiscalCalculator to avoid DB hits
patcher = patch('succession_engine.rules.fiscal.FiscalCalculator.calculate_inheritance_tax')
mock_calc_tax = patcher.start()

# Return dummy tax and details object using proper Pydantic model
dummy_details = TaxCalculationDetail(
    relationship="ENFANT",
    gross_amount=1000.0,
    allowance_name="Abattement test",
    allowance_amount=100.0,
    net_taxable=900.0,
    brackets_applied=[],
    total_tax=100.0
)
mock_calc_tax.return_value = (100.0, dummy_details)

calc = SuccessionCalculator()

# Setup basic scenario
heir = FamilyMember(id='h1', birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD)
marriage_date = date(2000, 1, 1)

# TEST 1: Funeral Expenses Capping
print('\n[Test 1] Funeral Expenses > 1500€ (No Proof)')
input_data_1 = SimulationInput(
    members=[heir],
    assets=[],
    debts=[
        Debt(
            id='d1', amount=5000.0, debt_type='FUNERAL', 
            is_deductible=True, asset_origin=AssetOrigin.COMMUNITY_PROPERTY,
            proof_provided=False
        )
    ],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
# Note: Matrimonial regime Separation here to avoid liquidation complexity for this simple test

result_1 = calc.run(input_data_1)
# Total deductible should be 1500
total_debts = result_1.global_metrics.total_estate_value + 1500 - result_1.global_metrics.total_estate_value # Tricky way to get debts.. wait, reconstitute_estate output isn't directly exposed in global metrics easily except as diff. 
# Better: check the calculation steps or warnings.
# ACTUALLY, total_estate_value = net_assets + donations - debts. 
# Here net_assets = 0, donations = 0. So total_estate_value = -debts.
deducted = -result_1.global_metrics.total_estate_value
print(f"Deducted: {deducted}€ (Expected: {MAX_FUNERAL_DEDUCTION}€)")
print("Warnings:", result_1.warnings)

assert abs(deducted - MAX_FUNERAL_DEDUCTION) < 0.01, f"Expected {MAX_FUNERAL_DEDUCTION}, got {deducted}"
assert any("plafonnés" in w for w in result_1.warnings), "Missing warning about capping"
print("✅ Test 1 Passed")


# TEST 2: Funeral Expenses > 1500€ (WITH Proof)
print('\n[Test 2] Funeral Expenses > 1500€ (WITH Proof)')
input_data_2 = SimulationInput(
    members=[heir],
    assets=[],
    debts=[
        Debt(
            id='d2', amount=5000.0, debt_type='FUNERAL', 
            is_deductible=True, asset_origin=AssetOrigin.COMMUNITY_PROPERTY,
            proof_provided=True 
        )
    ],
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
result_2 = calc.run(input_data_2)
deducted_2 = -result_2.global_metrics.total_estate_value
print(f"Deducted: {deducted_2}€ (Expected: 5000€)")
print("Warnings:", result_2.warnings)

assert abs(deducted_2 - 5000.0) < 0.01, f"Expected 5000, got {deducted_2}"
assert any("supérieurs au plafond légal" in w for w in result_2.warnings), "Missing advisory warning"
print("✅ Test 2 Passed")


# TEST 3: Date Consistency (Community Asset before Marriage)
print('\n[Test 3] Date Consistency (Community Asset before Marriage with COMMUNITY regime)')
input_data_3 = SimulationInput(
    members=[heir],
    assets=[
        Asset(
            id='a1', estimated_value=100000, 
            asset_origin=AssetOrigin.COMMUNITY_PROPERTY, 
            ownership_mode=OwnershipMode.FULL_OWNERSHIP,
            acquisition_date=date(1990, 1, 1) # Before 2000
        )
    ],
    debts=[],
    matrimonial_regime=MatrimonialRegime.COMMUNITY_LEGAL, # Needs COMMUNITY_LEGAL regime
    marriage_date=marriage_date
)
result_3 = calc.run(input_data_3)
print("Warnings:", result_3.warnings)
assert any("antérieure au mariage" in w for w in result_3.warnings), "Missing warning about pre-marriage community asset"
print("✅ Test 3 Passed")


# TEST 4: Date Consistency (Personal Asset during Marriage)
print('\n[Test 4] Date Consistency (Personal Asset during Marriage with COMMUNITY regime)')
input_data_4 = SimulationInput(
    members=[heir],
    assets=[
        Asset(
            id='a2', estimated_value=100000, 
            asset_origin=AssetOrigin.PERSONAL_PROPERTY, 
            ownership_mode=OwnershipMode.FULL_OWNERSHIP,
            acquisition_date=date(2005, 1, 1) # After 2000
        )
    ],
    debts=[],
    matrimonial_regime=MatrimonialRegime.COMMUNITY_LEGAL,
    marriage_date=marriage_date
)
result_4 = calc.run(input_data_4)
print("Warnings:", result_4.warnings)
assert any("pendant le mariage" in w for w in result_4.warnings), "Missing warning about post-marriage personal asset"
print("✅ Test 4 Passed")

print("\n🎉 All Security & Compliance tests passed!")
