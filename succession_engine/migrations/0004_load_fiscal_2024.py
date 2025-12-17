# Generated manually - Data migration to load fiscal legislation 2024

from django.db import migrations


def load_fiscal_data(apps, schema_editor):
    """Insert fiscal legislation data for 2024."""
    Legislation = apps.get_model('succession_engine', 'Legislation')
    Allowance = apps.get_model('succession_engine', 'Allowance')
    TaxBracket = apps.get_model('succession_engine', 'TaxBracket')
    
    # Create Legislation 2024
    legislation, created = Legislation.objects.get_or_create(
        year=2024,
        defaults={
            'name': 'Loi de Finances 2024',
            'is_active': True
        }
    )
    
    # Deactivate other legislations
    Legislation.objects.exclude(pk=legislation.pk).update(is_active=False)
    
    # Allowances (Art. 779 CGI)
    allowances_data = [
        ('CHILD', 100000.00),    # Enfants/Parents
        ('SIBLING', 15932.00),   # Frères/Sœurs
        ('SPOUSE', 0.00),        # Conjoint (exonéré totalement)
        ('OTHER', 1594.00),      # Autres
    ]
    
    for relationship, amount in allowances_data:
        Allowance.objects.get_or_create(
            legislation=legislation,
            relationship=relationship,
            defaults={'amount': amount}
        )
    
    # Tax Brackets - Ligne Directe (Art. 777 CGI)
    child_brackets = [
        (0, 8072, 0.05),
        (8072, 12109, 0.10),
        (12109, 15932, 0.15),
        (15932, 552324, 0.20),
        (552324, 902838, 0.30),
        (902838, 1805677, 0.40),
        (1805677, None, 0.45),
    ]
    
    for min_amt, max_amt, rate in child_brackets:
        TaxBracket.objects.get_or_create(
            legislation=legislation,
            relationship='CHILD',
            min_amount=min_amt,
            defaults={
                'max_amount': max_amt,
                'rate': rate
            }
        )
    
    # Tax Brackets - Frères/Sœurs
    sibling_brackets = [
        (0, 24430, 0.35),
        (24430, None, 0.45),
    ]
    
    for min_amt, max_amt, rate in sibling_brackets:
        TaxBracket.objects.get_or_create(
            legislation=legislation,
            relationship='SIBLING',
            min_amount=min_amt,
            defaults={
                'max_amount': max_amt,
                'rate': rate
            }
        )
    
    # Tax Brackets - Autres (60% flat)
    TaxBracket.objects.get_or_create(
        legislation=legislation,
        relationship='OTHER',
        min_amount=0,
        defaults={
            'max_amount': None,
            'rate': 0.60
        }
    )


def reverse_fiscal_data(apps, schema_editor):
    """Remove fiscal data (for rollback)."""
    Legislation = apps.get_model('succession_engine', 'Legislation')
    Legislation.objects.filter(year=2024).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('succession_engine', '0003_donation'),
    ]

    operations = [
        migrations.RunPython(load_fiscal_data, reverse_fiscal_data),
    ]
