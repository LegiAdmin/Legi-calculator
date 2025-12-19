# 08 - Renonciation Héritier UI

## Contexte
Un héritier peut renoncer à la succession (Art. 805+ Code civil). Dans ce cas, il est considéré comme n'ayant jamais été héritier et sa part accroît aux autres héritiers de même rang.

## Champs à ajouter dans FamilyMember

### Dans le formulaire d'ajout/édition de membre

```typescript
interface FamilyMemberForm {
  // ... champs existants ...
  
  // NOUVEAU: Section Renonciation
  has_renounced: boolean;  // default: false
  renunciation_date?: Date; // visible seulement si has_renounced = true
}
```

### UI Composants

#### Toggle "A renoncé à la succession"
- Position : En bas du formulaire FamilyMember
- Style : Toggle switch avec label
- Label : "Cet héritier a renoncé à la succession"
- Tooltip : "Un héritier qui renonce est exclu du partage. Sa part revient aux autres héritiers."

#### DatePicker "Date de renonciation" 
- Visible seulement si `has_renounced = true`
- Label : "Date de la renonciation"
- Format : DD/MM/YYYY
- Optionnel

---

## Comportement dans la liste des héritiers

### Affichage visuel
Si un héritier a `has_renounced = true` :

```
┌────────────────────────────────────────────┐
│  👤 Jean (Enfant)           ❌ A renoncé   │
│  ────────────────────────────────────────  │
│  Part : 0%                                 │
│  Renonciation : 15/01/2025                 │
└────────────────────────────────────────────┘
```

- Badge rouge "A renoncé" à côté du nom
- Ligne légèrement grisée (opacity: 0.6)
- Part affichée explicitement à 0%

---

## Dans les résultats de simulation

### Section Héritiers
L'héritier renonciataire doit apparaître dans les résultats avec :
- `legal_share_percent: 0`
- `gross_share_value: 0`
- Note explicative : "A renoncé à la succession (Art. 805 CC)"

### Alerte informative
Si au moins un héritier a renoncé, afficher une alerte INFO :
```
ℹ️ Renonciation prise en compte
Jean a renoncé à la succession. Sa part a été redistribuée 
aux autres héritiers de même rang.
```

---

## Validation

### Règles de validation
1. `renunciation_date` ne peut pas être dans le futur
2. `renunciation_date` doit être postérieure à la date de décès
3. Avertissement si tous les enfants renoncent (cas rare)

---

## API Payload

```json
{
  "members": [
    {
      "id": "enfant1",
      "relationship": "CHILD",
      "birth_date": "1990-01-01",
      "has_renounced": false
    },
    {
      "id": "enfant2",
      "relationship": "CHILD",  
      "birth_date": "1992-05-15",
      "has_renounced": true,
      "renunciation_date": "2025-01-15"
    }
  ]
}
```

---

## Supabase Schema

Ajouter dans la table `family_members` :
```sql
ALTER TABLE family_members 
ADD COLUMN has_renounced BOOLEAN DEFAULT FALSE,
ADD COLUMN renunciation_date DATE;
```
