# Prompt Lovable Agent - Adaptation Complète BDD/UI

## Contexte

Le calculateur de succession Python (`succession_engine`) nécessite des champs spécifiques pour fonctionner. Ce prompt contient TOUTES les instructions pour adapter la BDD Supabase et l'interface.

---

## PARTIE 1 : MIGRATIONS SQL SUPABASE

### 1.1 Table `assets`
```sql
ALTER TABLE assets 
ADD COLUMN is_main_residence BOOLEAN DEFAULT FALSE,
ADD COLUMN spouse_occupies_property BOOLEAN DEFAULT FALSE;
```

### 1.2 Table `family_members`
```sql
ALTER TABLE family_members
ADD COLUMN is_disabled BOOLEAN DEFAULT FALSE,
ADD COLUMN represented_heir_id UUID REFERENCES family_members(id);
```

### 1.3 Table `transmission_preferences`
```sql
ALTER TABLE transmission_preferences
ADD COLUMN spouse_choice_type TEXT 
CHECK (spouse_choice_type IN ('USUFRUCT', 'QUARTER_OWNERSHIP', 'DISPOSABLE_QUOTA'));
```

### 1.4 Enum `family_relationship`
```sql
ALTER TYPE family_relationship ADD VALUE IF NOT EXISTS 'PARTNER';
ALTER TYPE family_relationship ADD VALUE IF NOT EXISTS 'NEPHEW_NIECE';
```

### 1.5 Table `matrimonial_advantages` (nouvelle)
```sql
CREATE TABLE matrimonial_advantages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE,
  has_full_attribution BOOLEAN DEFAULT FALSE,
  has_preciput BOOLEAN DEFAULT FALSE,
  preciput_assets TEXT[],
  has_unequal_share BOOLEAN DEFAULT FALSE,
  spouse_share_percentage NUMERIC CHECK (spouse_share_percentage >= 51 AND spouse_share_percentage <= 99),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## PARTIE 2 : ENRICHISSEMENT JSONB

### 2.1 `assets.details`

**Pour REAL_ESTATE :**
```json
{
  "usufructuary_birth_date": "1960-03-15",
  "community_funding_percentage": 30,
  "received_from_parent_id": "uuid-parent"
}
```

**Pour INSURANCE :**
```json
{
  "premiums_before_70": 150000,
  "premiums_after_70": 50000,
  "subscriber_type": "DECEASED"
}
```

### 2.2 `family_members.details`

**Pour PARENT et SIBLING :**
```json
{
  "paternal_line": true
}
```

---

## PARTIE 3 : MODIFICATIONS UI

### 3.1 Formulaire Immobilier
- [ ] Checkbox "Résidence principale"
- [ ] Si cochée → Checkbox "Le conjoint y habite"
- [ ] Si ownership_mode = USUFRUCT/BARE_OWNERSHIP → Date picker "Naissance usufruitier"
- [ ] Si asset_origin = COMMUNITY_PROPERTY → Slider "% fonds propres"

### 3.2 Formulaire Assurance-vie
- [ ] Input "Primes avant 70 ans"
- [ ] Input "Primes après 70 ans"
- [ ] Select "Souscripteur" (Défunt / Conjoint)

### 3.3 Formulaire Famille
- [ ] Checkbox "En situation de handicap"
- [ ] Pour GRANDCHILD → Select "Représente" (parents décédés)
- [ ] Pour PARENT/SIBLING → Radio "Ligne" (Paternelle / Maternelle)

### 3.4 Formulaire Transmission
- [ ] Section "Option conjoint" avec radios :
  - Usufruit totalité (USUFRUCT)
  - 1/4 pleine propriété (QUARTER_OWNERSHIP)
  - Quotité disponible (DISPOSABLE_QUOTA) - si donation dernier vivant

### 3.5 Formulaire Avantages Matrimoniaux (nouveau)
- [ ] Checkbox "Attribution intégrale communauté"
- [ ] Checkbox "Préciput" + multi-select biens
- [ ] Checkbox "Partage inégal" + slider 51-99%

---

## PARTIE 4 : MISE À JOUR TYPES

```bash
npx supabase gen types typescript --project-id XXX > src/integrations/supabase/types.ts
```

Mettre à jour :
- `useAssets.ts` : is_main_residence, spouse_occupies_property
- `useFamilyMembers.ts` : is_disabled, represented_heir_id
- `useTransmissionPreferences.ts` : spouse_choice_type

---

## PRIORITÉS

| P1 | is_main_residence, spouse_occupies_property, champs assurance-vie |
| P2 | is_disabled, spouse_choice_type, represented_heir_id |
| P3 | paternal_line, matrimonial_advantages |

---

## PARTIE 5 : RAPPEL FISCAL 15 ANS (Art. 784 CGI)

Le calculateur utilise maintenant le champ `is_declared_to_tax` des donations pour calculer l'abattement restant.

**Comportement:**
- Les donations déclarées aux impôts consomment l'abattement
- Seules les donations < 15 ans comptent (à implémenter côté BDD si besoin)

**Impact UI:**
- S'assurer que le champ `is_declared_to_tax` est bien collecté dans le formulaire donations
- Afficher un avertissement si l'abattement est réduit par des donations antérieures

---

## PARTIE 6 : REPRÉSENTATION MULTI-NIVEAUX (Art. 751+ CC)

### Enum `family_relationship`
```sql
ALTER TYPE family_relationship ADD VALUE IF NOT EXISTS 'GREAT_GRANDCHILD';
```

### Explication
Les arrière-petits-enfants peuvent maintenant représenter leurs grands-parents décédés dans la souche successorale.

**Fonctionnement du calculateur:**
- Si un petit-enfant est décédé, ses enfants (arrière-petits-enfants) prennent sa place
- Ils sont regroupés dans la souche de l'enfant original du défunt
- Chaque souche reçoit une part égale, divisée entre ses membres

**Impact UI:**
- Ajouter valeur "GREAT_GRANDCHILD" dans l'enum family_relationship
- Pour les arrière-petits-enfants → ajouter select "Représente" (dropdown des petits-enfants décédés)

---

## PARTIE 7 : ADOPTION (Art. 786 CGI)

### Champs BDD Existants

La table `family_members` a déjà les colonnes suivantes dans `details` JSONB:
- `adoption_type`: "simple" | "plénière"
- `has_received_continuous_care`: boolean (pour adoption simple)

### Comportement Calculateur

| Type | Impact Fiscal |
|------|---------------|
| **Plénière** | Mêmes droits qu'enfant biologique (100K€ abattement, barème ligne directe) |
| **Simple sans soins continus** | Taxé comme "étranger" (60% taux forfaitaire, 1 594€ abattement) |
| **Simple avec soins continus 5 ans** | Mêmes droits qu'enfant biologique (Art. 786 CGI) |

### Vérifications UI

- [ ] S'assurer que `adoption_type` est bien passé au calculateur via `family_members.details.adoption_type`
- [ ] S'assurer que `has_received_continuous_care` est collecté pour les adoptions simples
- [ ] Afficher un avertissement si adoption simple sans soins continus (droit = 60%)

---

## PARTIE 8 : DÉMEMBREMENT COMPLEXE

### 8.1 Champs BDD (JSONB `assets.details`)

Ajouter les champs suivants pour gérer les cas spécifiques (Art. 669 I et II CGI) :

```json
{
  "usufruct_type": "VIAGER" | "TEMPORAIRE",
  "usufruct_duration_years": 10,
  "is_quasi_usufruct": true
}
```

### 8.2 Logique Calculateur

- **Usufruit Viager** (Défaut) : Basé sur l'âge de l'usufruitier (Art. 669 I CGI)
- **Usufruit Temporaire** (Art. 669 II CGI) : 23% de la pleine propriété par tranche de 10 ans (ex: 15 ans = 46%)
- **Quasi-usufruit** : Un simple flag pour l'instant (impacte potentiellement le passif successoral futur)

### 8.3 Modifications UI (Formulaire Actif)

- [ ] Ajouter sélecteur "Type d'usufruit" (Viager par défaut)
- [ ] Si "Temporaire" sélectionné → Afficher input "Durée (années)"
- [ ] Ajouter checkbox "Quasi-usufruit (bien consomptible)" (ex: comptes bancaires démembrés)

---

## PARTIE 9 : CAS EXCEPTIONNELS (Option Successorale)

### 9.1 Champs BDD (JSONB `family_members.details`)

Ajouter le champ `acceptance_option` :
- `PURE_SIMPLE` (Défaut) : Acceptation pure et simple
- `BENEFIT_INVENTORY` : À concurrence de l'actif net (Droits inchangés, impacte dettes)
- `RENUNCIATION` : Renonciation (Art. 805 CC)

### 9.2 Logique Calculateur

- **Renonciation** :
  - L'héritier est censé n'avoir jamais hérité (part = 0).
  - SAUF s'il est représenté (Art. 754 CC) : sa souche reçoit la part, distribuée à ses représentants.
  - Ne compte plus pour la réserve héréditaire (sauf si représenté).

### 9.3 Modifications UI (Formulaire Héritier)

- [ ] Ajouter sélecteur "Option d'acceptation" pour chaque héritier
- [ ] Valeurs : "Acceptation pure et simple", "À concurrence de l'actif net", "Renonciation"

---

## PARTIE 10 : SÉCURISATION & CONFORMITÉ (Phase 9)

### 10.1 Champs BDD

- **Dettes** (`debts.details`) : Ajouter `proof_provided: boolean` (Justificatif fourni ?).

### 10.2 Logique "Conseiller Discret"

Le moteur ne bloque jamais la saisie, mais renvoie des **warnings** dans `succession_output.warnings`.
L'interface doit afficher ces alertes de manière informative (ex: section "Audit" ou badges oranges).

**Contrôles effectués :**
1.  **Dates Incohérentes** : Bien déclaré "Commun" mais acquis avant mariage (ou "Propre" acquis pendant).
2.  **Frais Funéraires** : Plammonnement automatique à 1500€ déductibles si > 1500€ (Sauf si `proof_provided=true` où on prévient juste que c'est supérieur au standard).
3.  **Dettes non déductibles** : Warning si justificatif présent mais case "déductible" décochée.

### 10.3 Modifications UI

- [ ] Afficher les Warnings retournés par l'API dans une section "Résultats de l'audit" ou "Points d'attention".
- [ ] Dans le formulaire Dettes : Ajouter checkbox "Justificatif fourni" (débloque warning plafond funéraire).

---

## PARTIE 11 : OPTIMISATION SCI & COMPTES COURANTS (Phase 10)

### 11.1 Contexte Juridique
Une SCI est souvent composée de deux éléments pour un associé :
1.  **Parts Sociales** : Titres de propriété (Éligibles Pacte Dutreil - Exonération 75%).
2.  **Compte Courant d'Associé (CCA)** : Argent prêté par l'associé à la SCI (Créance pure - Non éligible Dutreil).

**Problème** : Si l'utilisateur saisit tout dans "Valeur estimée", le moteur applique l'exonération 75% sur le tout (Illégal).
**Solution** : Distinguer les deux valeurs.

### 11.2 Champs BDD (`assets`)
*   `cca_value` (number) : Montant du Compte Courant d'Associé.
*   `company_liabilities` (number, optionnel) : Dettes bancaires de la SCI (Aide au calcul).

### 11.3 Interface Saisie SCI (Formulaire Asset)
Si `Type == PROFESSIONAL` (ou SCI dans immobilier/financier) :
1.  **Champ "Valeur des Parts"** (`estimated_value`) : Valeur nette des parts.
2.  **Champ "Compte Courant d'Associé"** (`cca_value`) : "Avez-vous un compte courant dans la société ?" (Oui/Non + Montant).

### 11.4 Assistant de Valorisation (Calculatrice Intégrée)
Proposer un petit "Helper" pour calculer la valeur des parts si l'utilisateur ne la connaît pas :
> **Formule :** Valeur Parts = (Valeur Immeuble + Trésorerie - Emprunt Restant - Compte Courant Associés) x % Détenu

**Inputs Assistant :**
- Valeur vénale immeuble(s)
- Capital restant dû (Emprunts)
- Trésorerie
- Montant total des Comptes Courants d'Associés (Dette de la société envers les associés)

**Output** -> Remplit automatiquement `estimated_value` et `cca_value`.

---

## PARTIE 12 : INTERNATIONAL (Phase 11)

### 12.1 Radar de Conformité (Filet de Sécurité)
Nous devons détecter dès le départ si le dossier est "Hors Norme" (Loi étrangère potentielle).

### 12.2 Questionnaire Initial (Création Dossier)
Ajouter une question cruciale :
> **"Quel était le pays de résidence habituelle du défunt ?"**
> *   [Dropdown Pays] (Défaut : France)
> *   Si sélection != France -> Afficher Warning : *"Attention, la succession pourrait être soumise à une loi étrangère."*

### 12.3 Formulaire Actif (Asset)
Ajouter champ :
> **"Pays de situation du bien"**
> *   [Dropdown Pays] (Défaut : France)
> *   Si sélection != France -> Badge "International" sur l'actif.

### 12.4 Affichage des Risques
Le moteur renverra des `warnings` spécifiques.
*   Warning "Loi Applicable" -> Afficher en **ROUGE** en haut du bilan.
// ... (Warnings International)
*   Warning "Double Imposition" -> Afficher en **ORANGE** à côté de l'actif concerné.

---

## PARTIE 13 : FONCTIONNALITÉS EXPERT (PHASE 15)

### 13.1 Assurance-Vie Complexe
L'assurance-vie a des régimes fiscaux très différents selon la date du contrat.

**Modifications UI (Formulaire Assurance-vie) :**
Ajouter un sélecteur "Type de Contrat" :
*   `STANDARD` (Défaut) : Régime classique (Abattement 152 500€).
*   `VIE_GENERATION` : Contrat "Vie-Génération" (Investi 33% en PME/ETI/Logement social).
    *   *Info-bulle* : "Abattement supplémentaire de 20% sur les capitaux décès avant l'abattement fixe."
*   `ANCIEN_CONTRAT` : Contrat exonéré.
    *   *Info-bulle* : "Primes versées avant le 13/10/1998 sur un contrat ouvert avant le 20/11/1991."

### 13.2 Dettes au Prorata (Art. 769 CGI)
Si une dette finance un bien partiellement exonéré (ex: Forêt, Parts Dutreil), elle n'est déductible qu'à hauteur de la part taxable.

**Modifications UI (Formulaire Dettes) :**
*   S'assurer que le champ "Lié à l'actif" (`linked_asset_id`) est bien proposé (Dropdown des actifs).
*   Si l'utilisateur lie une dette à un actif "Professionnel" (Dutreil/Rural), afficher un petit warning/info :
    *   *"Attention : Ce bien étant partiellement exonéré, la dette ne sera déductible qu'au prorata (Art. 769 CGI)."*

---

## PARTIE 14 : DROIT DE RETOUR (Art. 738-2 CC)

### 14.1 Contexte
Si le défunt décède **sans descendant**, les parents peuvent récupérer les biens qu'ils lui avaient donnés (limité à 1/4 par parent).

### 14.2 Modification UI (Formulaire Actif)
Ajouter un champ conditionnel :
*   Question : **"Ce bien a-t-il été reçu par donation d'un parent ?"** (Oui/Non)
*   Si Oui : Select **"Parent donateur"** (Dropdown des Membres type PARENT).
*   *Stockage* : Champ `received_from_parent_id`.

---

## PARTIE 15 : RAFFINEMENTS FAMILLE

### 15.1 Adoption
Si `adoption_type` sélectionné :
*   Si "Simple" -> Checkbox supplémentaire : **"L'adopté a-t-il reçu des soins continus pendant 5 ans durant sa minorité ?"**
    *   *Info-bulle* : "Condition requise (Art. 786 CGI) pour bénéficier des droits en ligne directe (sinon 60%)."

### 15.2 Fente Successorale (Pas de conjoint ni enfants)
Pour les héritiers de type **PARENT** ou **SIBLING/NEPHEW** :
*   Ajouter Radio Button obligatoires : **"Ligne Paternelle"** / **"Ligne Maternelle"**.
*   *Stockage* : `paternal_line` (true/false).
