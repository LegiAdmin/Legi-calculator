# Generated manually - Data migration to add collateral taxes (Nephews, Aunts, Cousins)

from django.db import migrations


def add_collateral_taxes(apps, schema_editor):
    """Insert fiscal data for Collaterals (Nephews, Aunts, Cousins)."""
    Legislation = apps.get_model('succession_engine', 'Legislation')
    Allowance = apps.get_model('succession_engine', 'Allowance')
    TaxBracket = apps.get_model('succession_engine', 'TaxBracket')
    
    # Get active legislation (2024)
    legislation = Legislation.objects.filter(is_active=True).first()
    if not legislation:
        return

    # 1. NEPHEW_NIECE (Neveux et Nièces)
    # Art. 779 V CGI: Abattement 7 967 €
    # Art. 777 CGI Table III: Taux 55%
    Allowance.objects.update_or_create(
        legislation=legislation,
        relationship='NEPHEW_NIECE',
        defaults={'amount': 7967.00}
    )
    
    TaxBracket.objects.update_or_create(
        legislation=legislation,
        relationship='NEPHEW_NIECE',
        min_amount=0,
        defaults={
            'max_amount': None,
            'rate': 0.55
        }
    )

    # 2. RELATIVES_UP_TO_4TH_DEGREE (Parents jusqu'au 4ème degré inclus)
    # Oncles, Tantes, Cousins germains, Grands-Oncles/Tantes
    # Art. 779 IV CGI: Abattement 1 594 € (défaut personal abatement)
    # Art. 777 CGI Table III: Taux 55%
    
    Allowance.objects.update_or_create(
        legislation=legislation,
        relationship='RELATIVES_UP_TO_4TH_DEGREE',
        defaults={'amount': 1594.00}
    )
    
    TaxBracket.objects.update_or_create(
        legislation=legislation,
        relationship='RELATIVES_UP_TO_4TH_DEGREE',
        min_amount=0,
        defaults={
            'max_amount': None,
            'rate': 0.55
        }
    )


def remove_collateral_taxes(apps, schema_editor):
    """Remove collateral taxes."""
    Allowance = apps.get_model('succession_engine', 'Allowance')
    TaxBracket = apps.get_model('succession_engine', 'TaxBracket')
    
    Allowance.objects.filter(relationship__in=['NEPHEW_NIECE', 'RELATIVES_UP_TO_4TH_DEGREE']).delete()
    TaxBracket.objects.filter(relationship__in=['NEPHEW_NIECE', 'RELATIVES_UP_TO_4TH_DEGREE']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('succession_engine', '0006_force_fix_other_rate'),
    ]

    operations = [
        migrations.RunPython(add_collateral_taxes, remove_collateral_taxes),
    ]
