# 📘 Documentation Officielle du Moteur de Succession (Antigravity v1.5)

**Date de mise à jour** : 16 Décembre 2025  
**Version du Moteur** : 1.5 (Expert Features)  
**Audience** : Experts Comptables, Notaires, Développeurs, Auditeurs.

---

## 1. Introduction et Philosophie

Le moteur de calcul **Antigravity Succession Engine** est conçu pour modéliser avec une rigueur notariale les règles de transmission de patrimoine en France. Il ne s'agit pas d'une simple estimation, mais d'une **simulation juridique et fiscale stricte** basée sur le Code Civil (CC) et le Code Général des Impôts (CGI).

### Principes Clés
1.  **Conformité Légale** : Chaque règle de calcul est sourcée par un article de loi (CGI/CC).
2.  **Transparence** : Le moteur explique chaque étape de calcul (calcul intermédiaires, abattements utilisés, tranches appliquées).
3.  **Exhaustivité** : Gestion des cas simples (famille standard) aux cas complexes (familles recomposées, entreprises familiales, international).

---

## 2. Glossaire Technique & Juridique

*   **Masse Successorale** : Valeur totale du patrimoine du défunt au jour du décès, nette de dettes et augmentée des donations passées.
*   **Réserve Héréditaire (Art. 913 CC)** : Part minimale du patrimoine réservée par la loi à certains héritiers (enfants). Le défunt ne peut pas les en priver.
*   **Quotité Disponible** : Part du patrimoine dont le défunt peut disposer librement (testament, donations).
*   **Rapport Civil (Art. 843 CC)** : Opération consistant à réintégrer fictivement les donations passées pour vérifier que l'égalité entre héritiers est respectée.
*   **Dévolution** : Détermination des personnes ayant vocation à hériter et de leur rang.
*   **Abattement (Art. 779 CGI)** : Montant déduit de la part nette avant calcul de l'impôt.

---

## 3. Architecture du Calcul (Pipeline en 5 Étapes)

Le moteur exécute séquentiellement 5 étapes strictes pour garantir la justesse juridique.

### 🔄 Étape 1 : Liquidation du Régime Matrimonial
*Objectif : Déterminer ce qui appartient au défunt vs ce qui appartient au conjoint survivant.*

**Règles Appliquées :**
*   **Séparation de biens** : Les biens propres (`PERSONAL_PROPERTY`) restent à 100% au propriétaire. Les biens indivis sont partagés selon la quote-part.
*   **Communauté Légale** :
    *   Biens acquis **avant** mariage ou par succession/donation = Propres (100% défunt).
    *   Biens acquis **pendant** mariage = Communs (50% défunt / 50% conjoint).
    *   **Récompenses (Art. 1468 CC)** : Si un bien propre a été financé par la communauté (ou inversement), une récompense est calculée pour rétablir l'équilibre.
    *   **Avantages Matrimoniaux** : Prise en compte des clauses de **Préciput** (prélèvement avant partage) ou d'**Attribution Intégrale** (100% au conjoint).

**Résultat 1** : `Actif Net du Défunt`.

---

### 💰 Étape 2 : Reconstitution de la Masse
*Objectif : Reconstruire le patrimoine fictif pour vérifier la réserve.*

**Formule (Art. 922 CC) :**
> Masse = Actif Net + Donations Rapportables - Dettes Déductibles

**Détails Techniques :**
1.  **Rapport des Donations** :
    *   *Don Manuel* : Rapporté à sa valeur au jour du décès (réévaluée).
    *   *Donation-Partage* : Non rapportable civilement (fige les valeurs).
2.  **Passif (Dettes)** :
    *   Déduction des emprunts, impôts, frais funéraires (plafond 1 500€ sans justif - Art. 775 CGI).
    *   **Règle Expert (Art. 769 CGI)** : Les dettes finançant un bien partiellement exonéré (ex: Parts Dutreil 75%) ne sont déductibles qu'au prorata (ex: 25%).
    
**Résultat 2** : `Masse de Calcul de la Réserve`.

---

### ⚖️ Étape 3 : Dévolution et Réserve
*Objectif : Définir qui hérite de quoi et protéger les héritiers réservataires.*

**Ordre de Priorité (Art. 734 CC) :**
1.  **Enfants et descendants** (excluent les parents et collatéraux).
2.  **Parents** (si pas d'enfants).
    *   *Fente Successorale (Art. 746 CC)* : Si pas de conjoint/enfants, division 50/50 branche paternelle/maternelle.
3.  **Conjoint Survivant** :
    *   Si enfants communs : Choix entre 100% Usufruit ou 1/4 Pleine Propriété (Art. 757 CC).
    *   Si enfants d'un autre lit : 1/4 Pleine Propriété obligatoire (sauf si donation au dernier vivant).
4.  **Représentation (Art. 751 CC)** : Les petits-enfants prennent la part de leur parent prédécédé.

**Calcul de la Réserve (Art. 913 CC) :**
*   1 enfant : 1/2
*   2 enfants : 2/3
*   3+ enfants : 3/4
*   Conjoint (si pas d'enfants ni parents) : 1/4

---

### 🧩 Étape 4 : Distribution des Parts
*Objectif : Répartir les actifs selon la loi et les volontés (Testament).*

**Mécanique :**
1.  Application des **Legs Particuliers** (biens spécifiques légués).
2.  Application de la **Quotité Disponible** (souvent au conjoint via Donation au Dernier Vivant).
3.  Répartition du reste selon les droits légaux.
4.  **Valorisation de l'Usufruit (Art. 669 CGI)** : Si le conjoint opte pour l'usufruit, sa valeur fiscale dépend de son âge (ex: 71-80 ans = 30% de la valeur du bien).

---

### 💸 Étape 5 : Calcul de la Fiscalité (Droits de Succession)
*Objectif : Calculer l'impôt dû par chaque héritier.*

**Pipeline Fiscal :**
1.  **Part Nette Taxable** = Part reçue - Dettes proportionnelles.
2.  **Exonérations Partielles (Professionnel)** :
    *   **Pacte Dutreil (Art. 787 B CGI)** : Exonération de 75% sur la valeur des parts (si engagement conservé). *Attention : Comptes courants d'associés (CCA) exclus.*
    *   **Biens Ruraux / Forêts (Art. 793 CGI)** : Exonération de 75% (parfois plafond 300k€).
3.  **Abattements Personnels (Art. 779 CGI)** :
    *   Enfants/Parents : 100 000€.
    *   Frères/Sœurs : 15 932€.
    *   Conjoint/Pacs : **Totalement Exonéré**.
    *   Handicap : +159 325€ (cumulable).
    *   *Rappel Fiscal (Art. 784 CGI)* : Déduction des abattements déjà utilisés lors de donations < 15 ans.
4.  **Application du Barème (Art. 777 CGI)** : Tranches progressives (5% à 45% pour ligne directe).
5.  **Assurance-Vie (Hors Succession)** :
    *   **Primes < 70 ans (Art. 990 I CGI)** : Abattement 152 500€/bénéficiaire, puis taxé à 20% (jusqu'à 700k) / 31.25%.
    *   **Primes > 70 ans (Art. 757 B CGI)** : Abattement global 30 500€, puis droits de succession classiques.
    *   **Vie-Génération** : Abattement supplémentaire de 20% avant calcul.
    *   **Anciens Contrats (<1991/1998)** : Exonération totale.

---

## 4. Fonctionnalités Avancées (Expert)

### 🌍 Contexte International
*   **Résidence Fiscale** : Détection des résidents hors France. Warning sur l'application de la loi (Règlement UE 650/2012).
*   **Actifs Étrangers** : Warning sur risque de double imposition (crédit d'impôt non calculé automatiquement sans convention précise).

### 🏢 Société Civile Immobilière (SCI)
*   **Valorisation** : Distinction Part Sociale vs Compte Courant d'Associé (CCA).
*   **Dette Société** : Le passif social réduit la valeur de la part, mais le CCA est une créance taxable à 100% (sauf quasi-usufruit).

### 🔄 Adoptions
*   **Adoption Plénière** : Droits alignés sur enfants biologiques.
*   **Adoption Simple** : Taxé à 60% (Entre tiers) **SAUF** si preuve de "soins continus" pendant 5 ans durant minorité ou 10 ans majorité (Art. 786 CGI) -> rétablit taux ligne directe.

---

## 5. Dictionnaire des Données Exhaustif (Référence Technique)

Ce chapitre liste **tous** les champs acceptés par l'API (`SimulationInput`) et leur impact sur le calcul.

### 5.1 Contexte Global (`matrimonial_regime`, `wishes`...)

| Champ | Type | Description & Impact |
|-------|------|----------------------|
| `matrimonial_regime` | Enum | `SEPARATION` (séparation de biens), `COMMUNITY_LEGAL` (réduite aux acquêts), `COMMUNITY_UNIVERSAL`. <br> Impacte la liquidation (étape 1). |
| `marriage_date` | Date | Détermine si un bien acquis est propre ou commun en `COMMUNITY_LEGAL`. |
| `residence_country` | Code ISO | Pays de résidence du défunt (ex: "FR", "US"). Génère des alertes internationales si != "FR". |
| `matrimonial_advantages` | Objet | Clauses spécifiques (Préciput, Attribution Complète). Voir section 4. |

### 5.2 Les Actifs (`assets`)

Chaque bien est défini par un objet `Asset`.

| Champ | Impact | Règle de Gestion |
|-------|--------|------------------|
| `id` | Identifiant | Clé unique (ex: "Maison", "Compte titre"). |
| `estimated_value` | Valeur | Valeur vénale au jour du décès. |
| `asset_origin` | Enum | `PERSONAL_PROPERTY` (100% défunt) ou `COMMUNITY_PROPERTY` (50% si acquis pdt mariage). |
| `acquisition_date` | Date | Comparée à `marriage_date` pour qualifier le bien en communauté légale. |
| `professional_exemption` | Objet | **Pacte Dutreil / Rural**. Si présent, applique abattement 75% |
| `is_main_residence` | Bool | Si `True` et occupé par conjoint, abattement 20% sur la valeur. |
| `life_insurance_contract_type`| Enum | `STANDARD` (défaut), `VIE_GENERATION` (-20%), `ANCIEN_CONTRAT` (Exonéré). |
| `premiums_before_70` | Montant | Primes versées < 70 ans (Abattement 152.5k€/bénéficiaire). |
| `premiums_after_70` | Montant | Primes versées > 70 ans (Abattement 30.5k€ global). |

### 5.3 Les Héritiers (`members`)

| Champ | Impact | Règle de Gestion |
|-------|--------|------------------|
| `relationship` | Enum | `CHILD`, `SPOUSE`, `PARENT`, `SIBLING`, etc. Définit l'abattement fiscal et la réserve. |
| `is_disabled` | Bool | Si `True`, ajoute l'abattement handicap (+159 325€). |
| `is_from_current_union` | Bool | Si `False` (enfant d'un autre lit), bloque l'option "Usufruit" du conjoint (sauf donation). |
| `represented_heir_id` | ID | Pour la **Représentation**. Si renseigné, cet héritier prend la place du parent prédécédé. |
| `adoption_type` | Enum | `FULL` (Plénière) ou `SIMPLE` (Simple). Impacte le tarif (Simple = 60%, sauf exceptions). |
| `acceptance_option` | Enum | `RENUNCIATION` : L'héritier ne reçoit rien (sauf si représenté). |

### 5.4 Les Donations Passées (`donations`)

| Champ | Impact | Règle de Gestion |
|-------|--------|------------------|
| `donation_type` | Enum | `DON_MANUEL` (Rapportable pour sa valeur réévaluée), `DONATION_PARTAGE` (Rapportable pour 0€, fige la valeur). |
| `current_estimated_value` | Montant | Valeur utilisée pour le *Rapport Civil* (rétablissement égalité). |
| `is_declared_to_tax` | Bool | (Info) Indique si la donation a déjà payé des droits. |

### 5.5 Le Passif (`debts`)

| Champ | Impact | Règle de Gestion |
|-------|--------|------------------|
| `amount` | Montant | Valeur de la dette à déduire. |
| `is_deductible` | Bool | Si `False`, ignoré (ex: dette de jeu). |
| `linked_asset_id` | ID | Si lié à un actif exonéré (ex: Dutreil), déductibilité au prorata (Art. 769 CGI). |
| `asset_origin` | Enum | Si `COMMUNITY_PROPERTY`, dette divisée par 2 avant déduction. |

---

## 6. Règles de Gestion Critiques (Business Rules)

### Règle R-01 : Qualification des Biens (Liquidation)
> **Si** régime = `COMMUNITY_LEGAL` :
> *   Tout bien acquis **avant** `marriage_date` est `PROPRE`.
> *   Tout bien acquis **après** `marriage_date` est `COMMUN` (sauf si origine = `INHERITANCE` ou `DONATION`).
> *   Tout bien sans date est présumé `COMMUN`.

### Règle R-02 : Option du Conjoint (Art. 757 CC)
> *   **Si** enfants communs uniquement : Choix libre (100% Usufruit OU 1/4 PP).
> *   **Si** enfants non communs présents : 1/4 PP imposé.
> *   *Exception* : Si `has_spouse_donation` (Donation dernier vivant) est `True`, options élargies (Quotité disponible, etc.).

### Règle R-03 : Fiscalité Assurance-Vie (Art. 990 I)
> L'abattement de 152 500€ est **par bénéficiaire**.
> Le moteur calcule : `Abattement Total = 152 500 * Nombre de Bénéficiaires désignés`.
> *Note : Dans le moteur actuel, si aucun bénéficiaire spécifique n'est lié au contrat, on assume 1 bénéficiaire par défaut.*

### Règle R-04 : Plafonnement des Dettes (Art. 769 CGI)
> **Si** une dette finance un bien exonéré à X% (ex: Dutreil 75%),
> **Alors** la dette n'est déductible qu'à hauteur de (100 - X)%.
> *Exemple : Emprunt 100k€ sur bien Dutreil. Déductible = 25k€.*

### Règle R-05 : Représentation et Renonciation
> Un héritier renonçant (`RENUNCIATION`) ne compte pas pour la réserve, **SAUF** s'il est représenté par ses propres descendants.
> Le moteur vérifie récursivement la présence de représentants valides.

---



---
*Fin du document. Ce document fait foi pour l'audit et la validation technique.*
