# Mission Lovable - Étape 4 : Stratégie de Transmission & Volontés

**Objectif** : Offrir une interface complète pour définir "QUI reçoit QUOI". C'est ici que l'utilisateur exprime ses volontés, déclare ses donations passées et configure ses avantages matrimoniaux.
**Warning** : Cette étape est critique car elle modifie les règles de calcul par défaut (Dévolution légale).

**Fichiers concernés** : `src/components/strategy/WishesForm.tsx`, `src/components/strategy/DonationsManager.tsx`, `src/components/strategy/MatrimonialClauses.tsx`.

---

## 1. AVANTAGES MATRIMONIAUX (Si mariés)

Si le régime est communautaire, les époux peuvent avoir aménagé leur contrat.

### 1.1 Clauses Spécifiques
*   [ ] **Attribution Intégrale (`has_full_attribution`)**
    *   *UI* : Checkbox "Les époux ont-ils prévu que le survivant garde TOUTE la communauté ?"
    *   *Impact* : Si oui, pas de succession sur les biens communs. Tout va au conjoint.
*   [ ] **Préciput (`has_preciput`)**
    *   *UI* : Checkbox "Le conjoint peut-il prélever certains biens AVANT tout partage ?"
    *   *Si Oui* : Afficher un Multi-Select des catégories : `Résidence Principale`, `Secondaire`, `Mobilier`, `Comptes`, etc.
*   [ ] **Partage Inégal (`has_unequal_share`)**
    *   *UI* : Checkbox "Partage de la communauté différent de 50/50 ?"
    *   *Si Oui* : Slider ou Input (51% à 99% pour le survivant).

---

## 2. DONATIONS ANTÉRIEURES (Rapport Civil & Fiscal)

Les donations faites du vivant doivent être déclarées pour rétablir l'équilibre entre héritiers (Rapport) et calculer les abattements déjà consommés (Rappel fiscal).

### 2.1 Liste des Donations (`donations`)
*   [ ] Tableau/Liste des donations existantes avec bouton "Ajouter une donation".
*   [ ] **Formulaire Ajout Donation** :
    *   **Type** (Select) : `Don Manuel` (Argent/Meuble), `Donation Partage` (Devant notaire, fige la valeur), `Donation Immo`.
    *   **Bénéficiaire** (Select) : Choisir parmi les Membres de la Famille créés à l'étape 3.
    *   **Date** (DateLibre) : Important pour la règle des 15 ans (Rappel fiscal).
    *   **Montant/Valeur** :
        *   `Valeur à la date de donation` (Historique).
        *   `Valeur actuelle réévaluée` (Pour le rapport civil - Sauf donation-partage).
    *   **Déclarée ?** (Switch `is_declared_to_tax`) : Important pour savoir si on doit payer des droits dessus ou si c'est déjà purgé.

---

## 3. VOLONTÉS TEST AMENTAIRES (`wishes`)

Comment le défunt souhaite-t-il répartir son patrimoine personnel ?

### 3.1 Option du Conjoint Survivant (Art. 757 CC)
*   [ ] **Donation au Dernier Vivant (DDV)** (`has_spouse_donation`)
    *   *UI* : Checkbox "Une donation au dernier vivant a-t-elle été signée ?"
    *   *Impact* : Débloque l'option "Quotité Disponible".
*   [ ] **Choix du Conjoint** (Radio) - Uniquement si Conjoint présent :
    *   1. **Usufruit de la totalité** (Classique).
    *   2. **1/4 en Pleine Propriété** (Classique).
    *   3. **Quotité Disponible** (Si DDV cochée).

### 3.2 Testament & Legs
L'utilisateur peut déroger à la loi par testament.

*   [ ] **Type de Répartition (`testament_distribution`)**
    *   Radio : "Répartition Légale par défaut" (Rien à faire).
    *   Radio : "Répartition Personnalisée (Testament)".

*   [ ] **Gestion des Legs Particuliers (`specific_bequests`)**
    *   *Concept* : "Je laisse la Maison à Paul".
    *   *UI* : Interface "Qui reçoit quoi ?"
    *   Select : Choisir un Actif (créé à l'étape 2).
    *   Select : Choisir un Bénéficiaire.
    *   Input : % de l'actif (Défaut 100%).

---

## 4. DETTES & PASSIF (`debts`)

Les dettes réduisent l'actif net taxable.

### 4.1 Inventaire du Passif
*   [ ] Liste des dettes déclarées.
*   [ ] **Ajout de Dette** :
    *   **Nom/Type** : "Emprunt Immo", "Frais Funéraires" (Plafonné 1500€ auto), "Impôts".
    *   **Montant Restant Dû**.
    *   **Origine** : `Personnelle` ou `Commune` (Si marié).
    *   **Lien Actif** : Si c'est un emprunt lié à un bien précis (ex: pour déductibilité partielle sur bien exonéré Dutreil), permettre de lier à l'actif concerné.

---

## CRITÈRES DE SUCCÈS
*   [ ] L'utilisateur peut modéliser tout type de libéralité (don manuel, testament, préciput).
*   [ ] La distinction entre "Donation Partage" (valeur figée) et "Don Manuel" (réévaluée) est claire dans l'UI.
*   [ ] Le mécanisme de "Lier une dette à un actif" est présent (crucial pour les optimisations fiscales).
*   [ ] Les options du conjoint s'adaptent dynamiquement (DDV présente ou non).
