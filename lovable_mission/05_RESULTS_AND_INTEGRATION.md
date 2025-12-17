# Mission Lovable - Étape 4 : Intégration Moteur & Résultats

**Objectif** : Orchestrer l'appel API final, gérer les dettes complexes et afficher les résultats détaillés (Traçabilité, Fiscalité).

**Fichiers concernés** : `src/components/simulation/SimulationEngine.tsx`, `src/components/results/ResultsDashboard.tsx`.

---

## 1. GESTION DU PASSIF (DETTES)

### 1.1 Liaison Dette-Actif (Art. 769 CGI)
Certaines dettes ne sont pas totalement déductibles si elles financent un bien exonéré (ex: Dutreil).
*   [ ] Dans le formulaire de dette, ajouter Select : **"Lié à l'actif..."** (Dropdown des actifs).
*   [ ] *Logique UI* : Si l'utilisateur sélectionne un actif typé "Professionnel/Dutreil" ou "Forêt", afficher un Warning immédiat :
    *   ⚠️ *"Attention : Ce bien bénéficie d'une exonération partielle. La dette ne sera déductible qu'au prorata de la partie taxable (Art. 769 CGI)."*

### 1.2 Justificatifs (Mesure anti-fraude)
*   [ ] Checkbox : **"Justificatif fourni"** (`proof_provided`).
*   [ ] *Logique* : Si dette > 1500€ (notamment obsèques) et case non cochée -> Warning dans le récapitulatif.

---

## 2. APPEL API (ORCHESTRATION)

### 2.1 Mapping des Données
Tu dois transformer les données locales (Supabase Types) en `SimulationInput` pour l'API.
*   **Attention aux Enums** : Vérifie que les strings correspondent exactement (`COMMUNITY_LEGAL` vs `propre`...). Utilise le fichier `00_MASTER_CONTEXT_API.md` comme référence absolue.
*   **Nettoyage** : Envoie uniquement les champs pertinents (ex: pas de `spouse_occupies_property` si le bien n'est pas une résidence principale).

### 2.2 Authentification
*   L'appel doit inclure le Header : `Authorization: Bearer <SESSION_TOKEN>`.
*   Gère les erreurs 401 (Session expirée) en redirigeant vers /login.

---

## 3. TABLEAU DE BORD DES RÉSULTATS

L'affichage doit être pédagogique et rassurant ("Legal Design").

### 3.1 Synthèse Visuelle (`GlobalMetrics`)
*   [ ] Cartes Clés :
    *   **Actif Net Taxable** (Masse successorale).
    *   **Droits à Payer** (Total impôt).
    *   **Taux Moyen d'Imposition**.

### 3.2 Détail par Héritier (`HeirBreakdown`)
Afficher une "Fiche Héritier" pour chacun :
1.  **Part Brute** : Ce qu'il reçoit théoriquement.
2.  **Abattements** : Liste des abattements appliqués (Parent/Enfant, Handicap, etc.).
3.  **Base Taxable**.
4.  **Calcul de l'Impôt** : Afficher le tableau des tranches (`tax_calculation_details.brackets_applied`).
    *   *Exemple UI* : "5% sur 8 072€ = 403€".
5.  **Part Nette** : Ce qu'il touche réellement à la fin.

### 3.3 Transparence du Moteur (`CalculationStep`)
Pour rassurer les professionnels, affiche l'accordéon "Détail du Calcul" :
*   Affiche la liste `calculation_steps` retournée par l'API.
*   Chaque étape doit montrer son `step_name` et `result_summary`.

### 3.4 Audit & Alertes (Nouveau Système Unifié)
L'API retourne désormais une liste structurée `alerts` (remplaçant l'ancien `warnings`).
Tu dois afficher ces alertes intelligemment selon le profil (Utilisateur vs Notaire).

#### A. Vue "Utilisateur" (Guidage)
*   **Filtrage** : Affiche uniquement `audience = 'USER'`.
*   **Affichage** :
    *   🚨 **Bloquant/Critique** (`severity='CRITICAL'`) : Banner rouge en haut de page. (ex: Réserve non respectée).
    *   ⚠️ **Important** (`severity='WARNING'`) : Toast ou Callout orange. (ex: Incohérence de dates).
    *   ℹ️ **Info** (`severity='INFO'`) : Simple note bleue.

#### B. Vue "Notaire" (Expertise)
*   Créer un onglet ou un mode **"Détail Technique & Vigilance"**.
*   **Affichage** : Table complète de toutes les alertes (USER + NOTARY).
*   **Badges** :
    *   Badge Catégorie : `LEGAL`, `FISCAL`, `DATA`, `OPTIMIZATION`.
    *   Badge Sévérité.
*   *Exemple d'usage* : Le notaire doit voir immédiatement les risques de double imposition (Alertes Internationales) ou les notes sur les anciens contrats d'assurance-vie.

---

## CRITÈRES DE SUCCÈS
*   [ ] Le JSON envoyé à l'API est valide (vérifiés via Swagger).
*   [ ] Les résultats s'affichent clairement, même pour une succession complexe.
*   [ ] L'utilisateur comprend pourquoi il paie tel montant (grâce au détail des tranches).
