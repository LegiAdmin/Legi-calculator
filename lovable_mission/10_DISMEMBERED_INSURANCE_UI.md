# 10 - Clause Bénéficiaire Démembrée (Assurance-Vie)

## Contexte Légal
Un contrat d'assurance-vie peut avoir une clause bénéficiaire démembrée :
- **"Usufruit à mon conjoint, nue-propriété à mes enfants"**
- Le conjoint usufruitier perçoit les revenus du capital
- Les enfants nus-propriétaires reçoivent le capital au décès de l'usufruitier

---

## Fiscalité

| Bénéficiaire | Ce qu'il reçoit | Taxation |
|--------------|-----------------|----------|
| Conjoint (usufruit) | Valeur usufruit | **Exonéré** (Art. 796 CGI) |
| Enfants (NP) | Valeur nue-propriété | Art. 990 I / 757 B CGI |

La valorisation usufruit/NP utilise le barème Art. 669 CGI selon l'âge du conjoint.

---

## UI - Formulaire Assurance-Vie

### Champ existant à modifier
Dans les assets de type assurance-vie, ajouter une section "Bénéficiaires" :

```typescript
interface LifeInsuranceBeneficiary {
  beneficiary_id: string;     // Lien vers FamilyMember.id
  share_percent: number;       // default: 100
  ownership_type: 'FULL_OWNERSHIP' | 'USUFRUCT' | 'BARE_OWNERSHIP';
  birth_date?: Date;           // Pour valorisation usufruit
}
```

### Composants UI

#### Section "Bénéficiaires désignés"

```
┌────────────────────────────────────────────────────────────┐
│ 👥 Bénéficiaires du contrat                                │
│                                                             │
│ ┌─ Bénéficiaire 1 ────────────────────────────────────────┐│
│ │ Membre : [Select: conjoint/enfants]                     ││
│ │ Part : [100%]                                           ││
│ │ Type de propriété : [Pleine propriété ▼]                ││
│ │   ○ Pleine propriété                                    ││
│ │   ○ Usufruit                                            ││
│ │   ○ Nue-propriété                                       ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ [+ Ajouter un bénéficiaire]                                │
└────────────────────────────────────────────────────────────┘
```

### Template Clause Démembrée
Bouton "Utiliser clause démembrée standard" qui pré-remplit :
- Conjoint → Usufruit 100%
- Enfants → Nue-propriété (divisé équitablement)

---

## Validation

1. La somme des parts en pleine propriété = 100%
2. OU la somme usufruit = 100% ET somme NP = 100%
3. Si usufruit, date de naissance obligatoire (pour valorisation)

---

## API Payload

```json
{
  "assets": [
    {
      "id": "av1",
      "estimated_value": 200000,
      "premiums_before_70": 150000,
      "premiums_after_70": 50000,
      "life_insurance_beneficiaries": [
        {
          "beneficiary_id": "spouse",
          "share_percent": 100,
          "ownership_type": "USUFRUCT",
          "birth_date": "1960-05-15"
        },
        {
          "beneficiary_id": "child1",
          "share_percent": 50,
          "ownership_type": "BARE_OWNERSHIP"
        },
        {
          "beneficiary_id": "child2",
          "share_percent": 50,
          "ownership_type": "BARE_OWNERSHIP"
        }
      ]
    }
  ]
}
```

---

## Résultat attendu
Dans les résultats de simulation :
- Ligne distincte pour conjoint (usufruit, 0€ de droits car exonéré)
- Lignes pour chaque enfant (NP, avec abattement 152 500€ Art. 990 I)
