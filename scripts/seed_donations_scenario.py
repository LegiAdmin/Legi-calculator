import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

# Scénario avec donations
scenario = {
    "name": "📜 Donations antérieures - Rapport civil",
    "description": "Don manuel de 30k€ au conjoint (2023) et donation-partage de 5k€ à l'enfant (2004)",
    "input_data": {
        "matrimonial_regime": "COMMUNITY_LEGAL",
        "marriage_date": "2000-06-15",
        "assets": [
            {
                "id": "residence",
                "estimated_value": 400000,
                "ownership_mode": "FULL_OWNERSHIP",
                "asset_origin": "COMMUNITY_PROPERTY",
                "acquisition_date": "2005-03-20"
            }
        ],
        "members": [
            {"id": "child1", "birth_date": "2002-05-10", "relationship": "CHILD", "is_from_current_union": True}
        ],
        "wishes": {
            "has_spouse_donation": True,
            "testament_distribution": "LEGAL"
        },
        "donations": [
            {
                "id": "donation1",
                "donation_type": "don_manuel",
                "beneficiary_name": "Conjoint",
                "beneficiary_relationship": "SPOUSE",
                "donation_date": "2023-10-10",
                "description": "Partage",
                "purpose": "Immobilier",
                "original_value": 30000,
                "current_estimated_value": 42971,
                "is_declared_to_tax": False,
                "notes": "Oublié la déclaration"
            },
            {
                "id": "donation2",
                "donation_type": "donation_partage",
                "beneficiary_name": "Paul",
                "beneficiary_heir_id": "child1",
                "beneficiary_relationship": "CHILD",
                "donation_date": "2004-10-23",
                "description": "Voiture",
                "purpose": "Voiture",
                "original_value": 4974,
                "is_declared_to_tax": False,
                "notary_signature_date": "2004-09-10",
                "notary_name": "Maître michou",
                "notary_city": "Paris"
            }
        ]
    }
}

if not SimulationScenario.objects.filter(name=scenario["name"]).exists():
    SimulationScenario.objects.create(**scenario)
    print(f"✅ Créé: {scenario['name']}")
else:
    # Update existing
    SimulationScenario.objects.filter(name=scenario["name"]).update(
        description=scenario["description"],
        input_data=scenario["input_data"]
    )
    print(f"🔄 Mis à jour: {scenario['name']}")

print("\n📊 Donations dans le scénario:")
print("  1. Don manuel de 30k€ au conjoint (non déclaré)")
print("  2. Donation-partage de 5k€ à l'enfant (acte notarié)")
