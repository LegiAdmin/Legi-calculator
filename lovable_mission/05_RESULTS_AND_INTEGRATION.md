# Mission Lovable - Comprendre et Afficher les Résultats de l'API

Ce document t'explique **ce que l'API renvoie** après un calcul de succession. Ton objectif est de créer une section de résultats visuelle, moderne et pédagogique. Tu as carte blanche pour l'UX/UI.

---

## CE QUE L'API RENVOIE (`SuccessionOutput`)

Voici la structure complète de la réponse. Chaque bloc contient des données que tu peux exploiter pour informer l'utilisateur.

### 1. `global_metrics` — Vue d'Ensemble
```json
{
  "total_estate_value": 500000,      // Masse successorale nette
  "legal_reserve_value": 250000,     // Part réservée aux héritiers réservataires
  "disposable_quota_value": 250000,  // Part librement transmissible
  "total_tax_amount": 45000,         // Total des droits de succession
  "explanation_keys": [...]          // Clés d'explication (voir section dédiée)
}
```
**Ce que ça signifie** : Les grands chiffres de la succession. L'utilisateur veut savoir "Combien ?", "Combien d'impôts ?", "Combien de liberté j'ai ?".

---

### 2. `heirs_breakdown` — Détail par Héritier
```json
{
  "id": "Paul",
  "name": "Héritier Paul",
  "legal_share_percent": 50.0,       // % de la succession
  "gross_share_value": 250000,       // Valeur brute reçue
  "taxable_base": 150000,            // Base après abattements
  "abatement_used": 100000,          // Abattement appliqué
  "tax_amount": 28000,               // Impôt dû par cet héritier
  "net_share_value": 222000,         // Ce qu'il touche vraiment

  "received_assets": [               // Biens spécifiques reçus (legs)
    { "asset_id": "Maison", "share_percentage": 100, "value": 200000 }
  ],

  "tax_calculation_details": {       // Détail du calcul fiscal
    "relationship": "CHILD",
    "allowance_name": "Abattement ligne directe",
    "allowance_amount": 100000,
    "brackets_applied": [            // Tranches fiscales
      { "rate": 0.05, "taxable_in_bracket": 8072, "tax_for_bracket": 403 },
      { "rate": 0.10, "taxable_in_bracket": 4037, "tax_for_bracket": 403 },
      { "rate": 0.15, "taxable_in_bracket": 3823, "tax_for_bracket": 573 },
      { "rate": 0.20, "taxable_in_bracket": 134068, "tax_for_bracket": 26813 }
    ]
  },

  "explanation_keys": [              // Pourquoi ces chiffres ?
    { "key": "SHARE_CHILDREN_EQUAL", "context": { "num_children": 2 } },
    { "key": "ABATEMENT_CHILD_100K", "context": { "amount": 100000 } }
  ]
}
```
**Ce que ça signifie** : Chaque héritier a sa "fiche". L'utilisateur veut comprendre : "Pourquoi Paul reçoit ça ?", "Pourquoi il paie autant d'impôts ?".

---

### 3. `alerts` — Alertes et Avertissements
```json
{
  "severity": "WARNING",      // INFO, WARNING, CRITICAL
  "audience": "USER",         // USER (simple), NOTARY (expert)
  "category": "LEGAL",        // LEGAL, FISCAL, DATA, OPTIMIZATION
  "message": "Bien sur-alloué", 
  "details": "Le bien 'Maison' est distribué à 120%."
}
```
**Ce que ça signifie** : Le moteur a détecté quelque chose à signaler. Peut être une erreur de saisie, un risque juridique, ou une opportunité d'optimisation.

---

### 4. `liquidation_details` — Régime Matrimonial
```json
{
  "regime": "COMMUNITY_LEGAL",
  "community_assets_total": 400000,
  "spouse_community_share": 200000,  // Part du conjoint (hors succession)
  "deceased_community_share": 200000,
  "has_preciput": true,
  "preciput_value": 150000,          // Clause de préciput appliquée
  "explanation_keys": [...]
}
```
**Ce que ça signifie** : Avant de partager, on "liquide" le régime matrimonial. Le conjoint reprend sa part des biens communs.

---

### 5. `spouse_details` — Option du Conjoint
```json
{
  "has_usufruct": true,
  "usufruct_value": 120000,
  "usufruct_rate": 40,              // % selon âge (barème Art. 669 CGI)
  "choice_made": "USUFRUCT"
}
```
**Ce que ça signifie** : Le conjoint a souvent un choix à faire (Usufruit vs Propriété). Ces chiffres montrent l'option retenue.

---

### 6. `calculation_steps` — Étapes du Calcul
```json
{
  "step_number": 1,
  "step_name": "Liquidation du régime matrimonial",
  "description": "Calcul de la part communautaire...",
  "result_summary": "Part du défunt: 200 000€"
}
```
**Ce que ça signifie** : Pour les utilisateurs curieux (ou les notaires), le moteur montre comment il a calculé, étape par étape.

---

## LES CLÉS D'EXPLICATION (`explanation_keys`)

Plutôt que des textes bruts, l'API renvoie des **clés structurées**. C'est à toi de les transformer en textes humains.

### Exemple de clé :
```json
{ "key": "SHARE_CHILDREN_EQUAL", "context": { "num_children": 2 } }
```

### Dictionnaire de traduction (à créer) :
```typescript
const explanations = {
  SHARE_CHILDREN_EQUAL: (ctx) => `Partage égal entre ${ctx.num_children} enfant(s).`,
  ABATEMENT_CHILD_100K: (ctx) => `Abattement de ${ctx.amount.toLocaleString()}€ (Art. 779 CGI).`,
  TAX_SPOUSE_EXEMPT: () => `Le conjoint survivant est exonéré de droits.`,
  // ... autres clés
};
```

### Clés actuellement supportées :
- **Répartition** : `SHARE_CHILDREN_EQUAL`, `SHARE_SPOUSE`, `SHARE_REPRESENTATION`, `SHARE_SIBLINGS`
- **Abattements** : `ABATEMENT_CHILD_100K`, `ABATEMENT_SIBLING_15K`, `ABATEMENT_DISABILITY_159K`, `ABATEMENT_CONSUMED_15Y`
- **Fiscalité** : `TAX_SPOUSE_EXEMPT`
- **Liquidation** : `LIQUIDATION_COMMUNITY_50`, `LIQUIDATION_PRECIPUT`

---

## OBJECTIF DE LA SECTION RÉSULTATS

L'utilisateur doit pouvoir :
1. **Voir en un coup d'œil** combien chaque héritier reçoit et paie.
2. **Comprendre pourquoi** grâce aux explications (infobulles, notes...).
3. **Identifier les problèmes** via les alertes (quotité dépassée, données incohérentes...).
4. **Visualiser les biens reçus** (legs particuliers).

---

## APPEL API

**Endpoint** : `POST /api/simulate/`  
**Body** : `SimulationInput` (voir `00_MASTER_CONTEXT_API.md`)  
**Auth** : `Authorization: Bearer <TOKEN>`

La réponse est le `SuccessionOutput` décrit ci-dessus.
