# 📘 Moteur de Succession : La Pierre de Rosette (Tech & Droit)

**Version** : 2.0 (Expert Edition)  
**Date** : 20 Décembre 2025  
**Code Source** : `succession_engine/`

---

## 1. Introduction : Parler le même langage

Ce projet repose sur un principe absolu : **"Code is Law"**.
Pour que Développeurs et Juristes collaborent, voici le dictionnaire des concepts clés.

| Concept Juridique (Le Droit) | Objet Technique (Le Code) | Description |
|------------------------------|---------------------------|-------------|
| **Patrimoine** | `input.assets` (List[`Asset`]) | L'ensemble des biens (maison, comptes, bijoux). |
| **Dévolution** | `heir_shares` (Dict) | Qui hérite de quelle fraction (ex: 1/4 chacun). |
| **Masse Successorale** | `net_succession_assets` (Float) | La valeur nette finale à partager après dettes et rapports. |
| **Réserve Héréditaire** | `legal_reserve` (Float) | La part "intouchable" protégée pour les enfants. |
| **Abattement Fiscal** | `allowance_amount` (Float) | La réduction d'impôt liée à la parenté (ex: 100k€). |
| **Traçabilité** | `tracer` (Object) | Le "journal de bord" qui explique chaque `if`. |

---

## 2. Le Pipeline en 5 Actes (Calcul Successoral)

Le moteur exécute une séquence immuable de 5 étapes. Aucune étape ne peut être sautée.

### 🎭 Acte 1 : La Liquidation Matrimoniale
*Séparer ce qui est au conjoint de ce qui est au défunt.*

#### 🏛️ Le Droit (Pour le Dev)
Avant de partager l'héritage, il faut "couper le gâteau" du mariage.
*   **Séparation de biens** : Facile, chacun reprend ses billes.
*   **Communauté (Standard)** : Tout ce qui a été gagné pendant le mariage est divisé par 2.
*   **Règle Clé** : Si un époux a payé une dette de l'autre avec l'argent commun, il doit une **Récompense** (une dette interne).

#### ⚙️ L'Algorithme (Pour le Notaire)
1.  **Boucle sur les Actifs** :
    *   Si `AssetOrigin == PERSONAL` (Bien Propre) : 100% au propriétaire.
    *   Si `AssetOrigin == COMMUNITY` : 50% au défunt, 50% au conjoint.
    *   *Exception* : Si Régime = Séparation, `COMMUNITY` est impossible (Warning).
2.  **Calcul des Récompenses** :
    *   `Reward = Valeur_Bien * %_Financement_Commun`
    *   On ajuste les masses : `Actif_Défunt += Reward / 2`.
3.  **Avantages Matrimoniaux** :
    *   Si `FullAttribution` (Communauté Universelle) : Actif du défunt = 0 (Tout va au conjoint).
    *   *Check Chaos* : Si enfants d'un autre lit -> Appel règle **R-1527** (Voir Section 3).

#### 🧮 Exemple Concret
> Couple marié (Communauté), Maison (500k€). Financement : 20% Apport personnel Monsieur, 80% Emprunt commun.
> *   **Droit** : Le bien est commun (car acquis pendant mariage) mais Monsieur a droit à récompense.
> *   **Calcul Moteur** :
>     *   Masse Commune = 500k€. Part Monsieur = 250k€.
>     *   Récompense due par communauté à Monsieur = 500k * 20% = 100k€.
>     *   **Actif Successoral Monsieur** = 250k (Sa part) + 50k (1/2 Récompense) = **300k€**.

---

### 💰 Acte 2 : La Reconstitution (Le Passé)
*On ne meurt pas seulement avec ce qu'on a, mais avec ce qu'on a donné.*

#### 🏛️ Le Droit
Pour vérifier que les enfants ne sont pas lésés, on doit **"Rapporter"** (réintégrer fictivement) toutes les donations passées.
*   **Rapport Civil** : On ajoute la valeur des donations à la masse.
*   **Art. 738-2 (Droit de Retour)** : Si le défunt n'a pas d'enfants, les biens qu'il a reçus de ses parents retournent à eux (ils "remontent").

#### ⚙️ L'Algorithme
1.  **Masse Brute** = Résultat Acte 1.
2.  **Déduction Dettes** : `Masse -= Dettes`.
    *   *Attention* : Dettes sur biens exonérés (Dutreil) plafonnées (Art. 769 CGI).
3.  **Rapport Donations** : `Masse += Somme(Donations_Rapportables)`.
    *   Si `DonationPartage` : Valeur figée au jour de la donation.
    *   Si `DonManuel` : Valeur réévaluée au décès.
4.  **Check Droit de Retour (R-738-2)** :
    *   Si `Pas_Enfants` ET `Parents_Vivants` ET `Asset.received_from_parent`:
    *   L'actif sort de la masse et retourne au parent. `Masse -= Valeur_Bien`.

---

### ⚖️ Acte 3 : La Dévolution (Le Partage)
*Qui reçoit quelle part du gâteau ?*

#### 🏛️ Le Droit (Ordre de priorité)
1.  **Enfants** (Toujours prioritaires).
2.  **Conjoint** (Concurrence les enfants ou les parents).
3.  **Parents/Frères** (Si pas d'enfants ni conjoint).

#### ⚙️ L'Algorithme
1.  **Identification Ordre** :
    *   Si `List[Child] > 0` : Ordre 1 (Enfants). Part Conjoint = Usufruit ou 1/4 (Art. 757 CC).
    *   Si `List[Child] == 0` : Activation logique "Hors Enfants".
2.  **Réserve Héréditaire** :
    *   `Reserve = Masse * (1/2 si 1 enf, 2/3 si 2 enf, 3/4 si 3+)`.
    *   `Quotité_Disponible = Masse - Reserve`.
3.  **Attribution** :
    *   Chaque héritier reçoit son `%` théorique.
    *   Si `Legs` (Testament) > `Quotité` -> **Action en Réduction** (On rogne le legs).

#### 🧮 Exemple Concret (Option Conjoint)
> Masse 1M€. 2 Enfants, 1 Conjoint. Conjoint choisit 100% Usufruit (Âge 72 ans -> 30%).
> *   **Calcul Part Conjoint** : 1M€ * 0% (PP) + Valeur Usufruit (300k€). Il reçoit 300k€ en valeur fiscale.
> *   **Calcul Part Enfants** : 1M€ - 300k€ = 700k€ (Nue-Propriété) à diviser par 2. Soit 350k€ chacun.

---

### 🛡️ Acte 4 : La Fiscalité Assurance-Vie (Le "Off-Shore" Légal)
*Avant de payer l'impôt sur l'héritage, on règle l'Assurance-Vie.*

#### 🏛️ Le Droit
L'Assurance-Vie est "Hors Succession". Elle a sa propre fiscalité.
*   **Art. 990 I** : Primes versées avant 70 ans. Abattement 152 500€ / bénéficiaire. Taux 20%.
*   **Art. 757 B** : Primes après 70 ans. Abattement unique de 30 500€. Le surplus réintègre la succession.

#### ⚙️ L'Algorithme
Pour chaque contrat :
1.  **Split** Primes <70 / >70.
2.  **Calcul 990 I** : 
    *   `Abattement = 152500 * Nb_Benef`.
    *   `Taxable = Primes - Abattement`.
    *   `Taxe = Taxable * 20%`.
3.  **Calcul 757 B (Réintégration)** :
    *   `Surplus = Max(0, Primes_Apres_70 - 30500)`.
    *   Ce montant est stocké dans `heir_757b_addbacks` pour l'Acte 5.

---

### 💸 Acte 5 : L'Impôt de Succession (La Facture)
*L'État passe à la caisse.*

#### 🏛️ Le Droit
Chaque héritier paie sur ce qu'il reçoit NET.
`Impôt = (Part Reçue - Abattement) * Barème Progressif`.

#### ⚙️ L'Algorithme
Pour chaque héritier :
1.  **Base Taxable** = `Part_Civile (Acte 3) + Réintégration_757B (Acte 4)`.
2.  **Abattements** :
    *   Déduire `100 000€` (Enfant) ou `15 932€` (Frère).
    *   *Rappel Fiscal* : Soustraire l'abattement déjà "mangé" par donations < 15 ans.
3.  **Calcul Droits** :
    *   Appliquer le barème par tranches (ex: 20% jusqu'à 550k€).
    *   *Spécificité* : Si `Adoption Simple` -> check `Soins Continus` -> Si OK, barème enfant, sinon 60%.

---

## 3. Catalogue des Règles "Chaos" (Expert Mode)

Ces règles ne s'activent que dans 5% des cas, mais ce sont les plus dangereuses.

### 🔴 **R-1527 : L'Action en Retranchement**
*   **Situation** : Remariage, Conjoint veut tout (Com. Universelle), Enfants du 1er lit lésés.
*   **La Loi** : L'avantage matrimonial est inopposable aux enfants du 1er lit. Il est réduit à la Quotité Disponible Spéciale.
*   **L'Algorithme** :
    *   `IF has_stepchildren AND regime == UNIVERSAL`:
    *   Calculer `Avantage = 50% Communauté`.
    *   Calculer `QD = Masse * (1/4 ou 1/3...)`.
    *   `Exces = Avantage - QD`.
    *   Le moteur force le reversement de `Exces` aux enfants du 1er lit.

### 🟣 **R-746 : La Fente Successorale**
*   **Situation** : Pas de descendance, pas de parents, pas de fratrie. Juste des cousins.
*   **La Loi** : On divise la succession en deux moitiés indépendantes (Paternelle / Maternelle).
*   **L'Algorithme** :
    *   Créer 2 sous-masses (`Masse / 2`).
    *   Chercher le parent le plus proche dans la branche Paternelle (ex: Cousin Germain).
    *   Chercher le parent le plus proche dans la branche Maternelle (ex: Grand-Oncle).
    *   Attribuer indépendamment. Ne jamais mélanger les branches.

### 🌍 **R-750-TER : Le Choc International**
*   **Situation** : Défunt résidant fiscal France, Actifs aux USA.
*   **La Loi** : La France taxe TOUT (Mondial).
*   **L'Algorithme** :
    *   `IF deceased.country == 'FR'`:
    *   Ne jamais filtrer les actifs par pays. Tout inclure.
    *   Générer un Warning "Risque de double imposition" (Crédit d'impôt non calculé auto).

---

*Ce document est la vérité technique du moteur Antigravity v2.0. Toute modification du code doit être reflétée ici.*
