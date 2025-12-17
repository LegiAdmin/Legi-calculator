# Mission Lovable - Référence : Dictionnaire d'Explications

Ce fichier liste toutes les **clés d'explication** renvoyées par l'API dans le champ `explanation_keys`.
Ton rôle est de maintenir un dictionnaire TypeScript qui mappe ces clés vers des textes humains.

---

## STRUCTURE DES CLÉS

Chaque clé est un objet :
```json
{
  "key": "SHARE_CHILDREN_EQUAL",
  "context": { "num_children": 2 }
}
```

- **`key`** : Identifiant unique (ex: `SHARE_CHILDREN_EQUAL`)
- **`context`** : Variables dynamiques à injecter dans le texte

---

## DICTIONNAIRE (À implémenter en `/src/lib/explanationDictionary.ts`)

```typescript
export const explanations: Record<string, (ctx: any) => string> = {
  // === RÉPARTITION ===
  SHARE_CHILDREN_EQUAL: (ctx) => 
    `Partage égal entre ${ctx.num_children} enfant(s).`,
  
  SHARE_SPOUSE: (ctx) => 
    `Part du conjoint survivant : ${ctx.share_percent.toFixed(0)}%.`,
  
  SHARE_REPRESENTATION: (ctx) => 
    `En représentation de ${ctx.represented_id} (prédécédé).`,
  
  SHARE_SIBLINGS: (ctx) => 
    `Part aux frères/sœurs : ${ctx.share_percent.toFixed(0)}%.`,
  
  // === ABATTEMENTS ===
  ABATEMENT_CHILD_100K: (ctx) => 
    `Abattement de ${ctx.amount.toLocaleString('fr-FR')}€ en ligne directe (Art. 779 CGI).`,
  
  ABATEMENT_SIBLING_15K: (ctx) => 
    `Abattement frère/sœur de ${ctx.amount.toLocaleString('fr-FR')}€ (Art. 779 CGI).`,
  
  ABATEMENT_DISABILITY_159K: () => 
    `Abattement supplémentaire de 159 325€ pour handicap (Art. 779-II CGI).`,
  
  ABATEMENT_CONSUMED_15Y: (ctx) => 
    `Abattement déjà utilisé : ${ctx.amount_used.toLocaleString('fr-FR')}€ par donation < 15 ans (Art. 784 CGI).`,
  
  // === FISCALITÉ ===
  TAX_SPOUSE_EXEMPT: () => 
    `Exonération totale du conjoint survivant (Art. 796-0 bis CGI).`,
  
  TAX_BRACKET_5: (ctx) => 
    `Tranche à 5% sur ${ctx.amount.toLocaleString('fr-FR')}€.`,
  
  TAX_BRACKET_20: (ctx) => 
    `Tranche à 20% sur ${ctx.amount.toLocaleString('fr-FR')}€.`,
  
  // === LIQUIDATION ===
  LIQUIDATION_COMMUNITY_50: (ctx) => 
    `Biens communs : 50% reviennent au conjoint (${(ctx.community_total / 2).toLocaleString('fr-FR')}€).`,
  
  LIQUIDATION_PRECIPUT: (ctx) => 
    `Clause de préciput : ${ctx.value.toLocaleString('fr-FR')}€ prélevés par le conjoint avant partage.`,
  
  // === LEGS ===
  BEQUEST_SPECIFIC: (ctx) => 
    `Legs particulier : ${ctx.asset_name} (${ctx.pct}%).`,
  
  // === ALERTES ===
  ALERT_RESERVE_EXCEEDED: (ctx) => 
    `⚠️ La réserve héréditaire est entamée de ${ctx.excess.toLocaleString('fr-FR')}€.`,
  
  ALERT_OVER_ALLOCATION: (ctx) => 
    `⚠️ Le bien "${ctx.asset_id}" est sur-alloué (${ctx.pct}% distribué).`,
  
  ALERT_INTERNATIONAL: (ctx) => 
    `⚠️ Résidence à l'étranger (${ctx.country}). Convention fiscale à vérifier.`,
};
```

---

## UTILISATION DANS LES COMPOSANTS

```tsx
import { explanations } from '@/lib/explanationDictionary';

function HeirCard({ heir }) {
  return (
    <div>
      <h3>{heir.name}</h3>
      <ul>
        {heir.explanation_keys.map((ek, i) => (
          <li key={i}>
            {explanations[ek.key]?.(ek.context) || `[${ek.key}]`}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## MAINTENANCE

Quand le moteur ajoute une nouvelle clé :
1. Elle apparaîtra dans l'output API.
2. Si elle n'est pas dans le dictionnaire, afficher `[KEY_NAME]` comme fallback.
3. Ajouter la traduction humaine dans le dictionnaire.
