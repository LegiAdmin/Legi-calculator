
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
    HeirRelation, AssetOrigin, OwnershipMode, TaxCalculationDetail
)
from succession_engine.core.calculator import SuccessionCalculator

print('=== Phase 11 Verification: International Support ===')

# Mock FiscalCalculator to focus on warnings
patcher = patch('succession_engine.rules.fiscal.FiscalCalculator.calculate_inheritance_tax')
mock_calc_tax = patcher.start()
mock_calc_tax.return_value = (0.0, TaxCalculationDetail(
    relationship="ENFANT", gross_amount=0, allowance_name="", allowance_amount=0, net_taxable=0, brackets_applied=[], total_tax=0
))

calc = SuccessionCalculator()

heir = FamilyMember(id='h1', birth_date=date(1990, 1, 1), relationship=HeirRelation.CHILD)

print('\n[Test 1] Foreign Residence (Warning Expected)')
input_data_1 = SimulationInput(
    members=[heir],
    assets=[],
    debts=[],
    residence_country="UK", # Extranéité
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
result_1 = calc.run(input_data_1)
print(f"Residence: {input_data_1.residence_country}")
residence_warning = next((w for w in result_1.warnings if "défunt résidait à l'étranger" in w), None)
if residence_warning:
    print(f"✅ Warning Found: {residence_warning}")
else:
    print("❌ Warning NOT Found")
    print(result_1.warnings)

print('\n[Test 2] Foreign Asset (Warning Expected)')
asset_foreign = Asset(
    id='villa_espagne', 
    estimated_value=200_000, 
    location_country="ES", # Espagne
    asset_origin=AssetOrigin.PERSONAL_PROPERTY, 
    ownership_mode=OwnershipMode.FULL_OWNERSHIP
)
input_data_2 = SimulationInput(
    members=[heir],
    assets=[asset_foreign],
    debts=[],
    residence_country="FR", 
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
result_2 = calc.run(input_data_2)
print(f"Asset Location: {input_data_2.assets[0].location_country}")
asset_warning = next((w for w in result_2.warnings if "situé à l'étranger" in w), None)
if asset_warning:
    print(f"✅ Warning Found: {asset_warning}")
else:
    print("❌ Warning NOT Found")
    print(result_2.warnings)
    
print('\n[Test 3] All French (No Warning Expected)')
input_data_3 = SimulationInput(
    members=[heir],
    assets=[Asset(id='immo_fr', estimated_value=100_000, asset_origin=AssetOrigin.PERSONAL_PROPERTY, ownership_mode=OwnershipMode.FULL_OWNERSHIP)],
    debts=[],
    residence_country="FR",
    matrimonial_regime=MatrimonialRegime.SEPARATION
)
result_3 = calc.run(input_data_3)
intl_warnings = [w for w in result_3.warnings if "étranger" in w]
if not intl_warnings:
    print("✅ No International Warnings (Correct)")
else:
    print(f"❌ Unexpected warnings: {intl_warnings}")

print("\n🎉 Phase 11 Verification Complete!")
