import os
import django
import sys

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

scenarios = [
    {
        "name": "💰 Récompenses - Bien commun financé par fonds propres",
        "description": "Maison commune financée à 30% par héritage personnel du défunt",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2000-06-15",
            "assets": [
                {
                    "id": "maison_avec_recompense",
                    "estimated_value": 400000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2010-03-20",
                    "community_funding_percentage": 70  # 30% financé par fonds propres
                },
                {
                    "id": "appartement_loue",
                    "estimated_value": 200000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2015-09-10",
                    "community_funding_percentage": 100  # Entièrement financé par communauté
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
                    "choice": "QUARTER_OWNERSHIP"
                }
            }
        }
    },
    {
        "name": "🏡 Récompenses multiples - Plusieurs biens",
        "description": "Plusieurs biens avec financements mixtes",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1995-03-10",
            "assets": [
                {
                    "id": "residence_principale",
                    "estimated_value": 500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2005-06-15",
                    "community_funding_percentage": 60  # 40% fonds propres
                },
                {
                    "id": "residence_secondaire",
                    "estimated_value": 300000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "acquisition_date": "2012-04-20",
                    "community_funding_percentage": 80  # 20% fonds propres
                },
                {
                    "id": "heritage_defunt",
                    "estimated_value": 150000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"  # Bien propre, pas de récompense
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1968-08-12", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1996-05-10", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL",
                "spouse_choice": {
                    "choice": "USUFRUCT"
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
print("\n💡 Scénarios récompenses matrimoniales ajoutés:")
print("  - Bien commun avec 30% fonds propres")
print("  - Multiples biens avec financements mixtes")
print("\n📋 Logique:")
print("  Si community_funding_percentage < 100%:")
print("    → Récompense = valeur × (100% - community_funding%)")
print("    → Ajustement parts défunt/conjoint")
