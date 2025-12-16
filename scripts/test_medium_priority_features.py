"""
Test script for medium priority features:
1. Usufruct valuation (Art. 669 CGI)
2. Reduction indemnity (Art. 920+ CC)
"""

import os
import sys
import django

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.rules.usufruct import UsufructValuator
from succession_engine.rules.reduction import ReductionCalculator, Liberality
from datetime import date

print("🧪 Test des Fonctionnalités Moyenne Priorité")
print("=" * 60)

# ===================== TEST 1: USUFRUCT VALUATION =====================
print("\n📊 TEST 1: Valorisation usufruit selon âge (Art. 669 CGI)")
print("-" * 60)

test_cases = [
    (date(2005, 1, 1), "< 21 ans", 0.90),
    (date(1995, 1, 1), "21-30 ans", 0.80),
    (date(1985, 1, 1), "31-40 ans", 0.70),
    (date(1975, 1, 1), "41-50 ans", 0.60),
    (date(1965, 1, 1), "51-60 ans", 0.50),
    (date(1955, 1, 1), "61-70 ans", 0.40),
    (date(1945, 1, 1), "71-80 ans", 0.30),
    (date(1935, 1, 1), "81-90 ans", 0.20),
    (date(1920, 1, 1), "> 91 ans", 0.10),
]

total_value = 1_000_000
all_ok = True

print(f"\nValeur totale du bien: {total_value:,.0f}€")
print(f"Date de référence: {date.today()}")
print()
print(f"{'Âge usufruitier':<15} {'Usufruit':<15} {'Nue-propriété':<15} {'Taux':<10}")
print("-" * 55)

for birth_date, age_range, expected_rate in test_cases:
    usufruct_val, bare_val, rate = UsufructValuator.calculate_value(total_value, birth_date)
    
    age = date.today().year - birth_date.year
    status = "✅" if abs(rate - expected_rate) < 0.01 else "❌"
    all_ok = all_ok and abs(rate - expected_rate) < 0.01
    
    print(f"{age_range:<15} {usufruct_val:>12,.0f}€ {bare_val:>12,.0f}€ {rate*100:>8.0f}% {status}")

print()
if all_ok:
    print("✅ TEST 1 RÉUSSI - Barème usufruit correct!")
else:
    print("❌ TEST 1 ÉCHEC - Vérifier le barème")

# ===================== TEST 2: REDUCTION CALCULATOR =====================
print("\n💰 TEST 2: Calcul indemnité de réduction (Art. 920+ CC)")
print("-" * 60)

# Scenario: Quotité disponible 100k€, mais 150k€ de libéralités
liberalities = [
    Liberality("don1", "DONATION", "child1", 80000, date(2020, 5, 15)),
    Liberality("don2", "DONATION", "friend", 50000, date(2022, 8, 20)),
    Liberality("legs1", "BEQUEST", "charity", 20000, date(2024, 1, 1)),
]

disposable_quota = 100000
legal_reserve = 200000

print(f"\nQuotité disponible: {disposable_quota:,.0f}€")
print(f"Réserve: {legal_reserve:,.0f}€")
print(f"Total libéralités: {sum(l.value for l in liberalities):,.0f}€")
print()

result = ReductionCalculator.calculate_reduction(liberalities, disposable_quota, legal_reserve)

print(f"Excès à réduire: {result.total_excess:,.0f}€")
print(f"Réserve restaurée: {result.reserve_restored:,.0f}€")
print()

if result.reduced_liberalities:
    print("Libéralités réduites (ordre légal: legs puis donations du plus récent au plus ancien):")
    for red in result.reduced_liberalities:
        print(f"  → {red['type']} {red['liberality_id']}: {red['original_value']:,.0f}€ → {red['reduced_value']:,.0f}€ (-{red['reduction_amount']:,.0f}€)")

# Validation
# Total 150k, QD 100k → excès 50k
# Ordre: d'abord legs1 (20k), puis don2 (30k restants)
expected_excess = 50000
if abs(result.total_excess - expected_excess) < 1:
    print(f"\n✅ TEST 2 RÉUSSI - Réduction calculée: {result.total_excess:,.0f}€")
else:
    print(f"\n❌ TEST 2 ÉCHEC - Attendu {expected_excess:,.0f}€, obtenu {result.total_excess:,.0f}€")

print("\n" + "=" * 60)
print("📊 RÉSUMÉ")
print("=" * 60)
