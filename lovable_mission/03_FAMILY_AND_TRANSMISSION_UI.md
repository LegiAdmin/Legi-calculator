# Mission Lovable - Étape 3 : Famille & Transmission

**Objectif** : Gérer les structures familiales complexes (recomposées, adoption) et les désirs de transmission (options du conjoint, avantages matrimoniaux).

**Fichiers concernés** : `src/components/family/FamilyMemberForm.tsx`, `src/components/transmission/TransmissionPreferences.tsx`.

---

## 1. FORMULAIRE MEMBRES DE LA FAMILLE

L'ordre des héritiers est strict (Art 734 CC) mais connaît des exceptions (Représentation, Fente).

### 1.1 Qualification de la Relation
*   **Date de Naissance** : Obligatoire pour TOUS les membres (calcul d'âge pour usufruit et validité juridique).
Ajouter/Mettre à jour l'enum `relationship` avec :
*   `GREAT_GRANDCHILD` (Arrière-petit-enfant).
*   `NEPHEW_NIECE` (Neveu/Nièce).
*   `PARTNER` (Concubin/Pacs - Fiscalement étranger sauf testament).

### 1.2 La Représentation (Art. 751 CC)
Permet à un petit-enfant d'hériter à la place de son parent décédé.
*   [ ] Si relation = `GRANDCHILD` ou `GREAT_GRANDCHILD` :
    *   Afficher Select : **"Représente le parent..."** (Liste des héritiers décédés de la génération N-1).
    *   *Stockage* : `represented_heir_id`.
    *   *Validation* : On ne peut représenter qu'une personne décédée (`birth_date` + date décès virtuelle ou statut).

### 1.3 L'Adoption (Art. 786 CGI)
Fiscalité très différente selon le type.
*   [ ] Select "Type d'adoption" :
    *   **Aucune** (Biologique) - Défaut.
    *   **Plénière** (Droits complets).
    *   **Simple** (Droits restreints - 60% taxe).
*   [ ] *Conditionnel* (Si Adoption Simple) :
    *   Checkbox : **"A reçu des soins continus pendant 5 ans durant sa minorité ?"**
    *   *Impact* : Si coché, rétablit les droits en ligne directe (exonération/barème normal).

### 1.4 La Fente Successorale (Collateraux/Ascendants)
Si le défunt n'a ni conjoint ni enfant, le patrimoine est divisé entre ligne paternelle/maternelle.
*   [ ] Si relation = `PARENT` ou `SIBLING` ou `NEPHEW_NIECE` :
    *   Radio Obligatoire : **"Ligne Paternelle"** vs **"Ligne Maternelle"**.
    *   *Stockage* : `paternal_line` (bool).

### 1.5 Handicap (Art. 779 II CGI)
*   [ ] Checkbox : **"En situation de handicap"** (`is_disabled`).
    *   *Info* : "Ouvre droit à un abattement supplémentaire de 159 325€."

---

## 2. PRÉFÉRENCES DE TRANSMISSION

### 2.1 Option du Conjoint Survivant (Art. 757 CC)
Le calcul change radicalement selon ce choix.
*   [ ] Section "Choix du Conjoint" (Visible si Conjoint présent) :
    *   Radio : **"Usufruit de la totalité"** (`USUFRUCT`).
    *   Radio : **"1/4 en pleine propriété"** (`QUARTER_OWNERSHIP`).
    *   Radio : **"Quotité Disponible"** (`DISPOSABLE_QUOTA`).
        *   *Condition* : Uniquement si "Donation au dernier vivant" est cochée.

### 2.2 Avantages Matrimoniaux (Contrat de Mariage)
Clauses puissantes permettant de transmettre plus au conjoint *avant* la succession.
*   [ ] Section "Clauses du Contrat de Mariage" :
    *   Checkbox : **"Attribution Intégrale de la Communauté"** (`has_full_attribution`).
        *   *Effet* : Le conjoint prend tout le commun. Pas de succession sur ces biens.
    *   Checkbox : **"Préciput"** (`has_preciput`).
        *   *UI* : Multi-select "Biens concernés" (Résidence, Mobilier, Comptes...).
    *   Checkbox : **"Partage Inégal"** (`has_unequal_share`).
        *   *UI* : Slider "Part du conjoint" (51% à 99%).

---

## 3. REFUS DE SUCCESSION (Renonciation)
Un héritier peut refuser sa part (pour la laisser à ses enfants par représentation, ou pour ne pas payer les dettes).
*   [ ] Dans la liste des héritiers, ajouter un statut/action :
    *   Select "Option" : **Acceptation** (Défaut) / **Renonciation**.
    *   *Stockage* : `acceptance_option` = `RENUNCIATION`.

---

## CRITÈRES DE SUCCÈS
*   [ ] La saisie guidée couvre tous les cas (Adoption, Représentation).
*   [ ] Les options du conjoint sont claires et conformes à la loi (pas d'usufruit si enfant d'autre lit sans donation).
*   [ ] Les données sont prêtes à être envoyées à l'API.
