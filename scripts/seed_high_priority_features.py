"""
Test scenarios for high priority features:
1. Representation (grandchildren representing deceased parent)
2. Main residence 20% allowance
"""

import os
import sys
import django

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

scenarios = [
    # ==================== REPRESENTATION ====================
    {
        "name": "👶 Représentation - 2 petits-enfants représentent 1 parent décédé",
        "description": "Défunt a 2 enfants: A (vivant) et B (décédé). B a 2 enfants qui le représentent.",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "patrimoine",
                    "estimated_value": 600000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                # Enfant A (vivant)
                {"id": "child_A", "birth_date": "1975-03-15", "relationship": "CHILD"},
                # Petits-enfants représentant enfant B (décédé)
                {"id": "grandchild_B1", "birth_date": "2000-05-20", "relationship": "GRANDCHILD", "represented_heir_id": "deceased_child_B"},
                {"id": "grandchild_B2", "birth_date": "2002-08-10", "relationship": "GRANDCHILD", "represented_heir_id": "deceased_child_B"}
            ],
            "wishes": {
                "spouse_choice": None,
                "has_spouse_donation": False
            }
        }
    },
    {
        "name": "👶 Représentation avec conjoint - Usufruit + petits-enfants",
        "description": "Conjoint en usufruit, 2 souches: enfant A et 2 petits-enfants représentant enfant B",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1970-06-20",
            "assets": [
                {
                    "id": "patrimoine",
                    "estimated_value": 800000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1950-01-01", "relationship": "SPOUSE"},
                {"id": "child_A", "birth_date": "1975-03-15", "relationship": "CHILD"},
                {"id": "grandchild_B1", "birth_date": "2000-05-20", "relationship": "GRANDCHILD", "represented_heir_id": "deceased_child_B"},
                {"id": "grandchild_B2", "birth_date": "2002-08-10", "relationship": "GRANDCHILD", "represented_heir_id": "deceased_child_B"}
            ],
            "wishes": {
                "spouse_choice": {"choice": "USUFRUCT"},
                "has_spouse_donation": False
            }
        }
    },
    
    # ==================== RESIDENCE PRINCIPALE ====================
    {
        "name": "🏠 Abattement résidence principale 20%",
        "description": "Résidence principale 500k€ avec conjoint occupant → abattement 20% = 400k€ valorisé",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1980-05-10",
            "assets": [
                {
                    "id": "residence_principale",
                    "estimated_value": 500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "is_main_residence": True,
                    "spouse_occupies_property": True
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1955-03-20", "relationship": "SPOUSE"},
                {"id": "child1", "birth_date": "1985-06-15", "relationship": "CHILD"}
            ],
            "wishes": {
                "spouse_choice": {"choice": "QUARTER_OWNERSHIP"},
                "has_spouse_donation": False
            }
        }
    },
    {
        "name": "🏠 Résidence principale sans abattement (pas de conjoint occupant)",
        "description": "Résidence principale sans conjoint occupant → pas d'abattement 20%",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "residence_principale",
                    "estimated_value": 500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "is_main_residence": True,
                    "spouse_occupies_property": False
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1985-06-15", "relationship": "CHILD"},
                {"id": "child2", "birth_date": "1988-09-22", "relationship": "CHILD"}
            ],
            "wishes": {
                "spouse_choice": None,
                "has_spouse_donation": False
            }
        }
    },
    
    # ==================== COMBINAISON ====================
    {
        "name": "🔄 Représentation + Résidence principale + Indivision",
        "description": "Test complet: résidence en indivision (60% défunt), abattement 20%, 3 petits-enfants représentant 1 enfant",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1975-03-10",
            "assets": [
                {
                    "id": "residence_principale",
                    "estimated_value": 600000,
                    "ownership_mode": "INDIVISION",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "is_main_residence": True,
                    "spouse_occupies_property": True,
                    "indivision_details": {
                        "withSpouse": True,
                        "spouseShare": 40.0
                    }
                },
                {
                    "id": "placements",
                    "estimated_value": 200000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "spouse", "birth_date": "1952-07-15", "relationship": "SPOUSE"},
                {"id": "child_A", "birth_date": "1980-02-10", "relationship": "CHILD"},
                {"id": "grandchild_B1", "birth_date": "2005-01-15", "relationship": "GRANDCHILD", "represented_heir_id": "deceased_child_B"},
                {"id": "grandchild_B2", "birth_date": "2007-04-20", "relationship": "GRANDCHILD", "represented_heir_id": "deceased_child_B"},
                {"id": "grandchild_B3", "birth_date": "2010-08-05", "relationship": "GRANDCHILD", "represented_heir_id": "deceased_child_B"}
            ],
            "wishes": {
                "spouse_choice": {"choice": "QUARTER_OWNERSHIP"},
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
