"""
Test script for spouse inheritance scenarios (Art. 757-1 and 757-2 Code civil).

Tests:
1. Spouse alone (no children, parents, siblings) → 100%
2. Spouse with siblings → 50/50
3. Spouse with 2 parents → 50% spouse, 25% each parent
4. Spouse with 1 parent → 75% spouse, 25% parent
"""

import os
import sys
import django

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.schemas import (
    SimulationInput, Asset, FamilyMember, OwnershipMode, 
    AssetOrigin, HeirRelation
)
from succession_engine.core.calculator import SuccessionCalculator
from datetime import date

print("🧪 Test des Scénarios Conjoint (Art. 757-1 et 757-2 CC)")
print("=" * 60)

calc = SuccessionCalculator()
errors = []

# ===================== TEST 1: CONJOINT SEUL =====================
print("\n💍 TEST 1: Conjoint seul (sans enfants, parents, frères)")
print("-" * 60)
print("Scénario: Patrimoine 500k€, conjoint unique héritier")
print("Attendu: Conjoint reçoit 100%")

try:
    sim1 = SimulationInput(
        matrimonial_regime='SEPARATION',
        assets=[
            Asset(
                id='patrimoine',
                estimated_value=500000,
                ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                asset_origin=AssetOrigin.PERSONAL_PROPERTY
            )
        ],
        members=[
            FamilyMember(id='spouse', birth_date=date(1960, 3, 15), relationship=HeirRelation.SPOUSE)
        ]
    )

    result1 = calc.run(sim1)
    
    spouse_share = next((h for h in result1.heirs_breakdown if h.id == 'spouse'), None)
    
    if spouse_share and abs(spouse_share.gross_share_value - 500000) < 1:
        print(f"\n✅ TEST 1 RÉUSSI - Conjoint reçoit {spouse_share.gross_share_value:,.0f}€ (100%)")
    else:
        msg = f"❌ TEST 1 ÉCHEC - Attendu 500k€, obtenu {spouse_share.gross_share_value if spouse_share else 'N/A'}€"
        print(f"\n{msg}")
        errors.append(msg)
        
except Exception as e:
    errors.append(f"TEST 1 Erreur: {e}")
    print(f"❌ Erreur: {e}")

# ===================== TEST 2: CONJOINT + FRÈRES =====================
print("\n👫 TEST 2: Conjoint avec frères/sœurs (sans enfants ni parents)")
print("-" * 60)
print("Scénario: Patrimoine 600k€, conjoint + 2 frères")
print("Attendu: Conjoint 50% (300k€), chaque frère 25% (150k€)")

try:
    sim2 = SimulationInput(
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
            FamilyMember(id='spouse', birth_date=date(1960, 3, 15), relationship=HeirRelation.SPOUSE),
            FamilyMember(id='brother1', birth_date=date(1965, 5, 20), relationship=HeirRelation.SIBLING),
            FamilyMember(id='brother2', birth_date=date(1968, 8, 10), relationship=HeirRelation.SIBLING)
        ]
    )

    result2 = calc.run(sim2)
    
    spouse = next((h for h in result2.heirs_breakdown if h.id == 'spouse'), None)
    sibling_total = sum(h.gross_share_value for h in result2.heirs_breakdown if 'brother' in h.id)
    
    if spouse and abs(spouse.gross_share_value - 300000) < 1 and abs(sibling_total - 300000) < 1:
        print(f"\n✅ TEST 2 RÉUSSI - Conjoint: {spouse.gross_share_value:,.0f}€, Frères: {sibling_total:,.0f}€")
    else:
        msg = f"❌ TEST 2 ÉCHEC - Conjoint: {spouse.gross_share_value if spouse else 'N/A'}€, Frères: {sibling_total}€"
        print(f"\n{msg}")
        errors.append(msg)
        
except Exception as e:
    errors.append(f"TEST 2 Erreur: {e}")
    print(f"❌ Erreur: {e}")

# ===================== TEST 3: CONJOINT + 2 PARENTS =====================
print("\n👨‍👩‍👦 TEST 3: Conjoint avec 2 parents (sans enfants)")
print("-" * 60)
print("Scénario: Patrimoine 400k€, conjoint + 2 parents")
print("Attendu: Conjoint 50% (200k€), chaque parent 25% (100k€)")

try:
    sim3 = SimulationInput(
        matrimonial_regime='SEPARATION',
        assets=[
            Asset(
                id='patrimoine',
                estimated_value=400000,
                ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                asset_origin=AssetOrigin.PERSONAL_PROPERTY
            )
        ],
        members=[
            FamilyMember(id='spouse', birth_date=date(1960, 3, 15), relationship=HeirRelation.SPOUSE),
            FamilyMember(id='father', birth_date=date(1935, 5, 20), relationship=HeirRelation.PARENT),
            FamilyMember(id='mother', birth_date=date(1938, 8, 10), relationship=HeirRelation.PARENT)
        ]
    )

    result3 = calc.run(sim3)
    
    spouse = next((h for h in result3.heirs_breakdown if h.id == 'spouse'), None)
    parent_total = sum(h.gross_share_value for h in result3.heirs_breakdown if h.id in ['father', 'mother'])
    
    if spouse and abs(spouse.gross_share_value - 200000) < 1 and abs(parent_total - 200000) < 1:
        print(f"\n✅ TEST 3 RÉUSSI - Conjoint: {spouse.gross_share_value:,.0f}€, Parents: {parent_total:,.0f}€")
    else:
        msg = f"❌ TEST 3 ÉCHEC - Conjoint: {spouse.gross_share_value if spouse else 'N/A'}€, Parents: {parent_total}€"
        print(f"\n{msg}")
        errors.append(msg)
        
except Exception as e:
    errors.append(f"TEST 3 Erreur: {e}")
    print(f"❌ Erreur: {e}")

# ===================== TEST 4: CONJOINT + 1 PARENT =====================
print("\n👨‍👦 TEST 4: Conjoint avec 1 parent (sans enfants)")
print("-" * 60)
print("Scénario: Patrimoine 400k€, conjoint + 1 parent")
print("Attendu: Conjoint 75% (300k€), parent 25% (100k€)")

try:
    sim4 = SimulationInput(
        matrimonial_regime='SEPARATION',
        assets=[
            Asset(
                id='patrimoine',
                estimated_value=400000,
                ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                asset_origin=AssetOrigin.PERSONAL_PROPERTY
            )
        ],
        members=[
            FamilyMember(id='spouse', birth_date=date(1960, 3, 15), relationship=HeirRelation.SPOUSE),
            FamilyMember(id='mother', birth_date=date(1938, 8, 10), relationship=HeirRelation.PARENT)
        ]
    )

    result4 = calc.run(sim4)
    
    spouse = next((h for h in result4.heirs_breakdown if h.id == 'spouse'), None)
    parent = next((h for h in result4.heirs_breakdown if h.id == 'mother'), None)
    
    if spouse and parent and abs(spouse.gross_share_value - 300000) < 1 and abs(parent.gross_share_value - 100000) < 1:
        print(f"\n✅ TEST 4 RÉUSSI - Conjoint: {spouse.gross_share_value:,.0f}€, Parent: {parent.gross_share_value:,.0f}€")
    else:
        msg = f"❌ TEST 4 ÉCHEC - Conjoint: {spouse.gross_share_value if spouse else 'N/A'}€, Parent: {parent.gross_share_value if parent else 'N/A'}€"
        print(f"\n{msg}")
        errors.append(msg)
        
except Exception as e:
    errors.append(f"TEST 4 Erreur: {e}")
    print(f"❌ Erreur: {e}")

# ===================== RÉSUMÉ =====================
print("\n" + "=" * 60)
print("📊 RÉSUMÉ")
print("=" * 60)

if errors:
    print(f"\n❌ {len(errors)} erreur(s) détectée(s):")
    for err in errors:
        print(f"  - {err}")
else:
    print("\n✅ TOUS LES TESTS PASSENT!")
    print("   Art. 757-1 CC (conjoint + parents) : OK")
    print("   Art. 757-2 CC (conjoint seul/frères) : OK")
