import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

# Clear existing scenarios
SimulationScenario.objects.all().delete()

scenarios = [
    {
        "name": "🏠 Marié - 2 enfants - Résidence principale",
        "description": "Couple marié en communauté avec 2 enfants, résidence principale de 400k€",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2000-06-15",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 400000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "2005-03-12", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "2008-09-20", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "💼 Séparation de biens - 1 enfant - Patrimoine important",
        "description": "Séparation de biens, 1 enfant, patrimoine personnel de 800k€",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "marriage_date": "1995-04-10",
            "assets": [
                {
                    "id": "immobilier",
                    "estimated_value": 500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "portefeuille",
                    "estimated_value": 300000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1998-11-05", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "SPOUSE_ALL"
            }
        }
    },
    {
        "name": "👨‍👩‍👧‍👦 Famille recomposée - 3 enfants",
        "description": "Marié, 1 enfant de précédente union + 2 enfants du couple actuel",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2010-02-14",
            "assets": [
                {
                    "id": "maison",
                    "estimated_value": 350000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "2002-05-10", "relationship": "CHILD", "is_from_current_union": False},
                {"id": "child2", "birth_date": "2012-08-15", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child3", "birth_date": "2015-03-22", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "🏡 Usufruit - Conjoint survivant",
        "description": "Résidence avec usufruit au conjoint, 2 enfants en nue-propriété",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1985-07-20",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 450000,
                    "ownership_mode": "BARE_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY",
                    "usufructuary_birth_date": "1960-03-15"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1988-12-10", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1992-06-18", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "💰 Assurance-vie - Primes après 70 ans",
        "description": "Patrimoine avec assurance-vie souscrite après 70 ans",
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
                    "id": "assurance_vie",
                    "estimated_value": 150000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "premiums_after_70": 100000,
                    "premiums_before_70": 50000,
                    "subscriber_type": "MOI"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1995-04-22", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1998-09-30", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "👤 Célibataire - 4 enfants - Legs spécifique",
        "description": "Célibataire avec 4 enfants, legs d'un bien à un enfant spécifique",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 250000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "appartement_paris",
                    "estimated_value": 400000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "epargne",
                    "estimated_value": 100000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1990-01-15", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1992-05-20", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child3", "birth_date": "1995-08-10", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child4", "birth_date": "1998-11-25", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "CUSTOM",
                "specific_bequests": [
                    {"asset_id": "appartement_paris", "beneficiary_id": "child1"}
                ]
            }
        }
    },
    {
        "name": "🏠 Indivision - Biens partagés",
        "description": "Biens en indivision, situation complexe",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2005-09-10",
            "assets": [
                {
                    "id": "maison_indivision",
                    "estimated_value": 500000,
                    "ownership_mode": "INDIVISION",
                    "asset_origin": "INDIVISION",
                    "community_funding_percentage": 60.0
                },
                {
                    "id": "epargne",
                    "estimated_value": 80000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "2008-03-18", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "2011-07-22", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "💑 PACS - Testament au profit du partenaire",
        "description": "Couple pacsé avec testament, 1 enfant",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 320000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "partner", "birth_date": "1980-06-10", "relationship": "PARTNER"},
                {"id": "child1", "birth_date": "2010-12-05", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "SPOUSE_ALL"
            }
        }
    },
    {
        "name": "👴 Parents âgés - 1 enfant unique",
        "description": "Succession simple avec un enfant unique, patrimoine modeste",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1970-05-12",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 200000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                },
                {
                    "id": "livret",
                    "estimated_value": 50000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1975-08-20", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "💼 Patrimoine important - 3 enfants - Diversifié",
        "description": "Patrimoine de 1,5M€ diversifié, 3 enfants",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1992-09-15",
            "assets": [
                {
                    "id": "residence_principale",
                    "estimated_value": 600000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                },
                {
                    "id": "residence_secondaire",
                    "estimated_value": 300000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                },
                {
                    "id": "portefeuille_actions",
                    "estimated_value": 400000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "assurance_vie",
                    "estimated_value": 200000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY",
                    "premiums_before_70": 200000,
                    "subscriber_type": "MOI"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1995-03-10", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1998-06-15", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child3", "birth_date": "2002-11-20", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "CHILDREN_ALL"
            }
        }
    }
]

print("🌱 Création des scénarios de test...")
for scenario_data in scenarios:
    scenario = SimulationScenario.objects.create(**scenario_data)
    print(f"  ✅ {scenario.name}")

print(f"\n✨ {len(scenarios)} scénarios créés avec succès !")
