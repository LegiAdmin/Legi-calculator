# Mission Lovable - Étape 3 : Membres de la Famille

**Objectif** : Gérer les structures familiales complexes (recomposées, adoption) avec une rigueur juridique totale.
**Focus** : Uniquement la constitution de la famille (Héritiers). La stratégie de transmission sera traitée à l'étape suivante.

**Fichiers concernés** : `src/components/family/FamilyMemberForm.tsx`, `src/components/family/FamilyTree.tsx`.

---

## 1. UX : ARBRE GÉNÉALOGIQUE PROGRESSIF

L'utilisateur ne doit pas saisir une liste plate, mais construire un arbre.

### 1.1 Niveau 1 : Les Enfants
*   Afficher une liste de "Souches" (Enfants).
*   Bouton **"Ajouter un Enfant"**.
*   Champs pour chaque enfant :
    *   `Prénom`, `Date de Naissance`.
    *   Switch : **"Est décédé(e) ?"**
    *   Switch : **"A renoncé à la succession ?"**
    *   *Si Décédé/Renonçant* -> Afficher un appel à l'action clair : *"Ajouter ses enfants (Vos petits-enfants) pour la représentation"*.

### 1.2 Niveau 2 : Les Petits-Enfants (Attachés à un parent)
*   Chaque "Enfant" (card/row) doit avoir une sous-section ou un bouton **"Ajouter un Petit-Enfant"**.
*   **Logique Métier Critique** :
    *   Si le parent est **DÉCÉDÉ** ou **RENONÇANT** :
        *   Le petit-enfant vient **en représentation** (hérite à la place du parent).
        *   **Action** : Assigner automatiquement `represented_heir_id` = ID du Parent.
    *   Si le parent est **VIVANT** et **ACCEPTANT** :
        *   Le petit-enfant n'hérite pas légalement (sauf testament spécifique).
        *   **Action** : On permet quand même de le créer (pour les legs futurs), mais `represented_heir_id` = `null`.

### 1.3 Gestion des autres héritiers (Si pas de descendants)
*   Si aucun enfant n'est saisi, afficher progressivement les options pour :
    *   **Père / Mère** (Ascendants).
    *   **Frères / Sœurs** (Collatéraux).
    *   **Neveux / Nièces** (Si Frère/Sœur décédé -> Représentation identique aux enfants).

---

## 2. DÉTAILS JURIDIQUES & CHAMPS COMPLÉMENTAIRES

Une fois la structure créée, des champs spécifiques apparaissent selon le contexte.

### 2.1 Spécificités Adoption (Enfants uniquement)
*   [ ] Select "Type d'adoption" (Visible sur chaque Enfant) :
    *   **Aucune** (Biologique) - Défaut.
    *   **Plénière** (Droits complets).
    *   **Simple** (Droits restreints - 60% taxe).
*   [ ] *Si Adoption Simple* :
    *   Checkbox : **"A reçu des soins continus pendant 5 ans durant sa minorité ?"**
    *   *Impact* : Débloque la fiscalité "Enfant".

### 2.2 Fente Successorale (Parents/Collatéraux)
*   Uniquement si aucun descendant ni conjoint n'est présent.
*   [ ] Sur chaque Parent ou Frère/Sœur : Radio Obligatoire **"Ligne Paternelle"** vs **"Ligne Maternelle"** (`paternal_line`).

### 2.3 Handicap
*   [ ] Checkbox globale sur chaque fiche membre : **"En situation de handicap"**.
    *   *Impact* : Abattement +159 325€.

---

## 3. RÉCAPITULATIF TECHNIQUE DES LIENS
Le frontend doit transformer l'arbre visuel en une liste plate pour l'API.

| ID Membre | Relation | Parent Status | Résultat API (`represented_heir_id`) |
| :--- | :--- | :--- | :--- |
| Enfant A | CHILD | Vivant | `null` |
| Enfant B | CHILD | Décédé | `null` |
| Petit-Fils B1 | GRANDCHILD | (Enfant B est Décédé) | `ID_Enfant_B` |
| Petit-Fils A1 | GRANDCHILD | (Enfant A est Vivant) | `null` |

---

## CRITÈRES DE SUCCÈS
*   [ ] La saisie est hiérarchique (Parent -> Enfant).
*   [ ] La représentation est automatisée (pas besoin de demander "Qui représentez-vous ?", c'est implicite par la hiérarchie).
*   [ ] Cas "Saut de génération" supporté (Petits-enfants ajoutés même si parent vivant).

