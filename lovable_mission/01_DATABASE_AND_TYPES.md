# Mission Lovable - Étape 1 : Infrastructure & Données

**Objectif** : Mettre niveau la base de données Supabase et générer les types TypeScript pour supporter le nouveau moteur de calcul de succession.

Cette étape est **fondamentale** et doit être exécutée avec précision avant toute modification d'interface.

---

## 1. MIGRATIONS SQL (Supabase)

Exécute ces commandes SQL dans l'éditeur SQL de Supabase pour mettre à jour le schéma.

### 1.1 Enrichissement Table `assets`
Ajout des champs pour la résidence principale.
```sql
ALTER TABLE assets 
ADD COLUMN is_main_residence BOOLEAN DEFAULT FALSE,
ADD COLUMN spouse_occupies_property BOOLEAN DEFAULT FALSE;
```

### 1.2 Enrichissement Table `family_members`
Ajout des champs pour le handicap et la représentation.
```sql
ALTER TABLE family_members
ADD COLUMN is_disabled BOOLEAN DEFAULT FALSE,
ADD COLUMN represented_heir_id UUID REFERENCES family_members(id);
```

### 1.3 Enrichissement `transmission_preferences`
Typage strict du choix du conjoint.
```sql
ALTER TABLE transmission_preferences
ADD COLUMN spouse_choice_type TEXT 
CHECK (spouse_choice_type IN ('USUFRUCT', 'QUARTER_OWNERSHIP', 'DISPOSABLE_QUOTA'));
```

### 1.4 Mise à jour Enum `family_relationship`
Ajout des liens de parenté manquants pour les cas complexes (Représentation, Famille recomposée).
```sql
ALTER TYPE family_relationship ADD VALUE IF NOT EXISTS 'PARTNER';
ALTER TYPE family_relationship ADD VALUE IF NOT EXISTS 'NEPHEW_NIECE';
ALTER TYPE family_relationship ADD VALUE IF NOT EXISTS 'GREAT_GRANDCHILD';
```

### 1.5 Nouvelle Table `matrimonial_advantages`
Pour stocker les clauses spécifiques du contrat de mariage (Préciput, Attribution Intégrale).
```sql
CREATE TABLE matrimonial_advantages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  has_full_attribution BOOLEAN DEFAULT FALSE,
  has_preciput BOOLEAN DEFAULT FALSE,
  preciput_assets TEXT[], -- Stocke les enum keys (ex: 'RESIDENCE_PRINCIPALE')
  has_unequal_share BOOLEAN DEFAULT FALSE,
  spouse_share_percentage NUMERIC CHECK (spouse_share_percentage >= 51 AND spouse_share_percentage <= 99),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 2. GÉNÉRATION DES TYPES (Frontend)

Une fois les migrations appliquées, mets à jour les définitions TypeScript.

1.  Lance la commande de génération :
    ```bash
    npx supabase gen types typescript --project-id <TON_PROJECT_ID> > src/integrations/supabase/types.ts
    ```

2.  Vérifie que les nouveaux champs sont bien présents dans `Database['public']['Tables']`.

---

## 3. TYPES UTILITAIRES (JSONB)

Certaines données complexes sont stockées dans les colonnes `details` (JSONB). Crée ou mets jour les interfaces TypeScript pour ces objets JSON dans un fichier `src/types/json-structures.ts`.

### 3.1 Détails Actifs (`AssetDetails`)
```typescript
interface AssetDetails {
  // Démembrement (Usufruit)
  usufructuary_birth_date?: string; // YYYY-MM-DD
  usufruct_type?: "VIAGER" | "TEMPORAIRE";
  usufruct_duration_years?: number;
  is_quasi_usufruct?: boolean;
  
  // Finance & Origine
  community_funding_percentage?: number;
  asset_origin?: "PERSONAL_PROPERTY" | "COMMUNITY_PROPERTY";
  
  // Assurance-vie (Expert)
  premiums_before_70?: number;
  premiums_after_70?: number;
  subscriber_type?: "DECEASED" | "SPOUSE";
  life_insurance_contract_type?: "STANDARD" | "VIE_GENERATION" | "ANCIEN_CONTRAT";
  
  // SCI & Société
  cca_value?: number; // Compte Courant Associé
  company_liabilities?: number;
  
  // International & Retour
  location_country?: string; // ISO 2 code
  received_from_parent_id?: string; // UUID parent donateur
}
```

### 3.2 Détails Héritiers (`HeirDetails`)
```typescript
interface HeirDetails {
  // Famille Recomposée & Fente
  is_from_current_union?: boolean;
  paternal_line?: boolean; // true = Paternel, false = Maternel
  
  // Adoption
  adoption_type?: "FULL" | "SIMPLE";
  has_received_continuous_care?: boolean; // 5 ans soins continus (Adoption simple)
  
  // Option Successorale
  acceptance_option?: "PURE_SIMPLE" | "RENUNCIATION" | "BENEFIT_INVENTORY";
}
```

---

## CRITÈRES DE SUCCÈS
*   [ ] Toutes les commandes SQL passent sans erreur.
*   [ ] Le fichier `types.ts` est à jour.
*   [ ] Les interfaces JSONB sont créées et prêtes à être utilisées par les composants UI.
