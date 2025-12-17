# Mission Lovable - Étape 2 : Interface Gestion des Actifs (Expert)

**Objectif** : Modifie les formulaires UI pour gérer les actifs complexes (Immobilier, Assurance-Vie, SCI) avec toutes les nuances fiscales.

> **🎨 Liberté UX/UI** : Tu as carte blanche pour organiser l'interface, afin de rendre l'expérience utilisateur la plus fluide possible.
> **⚠️ Contrainte Data** : Seule contrainte stricte : le format des données en sortie (JSON) doit correspondre *exactement* aux spécifications pour être accepté par l'API.

**Fichiers concernés** : `src/components/assets/AssetForm.tsx` (ou équivalent), `src/hooks/useAssets.ts`.

---

## 1. FORMULAIRE IMMOBILIER (REAL_ESTATE)

### 1.3 Spécificités Immobilier
*   [ ] **Résidence Principale** (`is_main_residence`)
    *   Checkbox : "C'est la résidence principale du couple"
    *   Si cochée : "Le conjoint survivant continue de l'occuper ?" (`spouse_occupies_property`) -> Abattement 20%.

---

## 2. QUESTIONS COMMUNES (TOUS ACTIFS)

Certaines questions s'appliquent à **tous** les types de biens (Immobilier, Meubles, Placements...).

### 2.1 Mode de Détention (Démembrement)
*   [ ] Select "Mode" : Pleine Propriété, Usufruit, Nue-Propriété, Indivision.
*   [ ] Si **Démembrement** (Usufruit/Nue-Propriété) :
    *   Select "Type" : Viager (défaut) ou Temporaire.
    *   Input requis selon type : "Date naissance usufruitier" ou "Durée".

### 2.2 Droit de Retour (Biens de Famille - Art. 738-2 CC)
*Concerne tout bien reçu par donation d'un parent (Immeuble, Bijoux, Parts...)*
*   [ ] Radio : "Ce bien a-t-il été reçu par donation d'un parent ?"
*   [ ] Si Oui -> Select "Parent Donateur" (Liste des PARENTS).
    *   *Stockage* : `received_from_parent_id`.

---

## 2. FORMULAIRE ASSURANCE-VIE (INSURANCE)

L'assurance-vie a une fiscalité spécifique hors succession, qui dépend des dates.

### 2.1 Primes Versées
*   [ ] Input Number : "Primes versées avant 70 ans".
    *   *Abattement auto* : 152 500€ / bénéficiaire.
*   [ ] Input Number : "Primes versées après 70 ans".
    *   *Abattement auto* : 30 500€ global.

### 2.2 Type de Contrat (Expert Phase 15)
Ajouter un Select "Régime Fiscal du Contrat" :
1.  **Standard** (Défaut).
2.  **Vie-Génération** (*Investissement 33% PME/Social*).
    *   *Impact* : Abattement de 20% avant calcul des droits.
3.  **Ancien Contrat** (*Primes < 13/10/98 sur contrat < 20/11/91*).
    *   *Impact* : Exonération totale.

---

## 3. FORMULAIRE PROFESSIONNEL & SCI (SCI / SHARES)

Confusion fréquente : distinguer la valeur des parts de la créance (Compte Courant).

### 3.1 Distinction Parts vs Compte Courant (CCA)
Si Type = `PROFESSIONAL` ou `SCI` :
*   [ ] Input : "Valeur nette des parts sociales" (`estimated_value`).
    *   *Info* : "Actif Net - Dettes Bancaires". Éligible Dutreil (75% exonération).
*   [ ] Input : "Compte Courant d'Associé (CCA)" (`cca_value`).
    *   *Info* : "Sommes prêtées par l'associé à la société". Non éligible Dutreil (sauf cas très rares), taxé à 100%.

### 3.2 Helper de Valorisation (Calculatrice Pop-up)
Ajouter un bouton "Aide au calcul de la valeur des parts" qui ouvre une modale :
*   Inputs : Valeur Immeuble, Emprunt Restant, Trésorerie, CCA Global, % Détenu.
*   Formule : `(Immeuble + Trésorerie - Emprunt - CCA Global) * %Parts`.
*   Remplir automatiquement le champ `estimated_value`.

---

## 4. FORMULAIRE INTERNATIONAL
*   [ ] Select "Pays de situation" (Défaut FR).
*   [ ] Si autre que FR -> Afficher Badge "Risque Double Imposition".

---

## CRITÈRES DE SUCCÈS
*   [ ] Le formulaire change dynamiquement selon le type d'actif.
*   [ ] Les données complexes (JSONB) sont correctement sauvegardées et rechargées.
*   [ ] L'UX guide l'utilisateur pour éviter les erreurs (SCI notamment).
