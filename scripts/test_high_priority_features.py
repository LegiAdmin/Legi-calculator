"""
Test script for high priority features:
1. Representation (grandchildren representing deceased parent)
2. Main residence 20% allowance
"""

import os
import sys
import django

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.schemas import SimulationInput, Asset, FamilyMember, OwnershipMode, AssetOrigin, HeirRelation, Wishes, SpouseChoice, SpouseChoiceType
from succession_engine.core.calculator import SuccessionCalculator
from datetime import date

print("🧪 Test des Fonctionnalités Haute Priorité")
print("=" * 60)

# ===================== TEST 1: REPRESENTATION =====================
print("\n👶 TEST 1: Représentation par souche")
print("-" * 60)
print("Scénario: 2 souches (enfant A + parent B décédé avec 2 petits-enfants)")
print("Patrimoine 600k€ → Souche A = 300k€, Souche B = 300k€")
print("Petits-enfants B1 et B2 = 150k€ chacun")

try:
    sim1 = SimulationInput(
        matrimonial_regime='SEPARATION',
        assets=[
            Asset(
                id='patrimoine',
                estimated_value=600000,
                ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                asset_origin=AssetOrigin.PERSONAL_PROPERTY
            )
        ],
        members=[
            FamilyMember(id='child_A', birth_date=date(1975, 3, 15), relationship=HeirRelation.CHILD),
            FamilyMember(id='grandchild_B1', birth_date=date(2000, 5, 20), relationship=HeirRelation.GRANDCHILD, represented_heir_id='deceased_child_B'),
            FamilyMember(id='grandchild_B2', birth_date=date(2002, 8, 10), relationship=HeirRelation.GRANDCHILD, represented_heir_id='deceased_child_B')
        ]
    )

    calc = SuccessionCalculator()
    result1 = calc.run(sim1)

    print(f"\nRésultat:")
    print(f"  Masse: {result1.global_metrics.total_estate_value:,.0f}€")
    
    for heir in result1.heirs_breakdown:
        print(f"  {heir.id}: {heir.gross_share_value:,.0f}€ ({heir.legal_share_percent*100:.1f}%)")
    
    # Validation
    souche_A = next((h.gross_share_value for h in result1.heirs_breakdown if h.id == 'child_A'), 0)
    souche_B = sum(h.gross_share_value for h in result1.heirs_breakdown if h.id.startswith('grandchild'))
    
    if abs(souche_A - 300000) < 1 and abs(souche_B - 300000) < 1:
        print(f"\n✅ TEST 1 RÉUSSI - Représentation par souche correcte!")
    else:
        print(f"\n❌ TEST 1 ÉCHEC - Souches incorrectes (A={souche_A}, B={souche_B})")
        
except Exception as e:
    print(f"❌ Erreur: {e}")

# ===================== TEST 2: RESIDENCE PRINCIPALE =====================
print("\n🏠 TEST 2: Abattement résidence principale 20%")
print("-" * 60)
print("Scénario: Résidence 500k€ (biens communs), conjoint occupant")
print("Attendu: 500k → -20% = 400k → /2 (communauté) = 200k€ dans succession")

try:
    sim2 = SimulationInput(
        matrimonial_regime='COMMUNITY_LEGAL',
        marriage_date=date(1980, 5, 10),
        assets=[
            Asset(
                id='residence_principale',
                estimated_value=500000,
                ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                asset_origin=AssetOrigin.COMMUNITY_PROPERTY,
                is_main_residence=True,
                spouse_occupies_property=True
            )
        ],
        members=[
            FamilyMember(id='spouse', birth_date=date(1955, 3, 20), relationship=HeirRelation.SPOUSE),
            FamilyMember(id='child1', birth_date=date(1985, 6, 15), relationship=HeirRelation.CHILD)
        ],
        wishes=Wishes(
            spouse_choice=SpouseChoice(choice=SpouseChoiceType.QUARTER_OWNERSHIP),
            has_spouse_donation=False
        )
    )

    result2 = calc.run(sim2)

    print(f"\nRésultat:")
    print(f"  Masse successorale: {result2.global_metrics.total_estate_value:,.0f}€")
    
    # Validation
    expected = 200000  # 500k * 0.8 / 2
    if abs(result2.global_metrics.total_estate_value - expected) < 1:
        print(f"\n✅ TEST 2 RÉUSSI - Abattement 20% appliqué!")
    else:
        print(f"\n❌ TEST 2 ÉCHEC - Attendu {expected:,.0f}€, obtenu {result2.global_metrics.total_estate_value:,.0f}€")

except Exception as e:
    print(f"❌ Erreur: {e}")

# ===================== TEST 3: SANS ABATTEMENT =====================
print("\n🏠 TEST 3: Résidence principale SANS abattement (conjoint n'occupe pas)")
print("-" * 60)

try:
    sim3 = SimulationInput(
        matrimonial_regime='SEPARATION',
        assets=[
            Asset(
                id='residence_principale',
                estimated_value=500000,
                ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                asset_origin=AssetOrigin.PERSONAL_PROPERTY,
                is_main_residence=True,
                spouse_occupies_property=False  # Pas d'abattement
            )
        ],
        members=[
            FamilyMember(id='child1', birth_date=date(1985, 6, 15), relationship=HeirRelation.CHILD),
            FamilyMember(id='child2', birth_date=date(1988, 9, 22), relationship=HeirRelation.CHILD)
        ]
    )

    result3 = calc.run(sim3)

    print(f"\nRésultat:")
    print(f"  Masse: {result3.global_metrics.total_estate_value:,.0f}€")
    
    # Validation: 100% sans abattement
    if abs(result3.global_metrics.total_estate_value - 500000) < 1:
        print(f"\n✅ TEST 3 RÉUSSI - Pas d'abattement (conjoint n'occupe pas)")
    else:
        print(f"\n❌ TEST 3 ÉCHEC")

except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("📊 RÉSUMÉ DES TESTS")
print("=" * 60)
