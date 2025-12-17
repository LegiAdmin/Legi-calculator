# Mission Lovable - Étape 4 : Stratégie & Volontés (Wishes)

**Objectif** : Capturer les intentions du défunt ("Qui reçoit quoi ?") sans bloquer l'utilisateur avec des règles juridiques complexes. C'est le moteur qui fera le tri.

> **Philosophie "Permissive UI"** :
> L'interface doit permettre de combiner librement des **Legs Particuliers** (biens précis) ET une **Répartition Globale** (%).
> Ne cherche pas à valider la légalité en temps réel (ex: réserve héréditaire). Laisse l'utilisateur exprimer ses vœux, le calculateur générera les warnings nécessaires ensuite.

**Fichiers concernés** : `src/components/strategy/StrategyDashboard.tsx` (Suggestion), `src/components/strategy/WishesForm.tsx`, `src/hooks/useSimulation.ts`.

---

## 1. UX : PARCOURS PAR INTENTION

Au lieu d'un formulaire administratif, propose un parcours guidé par les questions clés :

### 1.1 "Avez-vous fait des donations de votre vivant ?"
*   Si OUI -> Interface d'ajout de Donations.
*   *Subtilité UX* : Distinguer clairement :
    *   **Donation-Partage** (Valeur figée au jour de l'acte) -> Pas de rapport civil.
    *   **Don Manuel / Simple** (Revalorisée au décès) -> Rapport civil.
    *   *Champs requis* : Date, Bénéficiaire, Montant/Bien.

### 1.2 "Avez-vous rédigé un testament ?"
Si OUI, deux niveaux de personnalisation possibles (cumulables) :

#### A. Legs Particuliers ("Je donne ma maison à Paul")
*   Permettre de lier un **Actif** spécifique à un **Bénéficiaire**.
*   *Backend* : `wishes.specific_bequests`.
*   *UX* : Une liste "Actif -> Bénéficiaire".

#### B. Répartition du Reste ("Je veux 50/50 entre mes enfants et mon ami")
*   Par défaut : **Dévolution Légale** (Rien à faire).
*   Si personnalisé : **Répartition Sur-Mesure** (`testament_distribution` = `CUSTOM`).
*   *UX* : Un camembert ou des sliders pour répartir 100% de la *masse restante* entre les bénéficiaires (Héritiers + Tiers).

### 1.3 "Clauses Spécifiques (Mariage)"
*   Uniquement si Marieé(e) sous régime communautaire.
*   Proposer les clauses : **Préciput**, **Attribution Intégrale**.

---

## 2. LOGIQUE DE PERSISTANCE (CRITIQUE)

Toutes les données saisies à cette étape (comme aux précédentes) doivent être sauvegardées dans la base de données Supabase créée à l'étape 1.

*   **Table `simulations`** : Stocke le JSON complet de l'état (Assets, Members, Wishes...).
*   **Sauvegarde** : Auto-save ou bouton "Sauvegarder" explicite.
*   **Pourquoi ?** : Le calcul final (Étape 5) est stateless, il a besoin de tout l'objet `SimulationInput` reconstitué.

---

## 3. POINTS D'ATTENTION & PISTES DE RÉFLEXION

### 3.1 La "Double Distribution"
L'utilisateur peut vouloir dire : *"Je donne la maison à Paul (Legs particulier), et tout le reste est partagé 50/50 entre Paul et Jacques."*
=> **C'est possible !**
*   L'UI doit permettre d'ajouter des legs particuliers, PUIS de définir la répartition du reste.
*   Ne bloque pas l'utilisateur s'il vide son patrimoine avec des legs particuliers. Le moteur gérera.

### 3.2 L'Option du Conjoint
*   Si le conjoint est présent, il a souvent un choix à faire (Usufruit vs 1/4 PP).
*   **Si Donation au Dernier Vivant (DDV)** déclarée : L'option "Quotité Disponible" s'ajoute.
*   *Conseil UX* : Affiche ces options comme des "Scénarios" possibles pour le calcul, ou laisse par défaut sur "Usufruit" (le plus courant) avec possibilité de changer.

### 3.3 Passif & Dettes
*   N'oublie pas une section **Passif** (`debts`).
*   Permettre de lier une dette à un actif (ex: Emprunt Immo sur Résidence Principale) est crucial pour le net taxable par actif.

---

## CRITÈRES DE SUCCÈS
*   [ ] L'utilisateur peut combiner Legs Particuliers et Répartition en %.
*   [ ] Les donations passées sont clairement identifiées (Rapportables ou non).
*   [ ] Aucune règle bloquante n'empêche la saisie (ex: dépasser la quotité disponible est autorisé en saisie, le moteur alertera).
*   [ ] Les données sont persistées en base pour le calcul final.
