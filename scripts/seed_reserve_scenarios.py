import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

# Scénarios pour tester les réserves et réductions

scenarios = [
    {
        "name": "⚖️ Réserve ascendants - 1 parent",
        "description": "Pas d'enfants, 1 parent vivant → réserve de 1/4",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {"id": "apt", "estimated_value": 200000, "ownership_mode": "FULL_OWNERSHIP", "asset_origin": "PERSONAL_PROPERTY"}
            ],
            "members": [
                {"id": "parent1", "birth_date": "1950-05-10", "relationship": "PARENT"}
            ],
            "wishes": {"has_spouse_donation": False, "testament_distribution": "LEGAL"}
        }
    },
    {
        "name": "⚖️ Réserve ascendants - 2 parents",
        "description": "Pas d'enfants, 2 parents vivants → réserve de 1/2 (1/4 chacun)",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {"id": "maison", "estimated_value": 300000, "ownership_mode": "FULL_OWNERSHIP", "asset_origin": "PERSONAL_PROPERTY"}
            ],
            "members": [
                {"id": "mother", "birth_date": "1950-03-15", "relationship": "PARENT"},
                {"id": "father", "birth_date": "1948-08-20", "relationship": "PARENT"}
            ],
            "wishes": {"has_spouse_donation": False, "testament_distribution": "LEGAL"}
        }
    },
    {
        "name": "🚨 Libéralités excessives - Violation réserve",
        "description": "Testament + donations dépassent la quotité disponible → réduction nécessaire",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {"id": "maison", "estimated_value": 400000, "ownership_mode": "FULL_OWNERSHIP", "asset_origin": "PERSONAL_PROPERTY"}
            ],
            "members": [
                {"id": "child1", "birth_date": "1990-05-10", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1992-08-15", "relationship": "CHILD"}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "CUSTOM",
                "custom_shares": [
                    {"beneficiary_id": "child1", "percentage": 90},
                    {"beneficiary_id": "child2", "percentage": 10}
                ]
            },
            "donations": [
                {
                    "id": "donation1",
                    "donation_type": "don_manuel",
                    "beneficiary_name": "Child1",
                    "beneficiary_heir_id": "child1",
                    "beneficiary_relationship": "CHILD",
                    "donation_date": "2020-01-15",
                    "original_value": 150000,
                    "current_estimated_value": 180000,
                    "is_declared_to_tax": True
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
