import os
import django
import sys

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

scenarios = [
    {
        "name": "💳 Dettes - Crédit à la consommation",
        "description": "Succession avec crédit à la consommation déductible",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "appartement",
                    "estimated_value": 300000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1995-05-10", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1998-08-15", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL"
            },
            "debts": [
                {
                    "id": "credit_conso",
                    "amount": 50000,
                    "debt_type": "crédit à la consommation",
                    "is_deductible": True,
                    "asset_origin": "PERSONAL_PROPERTY",
                    "creditor": "BNP Paribas",
                    "initial_amount": 80000,
                    "remaining_balance": 50000
                }
            ]
        }
    },
    {
        "name": "🏠 Dettes - Hypothèque sur bien immobilier",
        "description": "Maison avec hypothèque liée (emprunt immobilier)",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2005-06-15",
            "assets": [
                {
                    "id": "maison_principale",
                    "estimated_value": 500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2010-03-20"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1975-08-12", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "2006-05-10", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "QUARTER_OWNERSHIP"
                }
            },
            "debts": [
                {
                    "id": "hypotheque",
                    "amount": 200000,
                    "debt_type": "emprunt immobilier",
                    "is_deductible": True,
                    "linked_asset_id": "maison_principale",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "creditor": "BNP Paribas",
                    "initial_amount": 400000,
                    "remaining_balance": 200000
                }
            ]
        }
    },
    {
        "name": "📊 Dettes multiples - Hypothèque + crédit + impôts",
        "description": "Plusieurs types de dettes déductibles",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2000-03-10",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 600000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2008-09-15"
                },
                {
                    "id": "voiture",
                    "estimated_value": 30000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1970-05-10", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "2001-08-15", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "2004-11-22", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "USUFRUCT"
                }
            },
            "debts": [
                {
                    "id": "hypotheque_residence",
                    "amount": 250000,
                    "debt_type": "emprunt immobilier",
                    "is_deductible": True,
                    "linked_asset_id": "residence",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "creditor": "Crédit Agricole"
                },
                {
                    "id": "credit_auto",
                    "amount": 15000,
                    "debt_type": "crédit auto",
                    "is_deductible": True,
                    "asset_origin": "PERSONAL_PROPERTY",
                    "creditor": "PSA Finance"
                },
                {
                    "id": "impots_dus",
                    "amount": 8000,
                    "debt_type": "impôts",
                    "is_deductible": True,
                    "asset_origin": "PERSONAL_PROPERTY",
                    "creditor": "Direction Générale des Finances Publiques"
                },
                {
                    "id": "frais_funeraires",
                    "amount": 5000,
                    "debt_type": "frais funéraires",
                    "is_deductible": True,
                    "asset_origin": "PERSONAL_PROPERTY",
                    "description": "Frais d'obsèques"
                }
            ]
        }
    }
]

for scenario in scenarios:
    if not SimulationScenario.objects.filter(name=scenario["name"]).exists():
        SimulationScenario.objects.create(**scenario)
        print(f"✅ Créé: {scenario['name']}")
    else:
        SimulationScenario.objects.filter(name=scenario["name"]).update(
            description=scenario["description"],
            input_data=scenario["input_data"]
        )
        print(f"🔄 Mis à jour: {scenario['name']}")

print(f"\n📊 Total scénarios: {SimulationScenario.objects.count()}")
print("\n💡 Scénarios dettes ajoutés:")
print("  - Crédit à la consommation simple")
print("  - Hypothèque liée à un bien (linked_asset_id)")
print("  - Multi-dettes (hypothèque + crédit + impôts + funérailles)")
print("\n📋 Impact:")
print("  Masse successorale = Actif brut + Donations - Dettes déductibles")
