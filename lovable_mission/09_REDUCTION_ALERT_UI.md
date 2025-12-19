# 09 - Alerte Action en Réduction UI

## Contexte Légal
L'action en réduction (Art. 920+ Code civil) permet aux héritiers réservataires de récupérer leur part de réserve si les libéralités (donations + legs) dépassent la quotité disponible.

---

## Déclencheur
L'alerte s'affiche dans les résultats de simulation **si et seulement si** :
```typescript
totalDonations + totalBequests > disposableQuota
```

---

## Design de l'Alerte

### Position
En haut de la section "Résultats", avant le détail par héritier.

### Style
```typescript
<Alert type="warning" severity="high">
  <AlertTitle>⚠️ Libéralités excessives détectées</AlertTitle>
  <AlertDescription>
    Les donations et legs ({totalLiberalities}€) dépassent la quotité disponible ({disposableQuota}€).
    <br/>
    <strong>Excédent réductible :</strong> {excessAmount}€
  </AlertDescription>
  <AlertAction>
    <Tooltip content="Art. 920+ Code civil : Les héritiers réservataires peuvent demander la réduction des libéralités pour reconstituer leur réserve.">
      <InfoIcon />
    </Tooltip>
  </AlertAction>
</Alert>
```

### Colors
- Background : `#FEF3C7` (amber-100)
- Border : `#F59E0B` (amber-500)
- Icon : ⚠️ Warning triangle

---

## Détail de la Réduction (Expandable)

### Section collapsible
```
📋 Détail de la réduction
───────────────────────────
1. Legs testament → ami : 80 000€ → 20 000€ (réduction -60 000€)
2. Donation 2023 → neveu : 50 000€ → 50 000€ (non affecté)
```

### Ordre affiché
1. D'abord les legs (testamentaires)
2. Puis les donations (du plus récent au plus ancien)

---

## Bouton d'Action (Optionnel)

```typescript
<Button variant="outline" size="sm">
  En savoir plus sur l'action en réduction
</Button>
```
Lien vers : page explicative ou modal avec :
- Explication de l'action en réduction
- Délai de prescription (5 ans)
- Recommandation de consulter un notaire

---

## API Response Structure

```json
{
  "reduction_info": {
    "is_reducible": true,
    "total_excess": 60000,
    "reduced_liberalities": [
      {
        "liberality_id": "legs1",
        "type": "BEQUEST",
        "beneficiary_id": "ami",
        "original_value": 80000,
        "reduction_amount": 60000,
        "reduced_value": 20000
      }
    ]
  }
}
```

---

## Non affiché si
- `is_reducible == false`
- Pas d'héritiers réservataires (pas d'enfants)
- Aucune libéralité déclarée
