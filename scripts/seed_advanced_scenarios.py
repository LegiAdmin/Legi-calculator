import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import SimulationScenario

# Ne pas supprimer les scénarios existants, juste ajouter les nouveaux
print("🌱 Ajout de nouveaux scénarios de test avancés...")

new_scenarios = [
    {
        "name": "⚖️ Testament - Non-respect de la réserve légale",
        "description": "Testament tentant de donner 100% à un seul enfant alors qu'il y a 2 enfants (réserve 2/3)",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 300000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1990-05-10", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1993-08-15", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "CUSTOM",
                "specific_bequests": [
                    {"asset_id": "residence", "beneficiary_id": "child1", "share_percentage": 100}
                ]
            }
        }
    },
    {
        "name": "🚗 Patrimoine diversifié - Voiture de collection",
        "description": "Patrimoine avec voiture de collection, crypto et œuvres d'art",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "2000-03-15",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 400000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                },
                {
                    "id": "voiture_collection",
                    "estimated_value": 85000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "crypto_btc",
                    "estimated_value": 120000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "oeuvres_art",
                    "estimated_value": 65000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "2005-06-12", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "2008-11-20", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "CUSTOM",
                "specific_bequests": [
                    {"asset_id": "voiture_collection", "beneficiary_id": "child1"}
                ]
            }
        }
    },
    {
        "name": "💎 Legs spécifique - Bijoux et objets de valeur",
        "description": "Legs de bijoux à la fille, crypto au fils, résidence partagée",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "bijoux_famille",
                    "estimated_value": 45000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "crypto_portfolio",
                    "estimated_value": 180000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "daughter", "birth_date": "1995-03-10", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "son", "birth_date": "1998-07-22", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "CUSTOM",
                "specific_bequests": [
                    {"asset_id": "bijoux_famille", "beneficiary_id": "daughter"},
                    {"asset_id": "crypto_portfolio", "beneficiary_id": "son"}
                ]
            }
        }
    },
    {
        "name": "🏢 Entrepreneur - Parts sociales et patrimoine pro",
        "description": "Parts de société, fonds de commerce, véhicule professionnel",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "residence",
                    "estimated_value": 350000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "parts_societe",
                    "estimated_value": 450000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "fonds_commerce",
                    "estimated_value": 280000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "vehicule_pro",
                    "estimated_value": 55000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1990-01-15", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1992-09-20", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child3", "birth_date": "1995-04-10", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "CUSTOM",
                "specific_bequests": [
                    {"asset_id": "parts_societe", "beneficiary_id": "child1"},
                    {"asset_id": "fonds_commerce", "beneficiary_id": "child1"}
                ]
            }
        }
    },
    {
        "name": "🎨 Collectionneur - NFT et actifs numériques",
        "description": "Collection de NFT, crypto, domaines web et œuvres d'art numériques",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "appartement",
                    "estimated_value": 280000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "collection_nft",
                    "estimated_value": 95000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "crypto_eth",
                    "estimated_value": 145000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "domaines_web",
                    "estimated_value": 35000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "2000-05-12", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "LEGAL"
            }
        }
    },
    {
        "name": "⚠️ Partage inégal - Avantage à un héritier",
        "description": "Testament donnant 70% à un enfant et 30% à l'autre (dans la quotité disponible)",
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
                    "id": "placement_financier",
                    "estimated_value": 200000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1985-02-10", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1988-06-15", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "CUSTOM",
                "custom_shares": [
                    {"beneficiary_id": "child1", "percentage": 70},
                    {"beneficiary_id": "child2", "percentage": 30}
                ]
            }
        }
    },
    {
        "name": "🏎️ Luxe - Yacht, voitures, jet privé",
        "description": "Patrimoine de luxe avec différents types de véhicules et biens",
        "input_data": {
            "matrimonial_regime": "SEPARATION",
            "assets": [
                {
                    "id": "villa_principale",
                    "estimated_value": 2500000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "yacht",
                    "estimated_value": 850000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "ferrari",
                    "estimated_value": 380000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "jet_prive_parts",
                    "estimated_value": 1200000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "montres_collection",
                    "estimated_value": 220000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child1", "birth_date": "1992-03-15", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1995-08-22", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child3", "birth_date": "1998-11-10", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": False,
                "testament_distribution": "CUSTOM",
                "specific_bequests": [
                    {"asset_id": "ferrari", "beneficiary_id": "child1"},
                    {"asset_id": "yacht", "beneficiary_id": "child2"}
                ]
            }
        }
    },
    {
        "name": "🌾 Agriculteur - Terres, bâtiments, matériel",
        "description": "Exploitation agricole avec terres, bâtiments d'exploitation et matériel",
        "input_data": {
            "matrimonial_regime": "COMMUNITY_LEGAL",
            "marriage_date": "1995-06-20",
            "assets": [
                {
                    "id": "ferme_habitation",
                    "estimated_value": 320000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "COMMUNITY_PROPERTY"
                },
                {
                    "id": "terres_agricoles",
                    "estimated_value": 450000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "batiments_exploitation",
                    "estimated_value": 280000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "materiel_agricole",
                    "estimated_value": 185000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                },
                {
                    "id": "cheptel",
                    "estimated_value": 95000,
                    "ownership_mode": "FULL_OWNERSHIP",
                    "asset_origin": "PERSONAL_PROPERTY"
                }
            ],
            "members": [
                {"id": "child_farmer", "birth_date": "1996-04-15", "relationship": "CHILD", "is_from_current_union": True},
                {"id": "child2", "birth_date": "1999-09-20", "relationship": "CHILD", "is_from_current_union": True}
            ],
            "wishes": {
                "has_spouse_donation": True,
                "testament_distribution": "CUSTOM",
                "specific_bequests": [
                    {"asset_id": "terres_agricoles", "beneficiary_id": "child_farmer"},
                    {"asset_id": "batiments_exploitation", "beneficiary_id": "child_farmer"},
                    {"asset_id": "materiel_agricole", "beneficiary_id": "child_farmer"}
                ]
            }
        }
    }
]

created_count = 0
for scenario_data in new_scenarios:
    # Vérifier si le scénario existe déjà
    if not SimulationScenario.objects.filter(name=scenario_data["name"]).exists():
        scenario = SimulationScenario.objects.create(**scenario_data)
        print(f"  ✅ {scenario.name}")
        created_count += 1
    else:
        print(f"  ⏭️  {scenario_data['name']} (déjà existant)")

print(f"\n✨ {created_count} nouveaux scénarios créés !")
print(f"📊 Total dans la base : {SimulationScenario.objects.count()} scénarios")
