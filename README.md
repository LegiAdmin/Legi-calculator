# 🏛️ Succession Engine

[![Tests CI/CD](https://github.com/LegiAdmin/Legi-calculator/actions/workflows/tests.yml/badge.svg)](https://github.com/LegiAdmin/Legi-calculator/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/LegiAdmin/Legi-calculator/branch/main/graph/badge.svg)](https://codecov.io/gh/LegiAdmin/Legi-calculator)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)

> Moteur de calcul de succession français — Simulation fiscale, dévolution légale, et explicabilité complète.

## 🚀 Fonctionnalités

- **Calcul fiscal** : Droits de succession selon barèmes 2025
- **Dévolution légale** : Art. 913+ Code civil
- **Explicabilité** : Chaque étape documentée avec base légale
- **API REST** : Endpoints pour simulation et scénarios
- **Tests E2E** : 25 scénarios golden validés

## 📦 Installation

```bash
# Cloner le repo
git clone https://github.com/LegiAdmin/Legi-calculator.git
cd Legi-calculator

# Environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Dépendances
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Seed législation 2025
python manage.py shell < scripts/seed_legislation_2025.py

# Lancer le serveur
python manage.py runserver
```

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/unit/ -v

# Tests E2E (golden scenarios)
pytest tests/test_golden.py -v

# Tous les tests avec coverage
pytest --cov=succession_engine --cov-report=term-missing

# Régénérer les expected_output (snapshot)
python manage.py regenerate_golden_scenarios --dry-run
```

## 🏗️ Architecture

```
succession_engine/
├── core/
│   ├── calculator.py      # Orchestrateur principal
│   ├── devolution.py      # Calcul des parts héritiers
│   └── liquidation.py     # Liquidation régime matrimonial
├── rules/
│   ├── fiscal.py          # Calcul droits de succession
│   └── usufruct.py        # Valorisation usufruit (Art. 669 CGI)
├── services/
│   └── explainer.py       # Enrichissement explicabilité
├── data/
│   └── rule_dictionary.json  # Dictionnaire des règles FR
└── api/
    └── views.py           # Endpoints REST
```

## 📋 API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/simulate/` | POST | Lancer une simulation |
| `/api/scenarios/` | GET/POST | Gérer les scénarios |
| `/api/golden-scenarios/` | GET | Récupérer les scénarios de test |
| `/simulator/` | GET | Interface web de simulation |

## 📚 Documentation

- [Spécification Tests](docs/TEST_SPECIFICATION.md)
- [Analyse Technico-Légale](docs/ANALYSE_TECHNICO_LEGALE.md)

## 📄 Licence

Propriétaire - Tous droits réservés.
