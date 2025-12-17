# Mission Lovable - Étape 3 : Membres de la Famille

**Objectif** : Gérer les structures familiales complexes (recomposées, adoption) avec une rigueur juridique totale.
**Focus** : Uniquement la constitution de la famille (Héritiers). La stratégie de transmission sera traitée à l'étape suivante.

**Fichiers concernés** : `src/components/family/FamilyMemberForm.tsx`, `src/components/family/FamilyTree.tsx`.

---

## 1. PHILOSOPHIE UX : "L'ARBRE OUVERT"

Contrairement à une approche purement légale qui masquerait les héritiers non-prioritaires, nous devons permettre la saisie de **TOUS** les membres potentiels (pour les legs).

L'interface doit être séquencée en 3 étapes logiques :

### Étape 1 : La Lignée Directe (Descendants)
*   **Question** : "Avez-vous des enfants ?"
*   **UI** : Liste des Enfants (Souches).
*   **Interaction Hiérarchique** :
    *   Sur chaque Enfant, bouton/accordéon **"Ajouter Petit-Enfant"**.
    *   *Note au développeur* : Toujours permettre l'ajout, même si le parent est vivant (utile pour saut de génération).
    *   *Auto-detection* : Si Parent = Décédé/Renonçant -> Flag `represented_heir_id` automatique sur les petits-enfants.

### Étape 2 : L'Ascendance et les Collatéraux
*   **Question** : "Avez-vous des parents ou frères et sœurs ?"
*   **UI** :
    *   **Parents** : Ajout Père / Mère.
    *   **Frères / Sœurs** : Liste.
    *   **Neveux / Nièces** : Attachés aux Frères/Sœurs (comme les petits-enfants).
*   *Note* : Cette section doit être accessible **MÊME SI** des enfants sont saisis (car on peut vouloir léguer la quotité disponible aux parents/frères).

### Étape 3 : Tiers et Autres Bénéficiaires
*   **Question** : "Souhaitez-vous inclure d'autres personnes (proches, associations...) ?"
*   **Type de relation** :
    *   `PARTNER` (Concubin / Pacs).
    *   `OTHER` (Ami, Tiers).
    *   `CHARITY` (Association - *Nouveau type à prévoir*).

---

## 2. CHAMPS DE SAISIE ET LOGIQUE

### 2.1 Champs Communs
*   `Prénom / Nom`.
*   `Date de Naissance` (Ou "Décédé" -> Date Décès).
*   `Relation` (Determiné par la section d'ajout).

### 2.2 Champs Spécifiques (Conditionnels)
*   **Adoption** (Sur Enfant uniquement) : Simple/Plénière.
*   **Handicap** (Sur tous) : Checkbox "Situation de Handicap".
*   **Renonciation** (Sur héritiers présomptifs) : Switch "Renonce à la succession".
*   **Fente Successorale** (Sur Parents/Collatéraux) :
    *   Si contextuellement pertinent (pas d'enfants, pas de conjoint), demander "Ligne Paternelle" / "Maternelle".
    *   *UX* : Peut être inféré si on demande "Père" vs "Mère", mais pour les Frères/Soeurs (demi-frères), la question se pose.

---

## 3. TABLE DE ROUTAGE (RÈGLES MÉTIER)

Le frontend doit être permissif en entrée, c'est le moteur (Backend) qui filtrera les héritiers réservataires vs les légataires.

| Qui j'ajoute ? | Relation API | Parent Vivant ? | Parent Décédé ? | Note |
| :--- | :--- | :--- | :--- | :--- |
| Enfant | `CHILD` | - | - | Toujours héritier (sauf si renonce) |
| Petit-Enfant | `GRANDCHILD` | Non-Héritier (Légataire potentiel) | Héritier (Représentant) | L'UI doit gérer les 2 cas |
| Parent | `PARENT` | Non-Héritier (Si enfants) | Non-Héritier (Si enfants) | Peut recevoir un legs |
| Frère/Sœur | `SIBLING` | Non-Héritier (Si enfants/parents) | - | Peut recevoir un legs |
| Tiers | `OTHER` | Jamais Héritier | Jamais Héritier | Uniquement pour legs |



## CRITÈRES DE SUCCÈS
*   [ ] La saisie est hiérarchique (Parent -> Enfant).
*   [ ] La représentation est automatisée (pas besoin de demander "Qui représentez-vous ?", c'est implicite par la hiérarchie).
*   [ ] Cas "Saut de génération" supporté (Petits-enfants ajoutés même si parent vivant).

