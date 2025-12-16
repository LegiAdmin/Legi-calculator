import os
import django
import sys

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

scenarios = [
    {
        "name": "💍 Donation au dernier vivant - Quotité disponible (1 enfant)",
        "description": "Conjoint choisit quotité disponible (1/2) grâce à donation au dernier vivant",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2000-06-15",
            "assets": [
                {
                    "id": "maison",
                    "estimated_value": 600000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2005-03-20"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1970-05-10", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "2001-08-15", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": True,  # Donation au dernier vivant
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "DISPOSABLE_QUOTA"  # Quotité disponible = 1/2
                }
            }
        }
    },
    {
        "name": "💍 Donation au dernier vivant - Quotité disponible (2 enfants)",
        "description": "Conjoint choisit quotité disponible (1/3) avec 2 enfants",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1998-04-10",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 900000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2003-09-15"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1968-03-15", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1999-05-12", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "2002-11-20", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "DISPOSABLE_QUOTA"  # Quotité disponible = 1/3
                }
            }
        }
    },
    {
        "name": "💍 Donation au dernier vivant - Quotité disponible (3 enfants)",
        "description": "Conjoint choisit quotité disponible (1/4) avec 3+ enfants",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1995-06-20",
            "assets": [
                {
                    "id": "patrimoine",
                    "estimated_value": 1200000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2000-05-10"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1965-08-12", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1996-03-10", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1998-07-15", "relationship": "CHILD"},
                {"id": "child3", "birth_date": "2001-11-22", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "DISPOSABLE_QUOTA"  # Quotité disponible = 1/4
                }
            }
        }
    },
    {
        "name": "⚖️ Comparaison - Sans donation (1/4 PP)",
        "description": "Même situation mais sans donation au dernier vivant - conjoint limité à 1/4",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2000-06-15",
            "assets": [
                {
                    "id": "maison",
                    "estimated_value": 600000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2005-03-20"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1970-05-10", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "2001-08-15", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,  # PAS de donation
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "QUARTER_OWNERSHIP"  # Limité à 1/4
                }
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
print("\n💡 Scénarios donation au dernier vivant ajoutés:")
print("  - Quotité disponible avec 1 enfant (1/2)")
print("  - Quotité disponible avec 2 enfants (1/3)")
print("  - Quotité disponible avec 3 enfants (1/4)")
print("  - Comparaison sans donation (1/4 max)")
print("\n📋 Impact:")
print("  Avec donation: conjoint peut recevoir jusqu'à 50% en PP")
print("  Sans donation: conjoint limité à 25% en PP")
