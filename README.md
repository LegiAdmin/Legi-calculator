# 🏛️ Antigravity Succession Engine (v2.0)

[![Tests Status](https://img.shields.io/badge/tests-81%20passing-brightgreen)]()
[![Chaos Verified](https://img.shields.io/badge/chaos%20scenarios-16%2F16%20verified-purple)]()
[![Code Coverage](https://img.shields.io/badge/coverage-92%25-green)]()
[![Legal Compliance](https://img.shields.io/badge/law-Code%20Civil%20%26%20CGI-blue)]()

> **"Code is Law"** — Le premier système expert Open Source de simulation successorale capable de gérer le chaos fiscal et familial.

---

## 🚀 Pourquoi ce moteur est différent ?

La plupart des calculateurs gèrent "un couple marié avec 2 enfants". 
**Antigravity** a été conçu pour les 5% de cas qui font mal à la tête des notaires.

### Fonctionnalités "Expert" (Chaos Ready)
- **🌍 International** : Gestion de l'obligation fiscale illimitée (Art. 750 Ter CGI).
- **💔 Fente Successorale** : Division paternelle/maternelle quand la famille est décimée (Art. 746 CC).
- **👨‍👩‍👧‍👦 Action en Retranchement** : Protection des enfants du premier lit contre une communauté universelle abusive (Art. 1527 CC).
- **⚰️ Droit de Retour** : Restitution des biens de famille aux parents en cas de décès sans descendance (Art. 738-2 CC).
- **🏦 Assurance-Vie Démembrée** : Calcul de l'usufruit/nue-propriété sur la clause bénéficiaire (Art. 669 CGI).

---

## 📚 Documentation Officielle

Ne lisez pas juste le code. Lisez notre **[White Paper Technique & Juridique](DOCUMENTATION_OFFICIELLE_MOTEUR.md)**.
Il explique pas à pas le "Pipeline en 5 Actes" qui garantit la justesse notariale.

---

## 🛠️ Installation & Usage

```bash
# 1. Cloner le moteur
git clone https://github.com/LegiAdmin/Legi-calculator.git
cd Legi-calculator

# 2. Setup Environnement
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Lancer les Tests "Golden" (Validation Métier)
pytest tests/test_golden.py -v
```

### Exemple d'Utilisation (Python)

```python
from succession_engine.api.client import SuccessionClient

# Simulation : Père avec 2 enfants, capital 1M€, Donation passée 200k
result = SuccessionClient.simulate({
    "assets": [{"id": "Maison", "value": 1000000}],
    "members": [{"role": "CHILD"}, {"role": "CHILD"}],
    "donations": [{"amount": 200000, "beneficiary": "Child1"}]
})

print(result.total_tax) # Calcul précis au centime près
```

---

## 🏗️ Architecture (Clean Code)

```
succession_engine/
├── core/
│   ├── calculator.py      # Chef d'orchestre (Pipeline)
│   ├── liquidation.py     # Acte 1 (Régimes Matrimoniaux)
│   └── devolution.py      # Acte 3 (Héritiers & Fente)
├── rules/
│   ├── fiscal.py          # Acte 5 (Impôts & Abattements)
│   ├── fente.py           # Logique rare (Art. 746 CC)
│   └── civil.py           # Règles civiles élémentaires
└── data/
    └── rule_dictionary.json  # Paramètres 2025 (Barèmes)
```

---

## 🛡️ License & Crédits

Propriété exclusive **Antigravity**. 
*Le code ne remplace pas le conseil d'un notaire.*
