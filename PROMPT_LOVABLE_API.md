## Contexte

Tu dois intégrer une API Django de calcul de succession française. L'API est accessible sur `https://legi-calculator-production.up.railway.app/api/` (en local: `http://127.0.0.1:8000/api/`).

---

## Endpoints Disponibles

### 1. POST `/api/simulate/` - Calcul de succession

**Description**: Reçoit les données patrimoniales et renvoie le calcul complet de la succession (répartition, fiscalité, étapes de calcul).

### 2. GET `/api/scenarios/` - Liste des scénarios de test

**Description**: Récupère les scénarios de test pré-enregistrés (utile pour le développement).

### 3. GET `/api/docs/` - Documentation Swagger

**Description**: Interface Swagger interactive pour tester l'API: https://legi-calculator-production.up.railway.app/api/docs/

---

## Schéma d'Entrée (SimulationInput)

```typescript
interface SimulationInput {
  // REQUIS - Régime matrimonial
  matrimonial_regime: "COMMUNITY_LEGAL" | "SEPARATION" | "PARTICIPATION_ACQUESTS" | "COMMUNITY_UNIVERSAL";
  
  // Optionnel - Date de mariage (format: "YYYY-MM-DD")
  marriage_date?: string;
  
  // REQUIS - Liste des actifs
  assets: Asset[];
  
  // REQUIS - Membres de la famille (héritiers)
  members: FamilyMember[];
  
  // Optionnel - Volontés testamentaires
  wishes?: Wishes;
  
  // Optionnel - Donations antérieures
  donations?: Donation[];
  
  // Optionnel - Dettes à déduire
  debts?: Debt[];
  
  // Optionnel - Avantages matrimoniaux (clauses contrat de mariage)
  matrimonial_advantages?: MatrimonialAdvantages;
}
```

### Types Détaillés

```typescript
interface Asset {
  id: string;                          // Identifiant unique
  estimated_value: number;             // Valeur en euros
  ownership_mode: "FULL_OWNERSHIP" | "USUFRUCT" | "BARE_OWNERSHIP" | "INDIVISION";
  asset_origin: "PERSONAL_PROPERTY" | "COMMUNITY_PROPERTY" | "INHERITANCE" | "INDIVISION";
  acquisition_date?: string;           // "YYYY-MM-DD" - Important pour régime matrimonial
  
  // Démembrement (si BARE_OWNERSHIP)
  usufructuary_birth_date?: string;    // Requis si BARE_OWNERSHIP
  
  // Financement mixte (récompenses)
  community_funding_percentage?: number; // 0-100, défaut 100
  
  // Résidence principale (abattement 20%)
  is_main_residence?: boolean;
  spouse_occupies_property?: boolean;  // Requis pour abattement
  
  // Assurance-vie
  premiums_before_70?: number;         // Abattement 152.5k€/bénéficiaire
  premiums_after_70?: number;          // Abattement global 30.5k€
}

interface FamilyMember {
  id: string;                          // Identifiant unique
  birth_date: string;                  // "YYYY-MM-DD" - Important pour usufruit
  relationship: "CHILD" | "SPOUSE" | "PARTNER" | "PARENT" | "SIBLING" | "GRANDCHILD" | "OTHER";
  is_from_current_union?: boolean;     // Défaut: true. False = enfant d'autre lit
  represented_heir_id?: string;        // Pour représentation (petits-enfants)
}

interface Wishes {
  has_spouse_donation?: boolean;       // Donation au dernier vivant
  testament_distribution?: "LEGAL" | "SPECIFIC_BEQUESTS" | "SPOUSE_ALL" | "CHILDREN_ALL" | "CUSTOM";
  specific_bequests?: SpecificBequest[];
  custom_shares?: CustomShare[];
  spouse_choice?: {
    choice: "USUFRUCT" | "QUARTER_OWNERSHIP" | "DISPOSABLE_QUOTA";
  };
}

interface Donation {
  id: string;
  donation_type: "don_manuel" | "donation_partage" | "present_usage" | "donation_residuelle" | "donation_graduelle";
  beneficiary_name: string;
  beneficiary_heir_id?: string;        // Lien vers FamilyMember.id
  beneficiary_relationship: "CHILD" | "SPOUSE" | "PARENT" | "SIBLING" | "GRANDCHILD" | "OTHER";
  donation_date: string;               // "YYYY-MM-DD"
  original_value: number;
  current_estimated_value?: number;    // Réévaluation au jour du décès
  is_declared_to_tax?: boolean;
}

interface Debt {
  id: string;
  amount: number;                      // Montant positif restant dû
  debt_type: string;                   // "emprunt immobilier", "crédit consommation", "impôts", "frais funéraires"
  is_deductible?: boolean;             // Défaut: true
  linked_asset_id?: string;            // Si hypothèque liée à un bien
  asset_origin: "PERSONAL_PROPERTY" | "COMMUNITY_PROPERTY";
}

interface MatrimonialAdvantages {
  has_full_attribution?: boolean;      // Clause d'attribution intégrale
  has_preciput?: boolean;              // Clause de préciput
  preciput_assets?: ("RESIDENCE_PRINCIPALE" | "RESIDENCE_SECONDAIRE" | "VEHICULE" | "MOBILIER" | "COMPTES_JOINTS" | "AUTRE")[];
  has_unequal_share?: boolean;         // Partage inégal
  spouse_share_percentage?: number;    // 51-99 si partage inégal
}
```

---

## Schéma de Sortie (SuccessionOutput)

```typescript
interface SuccessionOutput {
  // Métriques globales
  global_metrics: {
    total_estate_value: number;        // Masse successorale nette
    legal_reserve_value: number;       // Réserve héréditaire
    disposable_quota_value: number;    // Quotité disponible
    total_tax_amount: number;          // Total des droits de succession
  };
  
  // Détail par héritier
  heirs_breakdown: HeirBreakdown[];
  
  // Contexte familial
  family_context?: {
    has_spouse: boolean;
    num_children: number;
    has_stepchildren: boolean;         // Enfants d'autre lit
    spouse_age?: number;
  };
  
  // Détails conjoint (si applicable)
  spouse_details?: {
    has_usufruct: boolean;
    usufruct_value?: number;
    usufruct_rate?: number;            // Taux selon barème Art. 669 CGI
    choice_made?: string;
  };
  
  // Liquidation du régime matrimonial
  liquidation_details?: {
    regime: string;
    community_assets_total: number;
    spouse_community_share: number;
    deceased_community_share: number;
    personal_assets_deceased: number;
    has_full_attribution: boolean;
    has_preciput: boolean;
    preciput_value: number;
    details: string[];                 // Explications textuelles
  };
  
  // Détail des actifs
  assets_breakdown: AssetBreakdown[];
  
  // Étapes de calcul (pour transparence)
  calculation_steps: CalculationStep[];
  
  // Alertes et warnings
  warnings: string[];
}

interface HeirBreakdown {
  id: string;
  name: string;
  legal_share_percent: number;         // Pourcentage de la part
  gross_share_value: number;           // Part brute en euros
  taxable_base: number;                // Base taxable après abattement
  abatement_used: number;              // Abattement utilisé
  tax_amount: number;                  // Droits de succession
  net_share_value: number;             // Part nette après impôts
  
  // Détail du calcul fiscal
  tax_calculation_details?: {
    relationship: string;
    gross_amount: number;
    allowance_name: string;
    allowance_amount: number;
    net_taxable: number;
    brackets_applied: TaxBracketDetail[];
    total_tax: number;
  };
}

interface CalculationStep {
  step_number: number;
  step_name: string;                   // Ex: "Liquidation du régime matrimonial"
  description: string;
  result_summary: string;              // Ex: "Part du défunt: 350 000€"
}
```

---

## Exemple de Requête

```json
{
  "matrimonial_regime": "COMMUNITY_LEGAL",
  "marriage_date": "2000-06-15",
  "assets": [
    {
      "id": "maison",
      "estimated_value": 500000,
      "ownership_mode": "FULL_OWNERSHIP",
      "asset_origin": "COMMUNITY_PROPERTY",
      "acquisition_date": "2005-03-20",
      "is_main_residence": true,
      "spouse_occupies_property": true
    }
  ],
  "members": [
    {"id": "spouse", "birth_date": "1970-05-10", "relationship": "SPOUSE"},
    {"id": "child1", "birth_date": "2001-08-15", "relationship": "CHILD"},
    {"id": "child2", "birth_date": "2004-11-22", "relationship": "CHILD"}
  ],
  "wishes": {
    "has_spouse_donation": false,
    "testament_distribution": "LEGAL",
    "spouse_choice": {"choice": "USUFRUCT"}
  }
}
```

---

## Considérations Techniques

### CORS
L'API doit être configurée avec CORS pour permettre les appels depuis ton frontend. Si tu rencontres des erreurs CORS, demande-moi de configurer `django-cors-headers`.

### Authentification (Sécurisée) **[NOUVEAU]**
L'API est sécurisée via **Supabase Auth**. Tout appel doit inclure un header `Authorization` avec un token JWT valide.

```http
Authorization: Bearer <SUPABASE_ACCESS_TOKEN>
```

### Intégration Frontend (React + Supabase)

Voici comment appeler l'API depuis l'application React :

```typescript
import { supabase } from "@/integrations/supabase/client";

const simulateSuccession = async (simulationInput: SimulationInput) => {
  // 1. Récupérer la session active
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session) {
    throw new Error("Utilisateur non authentifié");
  }

  // 2. Appel API avec le token
  const response = await fetch('https://legi-calculator-production.up.railway.app/api/v1/simulate/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}` // <--- Token Supabase
    },
    body: JSON.stringify(simulationInput)
  });

  if (!response.ok) {
    if (response.status === 401) throw new Error("Session expirée, veuillez vous reconnecter");
    const errorData = await response.json();
    throw new Error(errorData.error || "Erreur de calcul");
  }

  return await response.json();
};
```

### Gestion d'Erreurs
- **400 Bad Request**: Données d'entrée invalides (voir `errors` dans la réponse pour détails Pydantic)
- **500 Internal Server Error**: Erreur de calcul (voir `error` et `details`)

### État de l'API
L'API est stateless. Chaque appel à `/api/simulate/` est indépendant.

---

## Considérations Métier (Droit Français)

### Régimes Matrimoniaux
- **COMMUNITY_LEGAL**: Communauté réduite aux acquêts (régime par défaut). Biens acquis pendant le mariage = communs (50/50)
- **SEPARATION**: Séparation de biens. Chaque époux garde ses biens propres
- **COMMUNITY_UNIVERSAL**: Tout est commun (y compris biens acquis avant mariage)

### Option du Conjoint Survivant (Art. 757 CC)
Sans donation au dernier vivant:
- `USUFRUCT`: 100% en usufruit (enfants = nus-propriétaires)
- `QUARTER_OWNERSHIP`: 1/4 en pleine propriété

Avec donation au dernier vivant (`has_spouse_donation: true`):
- `DISPOSABLE_QUOTA`: Quotité disponible en PP (1/2 si 1 enfant, 1/3 si 2, 1/4 si 3+)

### Réserve Héréditaire (Art. 913 CC)
Part incompressible réservée aux enfants:
- 1 enfant: 1/2
- 2 enfants: 2/3
- 3+ enfants: 3/4

### Abattements Fiscaux (CGI)
- Conjoint: **exonéré total**
- Enfants: **100 000€** par parent
- Petits-enfants: **1 594€**
- Frères/sœurs: **15 932€**

### Résidence Principale
Abattement de 20% si le conjoint survivant occupe le bien.

### Assurance-Vie
- Primes versées avant 70 ans: 152 500€ d'abattement par bénéficiaire
- Primes versées après 70 ans: 30 500€ d'abattement global

---

## Ce que tu dois afficher

1. **Métriques globales**
   - Masse successorale totale
   - Réserve héréditaire / Quotité disponible
   - Total des droits de succession

2. **Répartition par héritier**
   - Nom et lien de parenté
   - Part en pourcentage et en euros
   - Abattement utilisé
   - Droits de succession
   - Part nette finale

3. **Étapes de calcul** (pour transparence)
   - Afficher `calculation_steps` pour montrer la logique

4. **Alertes** (`warnings`)
   - Libéralités excessives
   - Représentation par souche
   - etc.

5. **Détail liquidation** (si conjoint)
   - Part communauté vs biens propres
   - Avantages matrimoniaux appliqués

---

## URL Swagger

Pour tester interactivement l'API: `https://legi-calculator-production.up.railway.app/api/docs/`
