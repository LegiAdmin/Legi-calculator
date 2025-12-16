import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

scenarios = [
    {
        "name": "💍 Liquidation - Communauté légale",
        "description": "Couple marié en communauté avec biens propres et communs",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2000-06-15",
            "assets": [
                {
                    "id": "maison",
                    "estimated_value": 400000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY", 
                    "acquisition_date": "2005-10-20"  # Après mariage
                },
                {
                    "id": "heritage_defunt",
                    "estimated_value": 100000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"  # Bien propre du défunt
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "2002-03-10", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "👫 Option conjoint - Usufruit total",
        "description": "Conjoint choisit l'usufruit, enfants ont nue-propriété",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1995-05-20",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2000-03-15"
                }
            ],
            "members": [
                {"id": "conjoint", "birth_date": "1965-08-12", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1996-06-10", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1998-09-22", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "USUFRUCT"
                }
            }
        }
    },
    {
        "name": "🏠 Option conjoint - 1/4 Pleine Propriété",
        "description": "Conjoint choisit 1/4 en PP, enfants se partagent les 3/4",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1998-04-10",
            "assets": [
                {
                    "id": "maison",
                    "estimated_value": 600000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2005-07-20"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1968-03-15", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1999-05-12", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "2001-08-20", "relationship": "CHILD"}
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
        "name": "💔 Séparation de biens",
        "description": "Régime de séparation - chaque bien appartient à son propriétaire",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "marriage_date": "2010-09-12",
            "assets": [
                {
                    "id": "appartement_defunt",
                    "estimated_value": 350000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"  # Bien propre
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "2011-06-10", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "2013-11-15", "relationship": "CHILD"}
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
print("\n💡 Scénarios ajoutés:")
print("  - Liquidation communauté légale (biens propres vs communs)")
print("  - Option conjoint : usufruit total")
print("  - Option conjoint : 1/4 pleine propriété")
print("  - Séparation de biens")
