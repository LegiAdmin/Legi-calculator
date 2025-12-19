# Spécification des Tests - Moteur de Succession

Ce document liste les **règles fiscales implémentées** dans le calculateur.
**Validez ces valeurs avant l'implémentation des tests.**

---

## 1. Abattements (Art. 779 CGI)

| Relation | Abattement | Article |
|----------|------------|---------|
| Enfant / Parent | **100 000 €** | Art. 779 I CGI |
| Frère / Sœur | **15 932 €** | Art. 779 IV CGI |
| Neveu / Nièce | **7 967 €** | Art. 779 V CGI |
| Autre (>4ème degré) | **1 594 €** | Art. 779 VI CGI |
| Conjoint / PACS | **Exonéré** | Loi TEPA 2007 |
| Handicap (cumul) | **+159 325 €** | Art. 779 II CGI |

### Vérification proposée
- [ ] Enfant hérite 200 000€ → Base taxable = 100 000€
- [ ] Frère hérite 50 000€ → Base taxable = 34 068€
- [ ] Conjoint hérite 1M€ → Taxe = 0€

---

## 2. Barème Ligne Directe (Art. 777 CGI)

| Tranche | Taux | Impôt pour cette tranche |
|---------|------|-------------------------|
| 0 → 8 072 € | 5% | max 403,60 € |
| 8 072 → 12 109 € | 10% | max 403,70 € |
| 12 109 → 15 932 € | 15% | max 573,45 € |
| 15 932 → 552 324 € | 20% | max 107 278,40 € |
| 552 324 → 902 838 € | 30% | max 105 154,20 € |
| 902 838 → 1 805 677 € | 40% | max 361 135,60 € |
| > 1 805 677 € | 45% | — |

### Exemple de calcul détaillé

**Scénario : 1 enfant hérite de 500 000 €**

```
Masse successorale : 500 000 €
Abattement CHILD  : -100 000 €
────────────────────────────────
Base taxable      : 400 000 €

Calcul par tranches :
  8 072 × 5%      =     403,60 €
  4 037 × 10%     =     403,70 €
  3 823 × 15%     =     573,45 €
378 068 × 20%     =  75 613,60 €  (400 000 - 8 072 - 4 037 - 3 823 - 6 000)
────────────────────────────────
TOTAL IMPÔT       =  76 994,35 €
```

**⚠️ À VALIDER : Ce calcul est-il correct ?**

---

## 3. Barème Frères/Sœurs

| Tranche | Taux |
|---------|------|
| 0 → 24 430 € | 35% |
| > 24 430 € | 45% |

### Exemple

**Scénario : 1 frère hérite de 100 000 €**

```
Masse successorale : 100 000 €
Abattement SIBLING: -15 932 €
────────────────────────────────
Base taxable      : 84 068 €

Calcul :
  24 430 × 35%    =   8 550,50 €
  59 638 × 45%    =  26 837,10 €
────────────────────────────────
TOTAL IMPÔT       =  35 387,60 €
```

---

## 4. Barème Autres

| Relation | Taux |
|----------|------|
| Parents >4ème degré | 55% |
| Non-parents | 60% |

**Implémentation actuelle : 60% flat pour relationship=OTHER**

---

## 5. Réserve Héréditaire (Art. 913 CC)

| Nombre d'enfants | Réserve | Quotité disponible |
|------------------|---------|-------------------|
| 1 enfant | 1/2 | 1/2 |
| 2 enfants | 2/3 | 1/3 |
| 3+ enfants | 3/4 | 1/4 |

### Ascendants (sans enfants - Art. 914-1 CC)

| Situation | Réserve |
|-----------|---------|
| 2 parents vivants | 1/2 (1/4 chacun) |
| 1 parent vivant | 1/4 |

---

## 6. Usufruit (Art. 669 CGI)

| Âge de l'usufruitier | Valeur usufruit | Valeur nue-propriété |
|---------------------|-----------------|---------------------|
| < 21 ans | 90% | 10% |
| 21-30 ans | 80% | 20% |
| 31-40 ans | 70% | 30% |
| 41-50 ans | 60% | 40% |
| 51-60 ans | 50% | 50% |
| 61-70 ans | 40% | 60% |
| 71-80 ans | 30% | 70% |
| 81-90 ans | 20% | 80% |
| > 91 ans | 10% | 90% |

---

## 7. Assurance-Vie (Art. 990 I et 757 B CGI)

### Primes versées avant 70 ans (Art. 990 I)
- Abattement : **152 500 € par bénéficiaire**
- Au-delà : Taxation forfaitaire (20% puis 31,25%)

### Primes versées après 70 ans (Art. 757 B)
- Abattement global : **30 500 € tous bénéficiaires**
- Au-delà : Droits de succession normaux

---

## 8. Exonérations Professionnelles

| Dispositif | Exonération | Article |
|------------|-------------|---------|
| Pacte Dutreil | 75% | Art. 787 B CGI |
| Biens ruraux ≤300k | 75% | Art. 793 CGI |
| Biens ruraux >300k | 50% | Art. 793 CGI |
| Groupements forestiers | 75% | Art. 793 CGI |

---

## 9. Cas Spéciaux

### Adoption Simple (Art. 786 CGI)
- **Sans soins continus** → Taxé comme "OTHER" (60%)
- **Avec soins continus 5+ ans** → Taxé comme enfant légal

### Représentation (Art. 751+ CC)
- Petits-enfants représentant un parent **prédécédé**
- Part par souche, abattement partagé

---

## ✅ Checklist de Validation

- [ ] Les abattements sont corrects
- [ ] Le barème ligne directe est correct
- [ ] Le barème frères/sœurs est correct
- [ ] Le taux 60% pour "autres" est correct
- [ ] La réserve héréditaire est correcte
- [ ] Le barème usufruit est correct
- [ ] Les règles assurance-vie sont correctes
- [ ] Les exonérations Dutreil sont correctes
- [ ] L'adoption simple est correctement traitée

---

## 📝 Notes pour la validation

Si vous constatez des erreurs, notez-les ici :

_[Espace pour commentaires]_
