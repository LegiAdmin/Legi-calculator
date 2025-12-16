"""
Test script for indivision support.
"""

import os
import sys
import django

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.schemas import SimulationInput, Asset, FamilyMember, OwnershipMode, AssetOrigin, IndivisionDetails, HeirRelation
from succession_engine.core.calculator import SuccessionCalculator
from datetime import date

print("🧪 Test Indivision Support\n")

# Test case: Maison en indivision avec conjoint (65% conjoint, 35% défunt)
simulation_input = SimulationInput(
    matrimonial_regime="COMMUNITY_LEGAL",
    marriage_date=date(2000, 1, 1),
    assets=[
        Asset(
            id="maison_indivision",
            estimated_value=500_000,
            ownership_mode=OwnershipMode.INDIVISION,
            asset_origin=AssetOrigin.PERSONAL_PROPERTY,
            acquisition_date=date(2010, 5, 15),
            indivision_details=IndivisionDetails(
                withSpouse=True,
                spouseShare=65.0,  # Conjoint détient 65%
                withOthers=False
            )
        ),
        Asset(
            id="compte_bancaire",
            estimated_value=100_000,
            ownership_mode=OwnershipMode.FULL_OWNERSHIP,
            asset_origin=AssetOrigin.PERSONAL_PROPERTY
        )
    ],
    members=[
        FamilyMember(id="spouse", birth_date=date(1970, 1, 1), relationship=HeirRelation.SPOUSE),
        FamilyMember(id="child1", birth_date=date(2000, 6, 1), relationship=HeirRelation.CHILD),
        FamilyMember(id="child2", birth_date=date(2002, 8, 15), relationship=HeirRelation.CHILD)
    ]
)

calculator = SuccessionCalculator()

try:
    result = calculator.run(simulation_input)
    
    print("✅ Calcul réussi!\n")
    
    print("📊 Résultats:")
    print(f"   Masse successorale: {result.global_metrics.total_estate_value:,.0f}€")
    print(f"   Réserve: {result.global_metrics.legal_reserve_value:,.0f}€")
    print(f"   Quotité disponible: {result.global_metrics.disposable_quota_value:,.0f}€")
    
    print("\n👥 Héritiers:")
    for heir in result.heirs_breakdown:
        print(f"   {heir.id}: {heir.gross_share_value:,.0f}€ (part: {heir.legal_share_percent:.1f}%)")
    
    print("\n🏠 Actifs:")
    for asset in result.assets_breakdown:
        print(f"   {asset.asset_id}: {asset.asset_value:,.0f}€ (origine: {asset.asset_origin})")
    
    print("\n📋 Étapes de calcul:")
    for step in result.calculation_steps:
        print(f"   {step.step_number}. {step.step_name}")
        print(f"      {step.result_summary}")
    
    # Vérifications
    print("\n🔍 Vérifications:")
    
    # La maison en indivision devrait compter pour 35% seulement
    expected_house_value = 500_000 * 0.35  # 175 000€
    expected_total = expected_house_value + 100_000  # 275 000€
    
    print(f"   Valeur maison attendue (35%): {expected_house_value:,.0f}€")
    print(f"   Masse totale attendue: {expected_total:,.0f}€")
    print(f"   Masse totale calculée: {result.global_metrics.total_estate_value:,.0f}€")
    
    if abs(result.global_metrics.total_estate_value - expected_total) < 1:
        print("   ✅ Calcul indivision correct!")
    else:
        print("   ❌ Erreur dans le calcul indivision")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
