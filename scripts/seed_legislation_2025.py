import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import Legislation, TaxBracket, Allowance, UsufructScale

print("🗑️  Nettoyage des anciennes règles...")
Legislation.objects.all().delete()

print("📜 Création de la législation 2025...")
legislation = Legislation.objects.create(
    name="Loi de Finances 2025",
    year=2025,
    is_active=True
)

print("💶 Création des abattements 2025...")
# Abattements selon la législation française 2025
allowances = [
    {'relationship': 'CHILD', 'amount': 100000.00},  # Enfants et ascendants
    {'relationship': 'SIBLING', 'amount': 15932.00},  # Frères et sœurs
    {'relationship': 'OTHER', 'amount': 1594.00},     # Non-parents
    {'relationship': 'NEPHEW_NIECE', 'amount': 7967.00}, # Neveux et nièces (Art. 779 V CGI)
    {'relationship': 'SPOUSE', 'amount': 999999999.00},  # Conjoint (exonéré)
]

for data in allowances:
    Allowance.objects.create(legislation=legislation, **data)
    print(f"  ✅ {data['relationship']}: {data['amount']:,.0f}€")

print("\n📊 Création des barèmes fiscaux 2025...")

# Barème en ligne directe (enfants, parents) - 2025
print("  → Ligne directe (enfants/parents)")
direct_line_brackets = [
    {'min_amount': 0, 'max_amount': 8072, 'rate': 0.05},
    {'min_amount': 8072, 'max_amount': 12109, 'rate': 0.10},
    {'min_amount': 12109, 'max_amount': 15932, 'rate': 0.15},
    {'min_amount': 15932, 'max_amount': 552324, 'rate': 0.20},
    {'min_amount': 552324, 'max_amount': 902838, 'rate': 0.30},
    {'min_amount': 902838, 'max_amount': 1805677, 'rate': 0.40},
    {'min_amount': 1805677, 'max_amount': None, 'rate': 0.45},
]

for bracket in direct_line_brackets:
    TaxBracket.objects.create(
        legislation=legislation,
        relationship='CHILD',
        **bracket
    )
    max_display = f"{bracket['max_amount']:,.0f}€" if bracket['max_amount'] else "∞"
    print(f"    {bracket['min_amount']:>10,.0f}€ - {max_display:>15} : {bracket['rate']*100:>5.1f}%")

# Barème entre frères et sœurs - 2025
print("\n  → Frères et sœurs")
sibling_brackets = [
    {'min_amount': 0, 'max_amount': 24430, 'rate': 0.35},
    {'min_amount': 24430, 'max_amount': None, 'rate': 0.45},
]

for bracket in sibling_brackets:
    TaxBracket.objects.create(
        legislation=legislation,
        relationship='SIBLING',
        **bracket
    )
    max_display = f"{bracket['max_amount']:,.0f}€" if bracket['max_amount'] else "∞"
    print(f"    {bracket['min_amount']:>10,.0f}€ - {max_display:>15} : {bracket['rate']*100:>5.1f}%")

# Barème neveux et nièces - 2025 (Art. 777 CGI Tableau III)
print("\n  → Neveux et nièces")
nephew_brackets = [
    {'min_amount': 0, 'max_amount': None, 'rate': 0.55},
]

for bracket in nephew_brackets:
    TaxBracket.objects.create(
        legislation=legislation,
        relationship='NEPHEW_NIECE',
        **bracket
    )
    print(f"    Taux unique: {bracket['rate']*100:.0f}%")

# Barème autres (neveux, nièces, non-parents) - 2025
print("\n  → Autres (neveux, nièces, non-parents)")
other_brackets = [
    {'min_amount': 0, 'max_amount': None, 'rate': 0.60},  # Autres: 60% (Art. 777 CGI)
]

for bracket in other_brackets:
    TaxBracket.objects.create(
        legislation=legislation,
        relationship='OTHER',
        **bracket
    )
    print(f"    Taux unique: {bracket['rate']*100:.0f}%")

print("\n📐 Création du barème d'usufruit 2025 (Art. 669 CGI)...")
# Barème fiscal de l'usufruit selon l'âge de l'usufruitier
usufruct_scales = [
    {'max_age': 21, 'rate': 0.90},
    {'max_age': 31, 'rate': 0.80},
    {'max_age': 41, 'rate': 0.70},
    {'max_age': 51, 'rate': 0.60},
    {'max_age': 61, 'rate': 0.50},
    {'max_age': 71, 'rate': 0.40},
    {'max_age': 81, 'rate': 0.30},
    {'max_age': 91, 'rate': 0.20},
    {'max_age': 120, 'rate': 0.10},  # > 91 ans
]

for scale in usufruct_scales:
    UsufructScale.objects.create(legislation=legislation, **scale)
    print(f"  Moins de {scale['max_age']:>3} ans: {scale['rate']*100:>3.0f}%")

print("\n✨ Législation 2025 créée avec succès !")
print(f"📋 Total:")
print(f"  - {Allowance.objects.filter(legislation=legislation).count()} abattements")
print(f"  - {TaxBracket.objects.filter(legislation=legislation).count()} tranches fiscales")
print(f"  - {UsufructScale.objects.filter(legislation=legislation).count()} barèmes d'usufruit")
