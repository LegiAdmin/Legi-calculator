# Dictionnaire des Alertes Contextualisées

Ce document définit les alertes que le calculateur peut émettre et où elles doivent être affichées dans l'interface.

---

## Structure des Alertes

```typescript
interface Alert {
  key: string;           // Identifiant unique
  severity: "INFO" | "WARNING" | "ERROR";
  message: string;       // Message court
  context?: Record<string, any>;  // Données supplémentaires
}
```

---

## Niveau GLOBAL (`global_metrics.alerts`)

Alertes concernant la succession dans son ensemble.

| Key | Severity | Message | Context | Quand |
|-----|----------|---------|---------|-------|
| `INTERNATIONAL_ASSETS` | WARNING | Patrimoine international détecté | `{countries: string[]}` | Un actif est situé hors France |
| `NO_HEIRS` | ERROR | Aucun héritier déclaré | - | Liste `family_members` vide |
| `RESERVE_GLOBAL_VIOLATION` | WARNING | La réserve héréditaire n'est pas respectée | `{reserve: number, actual_to_reserve: number}` | Les legs/donations dépassent la quotité disponible |
| `USUFRUCT_OPTION_REQUIRED` | INFO | Le conjoint doit choisir son option successorale | `{options: string[]}` | Conjoint + enfants présents |
| `PRECIPUT_DETECTED` | INFO | Un préciput matrimonial a été appliqué | `{value: number}` | Clause de préciput active |
| `DEBTS_EXCEED_ASSETS` | ERROR | Les dettes dépassent l'actif successoral | `{debts: number, assets: number}` | Passif > Actif |

---

## Niveau HÉRITIER (`heirs_breakdown[].alerts`)

Alertes concernant un héritier spécifique.

| Key | Severity | Message | Context | Quand |
|-----|----------|---------|---------|-------|
| `RESERVE_HEIR_VIOLATION` | WARNING | Cet héritier reçoit moins que sa réserve | `{expected: number, actual: number, shortfall: number}` | Part reçue < réserve individuelle |
| `EXCLUDED_BY_ORDER` | INFO | Cet héritier est exclu par l'ordre successoral | `{reason: string}` | Ex: neveu exclu par présence enfants |
| `RENUNCIATION` | INFO | Cet héritier a renoncé à la succession | - | `acceptance_option = RENUNCIATION` |
| `ADOPTION_SIMPLE_TAX` | WARNING | Taxation majorée (adoption simple) | `{rate: number}` | Adoption simple sans soins continus |
| `DISABILITY_ALLOWANCE` | INFO | Abattement handicap appliqué | `{bonus: number}` | `is_disabled = true` |
| `ALLOWANCE_EXHAUSTED` | WARNING | Abattement épuisé par donations antérieures | `{used: number, remaining: number}` | Rappel fiscal 15 ans consomme l'abattement |
| `REPRESENTATION` | INFO | Cet héritier représente un héritier prédécédé | `{represented_id: string}` | Petits-enfants représentant parent décédé |
| `HIGH_TAX_RATE` | WARNING | Taux d'imposition élevé | `{effective_rate: number}` | Taux effectif > 40% |
| `BEQUEST_RECEIVED` | INFO | Legs particulier reçu | `{asset_id: string, asset_name: string}` | Héritier est bénéficiaire d'un legs |

---

## Niveau ACTIF (`assets_breakdown[].alerts`)

Alertes concernant un actif spécifique.

| Key | Severity | Message | Context | Quand |
|-----|----------|---------|---------|-------|
| `RESIDENCE_DISCOUNT` | INFO | Abattement résidence principale appliqué | `{discount: number, original: number}` | `is_main_residence = true` |
| `LIFE_INSURANCE_EXEMPT` | INFO | Assurance-vie exonérée | `{reason: string}` | Primes < seuil ou bénéficiaire exonéré |
| `LIFE_INSURANCE_TAXED` | WARNING | Assurance-vie soumise à taxation | `{tax: number}` | Primes après 70 ans > 30 500€ |
| `DUTREIL_APPLIED` | INFO | Pacte Dutreil appliqué | `{exemption: number}` | Entreprise avec pacte Dutreil |
| `MIXED_OWNERSHIP` | INFO | Bien en indivision | `{ownership_percent: number}` | `ownership_mode = INDIVISION` |
| `DONATED_ASSET` | INFO | Bien objet de donation antérieure | `{donation_date: string, value: number}` | Actif provient d'une donation rapportable |
| `DROIT_DE_RETOUR` | INFO | Droit de retour applicable | `{returning_to: string}` | Bien revient au parent donateur |
| `DISMEMBERMENT` | INFO | Bien démembré | `{usufruct_holder: string, bare_owner: string}` | NP/Usufruit séparés |

---

## Implémentation Frontend

### Affichage suggéré

1. **GLOBAL** : Bannière en haut des résultats
2. **HÉRITIER** : Badge/icône à côté du nom de l'héritier, avec tooltip ou encart
3. **ACTIF** : Badge/icône sur la ligne de l'actif

### Couleurs par sévérité

- `INFO` : Bleu/Gris
- `WARNING` : Orange/Jaune  
- `ERROR` : Rouge

### Exemple d'affichage héritier

```
┌────────────────────────────────────────┐
│ 👤 Marie Dupont                    ⚠️  │
│ Part nette: 125 000 €                  │
│ Droits: 8 500 €                        │
│ ┌──────────────────────────────────┐   │
│ │ ⚠️ Reçoit moins que sa réserve   │   │
│ │ Attendu: 150 000 € | Reçu: 125k  │   │
│ └──────────────────────────────────┘   │
└────────────────────────────────────────┘
```
