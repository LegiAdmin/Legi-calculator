import os
import django
import sys

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

scenarios = [
    {
        "name": "🔀 Indivision avec conjoint - 65% conjoint / 35% défunt",
        "description": "Maison en indivision: conjoint détient 65%, défunt 35%",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2000-01-01",
            "assets": [
                {
                    "id": "maison_indivision",
                    "estimated_value": 500000,
                    "ownership_mode": "INDIVISION",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "acquisition_date": "2010-05-15",
                    "indivision_details": {
                        "withSpouse": True,
                        "spouseShare": 65.0,
                        "withOthers": False
                    }
                },
                {
                    "id": "compte_bancaire",
                    "estimated_value": 100000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1970-01-01", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "2000-06-01", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "2002-08-15", "relationship": "CHILD"}
            ]
        }
    },
    {
        "name": "🔀 Indivision avec tiers - 50% frère / 50% défunt",
        "description": "Appartement en indivision avec un frère (50/50)",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "appartement_indivision",
                    "estimated_value": 300000,
                    "ownership_mode": "INDIVISION",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "indivision_details": {
                        "withSpouse": False,
                        "withOthers": True,
                        "othersShare": 50.0,
                        "coOwners": ["Frère Jean"]
                    }
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1995-03-10", "relationship": "CHILD"}
            ]
        }
    },
    {
        "name": "🔀 Indivision complexe - Conjoint 40% + Autre 30% = Défunt 30%",
        "description": "Bien en indivision à 3: conjoint 40%, ami 30%, défunt 30%",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1995-06-20",
            "assets": [
                {
                    "id": "immeuble_commercial",
                    "estimated_value": 1000000,
                    "ownership_mode": "INDIVISION",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "indivision_details": {
                        "withSpouse": True,
                        "spouseShare": 40.0,
                        "withOthers": True,
                        "othersShare": 30.0,
                        "coOwners": ["Associé Martin"]
                    }
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1968-03-15", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1996-05-12", "relationship": "CHILD"}
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
print("\n💡 Scénarios indivision ajoutés:")
print("  - Indivision avec conjoint (65/35)")
print("  - Indivision avec tiers (50/50)")
print("  - Indivision complexe à 3 (40/30/30)")
