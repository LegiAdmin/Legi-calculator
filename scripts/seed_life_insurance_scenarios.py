import os
import django
import sys

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

scenarios = [
    {
        "name": "💰 Assurance-vie - Primes avant 70 ans",
        "description": "Contrat avec primes versées avant 70 ans (abattement 152.5k€ par bénéficiaire)",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 300000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "assurance_vie_1",
                    "estimated_value": 200000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "premiums_before_70": 200000,
                    "premiums_after_70": 0
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1990-05-10", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "👴 Assurance-vie - Primes après 70 ans",
        "description": "Contrat avec primes versées après 70 ans (abattement global 30.5k€)",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "appartement",
                    "estimated_value": 250000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "assurance_vie_senior",
                    "estimated_value": 100000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "premiums_before_70": 0,
                    "premiums_after_70": 100000
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1995-03-15", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1998-07-20", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "🎯 Assurance-vie mixte - Avant et après 70 ans",
        "description": "Contrat avec primes avant ET après 70 ans (fiscalités différentes)",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1985-06-15",
            "assets": [
                {
                    "id": "maison",
                    "estimated_value": 400000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "1995-03-20"
                },
                {
                    "id": "assurance_vie_mixte",
                    "estimated_value": 300000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "premiums_before_70": 200000,  # Avant 70 ans
                    "premiums_after_70": 100000     # Après 70 ans
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1960-08-12", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1986-04-10", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1989-09-22", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "QUARTER_OWNERSHIP"
                }
            }
        }
    },
    {
        "name": "💎 Gros contrat - Au-delà des abattements",
        "description": "Contrat important (500k€) dépassant largement les abattements",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 600000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "assurance_vie_importante",
                    "estimated_value": 500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "premiums_before_70": 500000,
                    "premiums_after_70": 0
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1985-06-12", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL"
            }
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
print("\n💡 Scénarios assurance-vie ajoutés:")
print("  - Primes avant 70 ans (abattement 152.5k€)")
print("  - Primes après 70 ans (abattement 30.5k€)")
print("  - Mixte avant/après 70 ans")
print("  - Gros contrat dépassant abattements")
