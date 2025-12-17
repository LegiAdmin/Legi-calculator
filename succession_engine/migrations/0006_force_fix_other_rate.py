# Generated manually - Force correct OTHER tax rate by deleting and recreating

from django.db import migrations


def force_fix_other_tax_rate(apps, schema_editor):
    """Force fix the OTHER tax bracket by deleting and recreating with 60%."""
    TaxBracket = apps.get_model('succession_engine', 'TaxBracket')
    Legislation = apps.get_model('succession_engine', 'Legislation')
    
    # Get active legislation
    try:
        legislation = Legislation.objects.get(is_active=True)
    except Legislation.DoesNotExist:
        print("[MIGRATION 0006] No active legislation found!")
        return
    
    # Delete ALL existing OTHER brackets
    deleted_count = TaxBracket.objects.filter(relationship='OTHER').delete()[0]
    print(f"[MIGRATION 0006] Deleted {deleted_count} existing OTHER bracket(s)")
    
    # Create fresh OTHER bracket with correct 60% rate
    TaxBracket.objects.create(
        legislation=legislation,
        relationship='OTHER',
        min_amount=0,
        max_amount=None,
        rate=0.60
    )
    print("[MIGRATION 0006] Created OTHER bracket with rate=0.60 (60%)")


def reverse_force_fix(apps, schema_editor):
    """Cannot reverse - this is a data fix."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('succession_engine', '0005_fix_other_tax_rate'),
    ]

    operations = [
        migrations.RunPython(force_fix_other_tax_rate, reverse_force_fix),
    ]
