# Generated manually - Fix OTHER tax rate from 55% to 60%

from django.db import migrations


def fix_other_tax_rate(apps, schema_editor):
    """Fix the OTHER tax bracket rate to 60%."""
    TaxBracket = apps.get_model('succession_engine', 'TaxBracket')
    
    # Update all OTHER tax brackets to 60%
    updated = TaxBracket.objects.filter(relationship='OTHER').update(rate=0.60)
    print(f"[MIGRATION] Updated {updated} OTHER tax bracket(s) to 60%")


def reverse_fix(apps, schema_editor):
    """Reverse - set back to 55% (though this shouldn't be needed)."""
    TaxBracket = apps.get_model('succession_engine', 'TaxBracket')
    TaxBracket.objects.filter(relationship='OTHER').update(rate=0.55)


class Migration(migrations.Migration):

    dependencies = [
        ('succession_engine', '0004_load_fiscal_2024'),
    ]

    operations = [
        migrations.RunPython(fix_other_tax_rate, reverse_fix),
    ]
