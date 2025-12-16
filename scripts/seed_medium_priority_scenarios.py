import os
import django
import sys

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

scenarios = [
    # ==================== USUFRUCT VALUATION ====================
    {
        "name": "📊 Valorisation usufruit - Conjoint 65 ans",
        "description": "Conjoint usufruit à 65 ans → taux 40% (Art. 669 CGI)",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1980-06-15",
            "assets": [
                {
                    "id": "patrimoine",
                    "estimated_value": 1000000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1960-03-20", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1985-05-10", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1988-08-22", "relationship": "CHILD"}
            ],
            "wishes": {
                "spouse_choice": {"choice": "USUFRUCT"},
                "has_spouse_donation": False
            }
        }
    },
    {
        "name": "📊 Valorisation usufruit - Conjoint 80 ans",
        "description": "Conjoint usufruit à 80 ans → taux 30% (Art. 669 CGI)",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1965-04-10",
            "assets": [
                {
                    "id": "patrimoine",
                    "estimated_value": 800000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1945-06-12", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1970-02-28", "relationship": "CHILD"}
            ],
            "wishes": {
                "spouse_choice": {"choice": "USUFRUCT"},
                "has_spouse_donation": False
            }
        }
    },
    
    # ==================== REDUCTION ====================
    {
        "name": "💰 Libéralités excessives - Action en réduction",
        "description": "Donations + legs dépassent quotité disponible → réduction possible",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "patrimoine",
                    "estimated_value": 300000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1990-03-15", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1992-07-20", "relationship": "CHILD"}
            ],
            "donations": [
                {
                    "id": "don_ami",
                    "donation_type": "don_manuel",
                    "beneficiary_name": "Ami",
                    "beneficiary_heir_id": "ami",
                    "beneficiary_relationship": "OTHER",
                    "donation_date": "2022-05-15",
                    "original_value": 100000,
                    "is_declared_to_tax": True
                }
            ],
            "wishes": {
                "specific_bequests": [
                    {"asset_id": "patrimoine", "beneficiary_id": "charity", "share_percentage": 30}
                ],
                "has_spouse_donation": False
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
