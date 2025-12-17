from enum import Enum
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field, model_validator

# --- Enums ---

class MatrimonialRegime(str, Enum):
    COMMUNITY_LEGAL = "COMMUNITY_LEGAL"
    SEPARATION = "SEPARATION"
    PARTICIPATION_ACQUESTS = "PARTICIPATION_ACQUESTS"
    COMMUNITY_UNIVERSAL = "COMMUNITY_UNIVERSAL"

class AssetOrigin(str, Enum):
    PERSONAL_PROPERTY = "PERSONAL_PROPERTY"
    COMMUNITY_PROPERTY = "COMMUNITY_PROPERTY"
    INHERITANCE = "INHERITANCE"  # Bien reçu en héritage (propre)
    DONATION = "DONATION"  # Pour les actifs virtuels (donations rapportées)
    INDIVISION = "INDIVISION"

class OwnershipMode(str, Enum):
    FULL_OWNERSHIP = "FULL_OWNERSHIP"
    USUFRUCT = "USUFRUCT"
    BARE_OWNERSHIP = "BARE_OWNERSHIP"
    INDIVISION = "INDIVISION"

class UsufructType(str, Enum):
    VIAGER = "VIAGER"  # Usufruit viager (défaut) - Art. 669 I CGI
    TEMPORAIRE = "TEMPORAIRE"  # Usufruit temporaire - Art. 669 II CGI

class HeirRelation(str, Enum):
    CHILD = "CHILD"
    SPOUSE = "SPOUSE"
    PARTNER = "PARTNER"  # Pacs/Concubin
    PARENT = "PARENT"
    SIBLING = "SIBLING"
    GRANDCHILD = "GRANDCHILD"
    GREAT_GRANDCHILD = "GREAT_GRANDCHILD"  # Arrière-petits-enfants
    NEPHEW_NIECE = "NEPHEW_NIECE"  # Neveux et nièces
    OTHER = "OTHER"

class SubscriberType(str, Enum):
    DECEASED = "DECEASED"
    SPOUSE = "SPOUSE"

class TestamentDistribution(str, Enum):
    SPECIFIC_BEQUESTS = "SPECIFIC_BEQUESTS"
    LEGAL = "LEGAL"
    SPOUSE_ALL = "SPOUSE_ALL"
    CHILDREN_ALL = "CHILDREN_ALL"
    CUSTOM = "CUSTOM"

class PreciputType(str, Enum):
    """Types de biens pouvant faire l'objet d'une clause de préciput."""
    RESIDENCE_PRINCIPALE = "RESIDENCE_PRINCIPALE"
    RESIDENCE_SECONDAIRE = "RESIDENCE_SECONDAIRE"
    VEHICULE = "VEHICULE"
    MOBILIER = "MOBILIER"
    COMPTES_JOINTS = "COMPTES_JOINTS"
    AUTRE = "AUTRE"

class ExemptionType(str, Enum):
    """Types d'exonérations professionnelles (Art. 787 B, 793 CGI)."""
    NONE = "NONE"
    DUTREIL = "DUTREIL"           # Pacte Dutreil - Art. 787 B CGI
    RURAL_LEASE = "RURAL_LEASE"   # Bail rural long terme - Art. 793 CGI
    FORESTRY = "FORESTRY"         # Groupement forestier - Art. 793 CGI

class LifeInsuranceContractType(str, Enum):
    """
    Type de contrat d'assurance-vie (impact fiscal).
    
    - STANDARD: Abattement 152 500€ / 30 500€
    - VIE_GENERATION: Abattement supplémentaire de 20% avant abattement fixe (Art. 990 I bis CGI)
    - ANCIEN_CONTRAT: Exonéré (Primes < 13/10/98 et souscrit < 20/11/91)
    """
    STANDARD = "STANDARD"
    VIE_GENERATION = "VIE_GENERATION"
    ANCIEN_CONTRAT = "ANCIEN_CONTRAT"

class AcceptanceOption(str, Enum):
    """
    Options d'acceptation de la succession (Art. 768 CC).
    """
    PURE_SIMPLE = "PURE_SIMPLE"           # Acceptation pure et simple (défaut)
    BENEFIT_INVENTORY = "BENEFIT_INVENTORY" # À concurrence de l'actif net
    RENUNCIATION = "RENUNCIATION"         # Renonciation (censé n'avoir jamais hérité)

class AdoptionType(str, Enum):
    """
    Type d'adoption (impact fiscal différent).
    
    Art. 786 CGI:
    - Plénière: Mêmes droits qu'un enfant biologique (abattement 100K€)
    - Simple: Droits comme "étranger" (60%) SAUF si a reçu des soins continus 5 ans pendant minorité
    """
    FULL = "plénière"   # Adoption plénière - droits = enfant
    SIMPLE = "simple"   # Adoption simple - droits = étranger (sauf exception)

# --- Alert System ---

class AlertSeverity(str, Enum):
    INFO = "INFO"         # Information utile (ex: Abattement appliqué)
    WARNING = "WARNING"   # Attention requise, mais calcul possible (ex: Risque double imposition)
    CRITICAL = "CRITICAL" # Blocage ou illégalité probable (ex: Atteinte à la réserve)

class AlertAudience(str, Enum):
    USER = "USER"       # Langage simple, orienté action
    NOTARY = "NOTARY"   # Termes juridiques précis, points de vigilance

class AlertCategory(str, Enum):
    LEGAL = "LEGAL"           # Droit civil (Réserve, ordre héritiers...)
    FISCAL = "FISCAL"         # Droit fiscal (Abattements, tranches...)
    DATA = "DATA"             # Qualité de données (Dates incohérentes...)
    OPTIMIZATION = "OPTIMIZATION" # Pistes d'amélioration

class Alert(BaseModel):
    severity: AlertSeverity
    audience: AlertAudience
    category: AlertCategory
    message: str          # Titre court
    details: Optional[str] = None # Explication détaillée

# --- Models ---

class MatrimonialAdvantages(BaseModel):
    """
    Avantages matrimoniaux (clauses du contrat de mariage).
    
    Ces clauses modifient le partage des biens au décès.
    Art. 1527 CC: Action en retranchement possible par enfants d'autre lit.
    """
    # Clause d'attribution intégrale (Art. 1524 CC)
    # Le conjoint reçoit 100% des biens communs
    has_full_attribution: bool = False
    
    # Clause de préciput (Art. 1515 CC)
    # Le conjoint prélève certains biens avant tout partage
    has_preciput: bool = False
    preciput_assets: List[PreciputType] = Field(default_factory=list)
    
    # Clause de partage inégal
    # Ex: 70/30 au lieu de 50/50
    has_unequal_share: bool = False
    spouse_share_percentage: Optional[float] = Field(default=None, ge=51, le=99)
    
    @model_validator(mode='after')
    def validate_advantages(self):
        if self.has_preciput and not self.preciput_assets:
            raise ValueError("Clause de préciput cochée mais aucun bien sélectionné")
        if self.has_unequal_share and not self.spouse_share_percentage:
            raise ValueError("Clause de partage inégal cochée mais pourcentage non renseigné")
        return self


class IndivisionDetails(BaseModel):
    """
    Détails d'un bien en indivision.
    Permet de gérer les biens détenus en copropriété avec d'autres personnes.
    """
    withSpouse: bool = False  # Indivision avec le conjoint
    spouseShare: Optional[float] = None  # Part du conjoint (en %)
    withOthers: bool = False  # Indivision avec d'autres personnes
    othersShare: Optional[float] = None  # Part des autres (en %)
    coOwners: Optional[List[str]] = None  # Liste des co-indivisaires (noms ou IDs)
    
    def get_deceased_share_percentage(self) -> float:
        """
        Calcule la part du défunt en pourcentage.
        
        Returns:
            float: Pourcentage détenu par le défunt (0-100)
        """
        total_others = 0.0
        
        if self.withSpouse and self.spouseShare:
            total_others += self.spouseShare
        
        if self.withOthers and self.othersShare:
            total_others += self.othersShare
        
        # Part du défunt = 100% - parts des autres
        return max(0.0, 100.0 - total_others)

class ProfessionalExemption(BaseModel):
    """
    Exonération professionnelle applicable à un actif.
    
    Art. 787 B CGI: Pacte Dutreil (75% exonération parts sociales)
    Art. 793 CGI: Biens ruraux et groupements forestiers
    """
    exemption_type: ExemptionType = ExemptionType.NONE
    
    # Pacte Dutreil (Art. 787 B CGI)
    dutreil_commitment_start: Optional[date] = None  # Date signature engagement
    dutreil_is_collective: bool = False  # Engagement collectif 2 ans minimum
    dutreil_is_individual: bool = False  # Engagement individuel 4 ans minimum
    
    # Bail rural long terme (Art. 793 CGI)
    lease_start_date: Optional[date] = None
    lease_duration_years: Optional[int] = None  # Doit être >= 18 ans
    
    # Groupement forestier (Art. 793 CGI)
    forestry_certificate_date: Optional[date] = None
    
    @model_validator(mode='after')
    def validate_exemption(self):
        if self.exemption_type == ExemptionType.DUTREIL:
            if not (self.dutreil_is_collective and self.dutreil_is_individual):
                raise ValueError("Pacte Dutreil requiert engagement collectif ET individuel")
        if self.exemption_type == ExemptionType.RURAL_LEASE:
            if not self.lease_duration_years or self.lease_duration_years < 18:
                raise ValueError("Bail rural doit être d'une durée >= 18 ans")
        return self



class Asset(BaseModel):
    id: str
    estimated_value: float
    ownership_mode: OwnershipMode
    asset_origin: AssetOrigin
    acquisition_date: Optional[date] = None  # Important pour déterminer si acquis pendant mariage
    
    # Dismemberment
    usufructuary_birth_date: Optional[date] = None
    usufruct_type: UsufructType = UsufructType.VIAGER
    usufruct_duration_years: Optional[int] = None  # Pour usufruit temporaire
    is_quasi_usufruct: bool = False  # Pour quasi-usufruit (biens consomptibles)
    
    # Finance / Rewards
    community_funding_percentage: Optional[float] = Field(default=0.0, ge=0.0, le=100.0)
    
    # Indivision
    indivision_details: Optional[IndivisionDetails] = None
    
    # Main Residence - Abattement 20% (Art. 764 bis CGI)
    is_main_residence: bool = False  # Si True, abattement de 20% sur la valeur
    spouse_occupies_property: bool = False  # Condition pour l'abattement
    
    # Life Insurance
    premiums_after_70: Optional[float] = None
    premiums_before_70: Optional[float] = None
    subscriber_type: Optional[SubscriberType] = None
    life_insurance_contract_type: LifeInsuranceContractType = LifeInsuranceContractType.STANDARD
    
    # Droit de retour (Art. 738-2 CC)
    # Si le défunt a reçu ce bien d'un parent par donation, le parent peut le récupérer
    # (limité à 1/4 de la succession si le défunt meurt sans descendants)
    received_from_parent_id: Optional[str] = None  # ID du parent donateur
    
    # Professional Exemption (Art. 787 B, 793 CGI)
    professional_exemption: Optional[ProfessionalExemption] = None

    # SCI & Société (Phase 10)
    cca_value: float = Field(default=0.0, description="Compte Courant d'Associé (Créance sur la société)")
    company_liabilities: Optional[float] = Field(default=None, description="Dettes de la société (pour aide au calcul valeur parts)")
    company_real_estate_value: Optional[float] = Field(default=None, description="Valeur de l'immobilier société (pour aide au calcul)")

    # International (Phase 11)
    location_country: str = Field(default="FR", description="Pays de situation du bien (ISO 2)")

    @model_validator(mode='after')
    def check_usufructuary_date(self):
        if self.ownership_mode == OwnershipMode.BARE_OWNERSHIP and not self.usufructuary_birth_date:
            raise ValueError('usufructuary_birth_date is required when ownership_mode is BARE_OWNERSHIP')
        return self
    
    def determine_owner(self, matrimonial_regime: 'MatrimonialRegime', marriage_date: Optional[date] = None) -> str:
        """
        Détermine le propriétaire légal du bien selon le régime matrimonial.
        Returns: "DECEASED" | "SPOUSE" | "COMMUNITY" (50/50)
        """
        # Biens propres → toujours au défunt (ou conjoint si hérité par lui)
        if self.asset_origin == AssetOrigin.PERSONAL_PROPERTY:
            return "DECEASED"
        
        if self.asset_origin == AssetOrigin.INHERITANCE:
            return "DECEASED"  # Assumed inherited by deceased
        
        # Biens communs
        if self.asset_origin == AssetOrigin.COMMUNITY_PROPERTY:
            if matrimonial_regime == MatrimonialRegime.SEPARATION:
                # Impossible en séparation de biens
                raise ValueError("Community property cannot exist under separation regime")
            
            # En communauté légale : uniquement si acquis PENDANT le mariage
            if matrimonial_regime == MatrimonialRegime.COMMUNITY_LEGAL:
                if marriage_date and self.acquisition_date:
                    if self.acquisition_date >= marriage_date:
                        return "COMMUNITY"
                    else:
                        return "DECEASED"  # Acquis avant mariage = bien propre
                # Si pas de date d'acquisition, on assume communauté
                return "COMMUNITY"
            
            # En communauté universelle : tout est commun
            if matrimonial_regime == MatrimonialRegime.COMMUNITY_UNIVERSAL:
                return "COMMUNITY"
        
        # Par défaut
        return "DECEASED"

class DonationType(str, Enum):
    DON_MANUEL = "don_manuel"
    DONATION_PARTAGE = "donation_partage"
    PRESENT_USAGE = "present_usage"
    DONATION_RESIDUELLE = "donation_residuelle"
    DONATION_GRADUELLE = "donation_graduelle"

class Donation(BaseModel):
    """Donation antérieure à prendre en compte dans la succession"""
    id: str
    donation_type: DonationType
    beneficiary_name: str
    beneficiary_heir_id: Optional[str] = None  # Link to FamilyMember.id
    beneficiary_relationship: HeirRelation
    donation_date: date
    description: Optional[str] = None
    purpose: Optional[str] = None
    
    # Valeurs
    original_value: float
    current_estimated_value: Optional[float] = None  # Réévaluation au jour du décès
    
    # Fiscalité
    is_declared_to_tax: bool = False
    tax_declaration_date: Optional[date] = None
    
    # Détails immobilier (si applicable)
    property_address: Optional[str] = None
    occupation_duration_months: Optional[int] = None
    monthly_rental_value: Optional[float] = None
    
    # Détails prêt (si applicable)
    loan_amount: Optional[float] = None
    amount_repaid: Optional[float] = None
    
    # Assurance-vie (si applicable)
    insurance_contract_reference: Optional[str] = None
    premium_amount_after_70: Optional[float] = None
    
    # Acte notarié
    notary_act_reference: Optional[str] = None
    notary_signature_date: Optional[date] = None
    notary_name: Optional[str] = None
    notary_city: Optional[str] = None
    notary_details_unknown: bool = False
    notary_search_hint: Optional[str] = None
    
    # Métadonnées
    current_value_unknown: bool = False
    notes: Optional[str] = None
    
    def get_reportable_value(self) -> float:
        """
        Retourne la valeur à rapporter selon le type de donation.
        - Donation-partage : pas de rapport mais compte pour la réserve
        - Don manuel : rapport en valeur réévaluée
        """
        if self.donation_type == DonationType.DONATION_PARTAGE:
            return 0.0  # Pas de rapport pour donation-partage
        
        # Valeur actuelle si connue, sinon valeur d'origine
        return self.current_estimated_value or self.original_value
    
    def is_reportable(self) -> bool:
        """Certaines donations ne sont pas rapportables"""
        # Present d'usage : non rapportable
        if self.donation_type == DonationType.PRESENT_USAGE:
            return False
        # Donation-partage : pas de rapport civil
        if self.donation_type == DonationType.DONATION_PARTAGE:
            return False
        return True

class FamilyMember(BaseModel):
    """
    Represents an heir in the succession.
    
    Représentation (Art. 751+ CC):
    Si un héritier est prédécédé, ses propres descendants (petits-enfants)
    peuvent le représenter et recevoir sa part.
    
    Fente successorale (Art. 746-749 CC):
    En l'absence de conjoint et descendants, les biens sont divisés
    par moitié entre ligne paternelle et maternelle.
    """
    id: str
    birth_date: date
    relationship: HeirRelation
    is_from_current_union: bool = True  # Enfant du même lit (pour familles recomposées)
    
    # Handicap: Abattement supplémentaire de 159 325€ (Art. 779 II CGI)
    is_disabled: bool = False
    
    # Fente successorale (Art. 746-749): True = ligne paternelle, False = ligne maternelle
    # Utilisé pour parents, oncles, tantes, cousins quand pas de conjoint ni descendants
    paternal_line: Optional[bool] = None
    
    # Représentation: ID de l'héritier prédécédé que ce membre représente
    # Ex: Si le petit-enfant représente son parent décédé, on met l'ID du parent
    represented_heir_id: Optional[str] = None
    
    # Adoption (Art. 786 CGI)
    # Simple: Droits comme étranger (60%) sauf si soins continus 5 ans pendant minorité
    # Plénière: Mêmes droits qu'enfant biologique
    adoption_type: Optional[AdoptionType] = None
    # Pour adoption simple: si True, bénéficie des droits en ligne directe (Art. 786 CGI)
    has_received_continuous_care: bool = False
    
    # Option successorale (Art. 768 CC)
    acceptance_option: AcceptanceOption = AcceptanceOption.PURE_SIMPLE
class SpecificBequest(BaseModel):
    asset_id: str
    beneficiary_id: str
    share_percentage: Optional[float] = 100.0  # Default to 100% of the asset

class CustomShare(BaseModel):
    beneficiary_id: str
    percentage: float  # 0-100

class SpouseChoiceType(str, Enum):
    """Type de choix du conjoint survivant"""
    USUFRUCT = "USUFRUCT"  # Usufruit de la totalité
    QUARTER_OWNERSHIP = "QUARTER_OWNERSHIP"  # 1/4 en pleine propriété
    DISPOSABLE_QUOTA = "DISPOSABLE_QUOTA"  # Quotité disponible en PP (nécessite donation au dernier vivant)

class SpouseChoice(BaseModel):
    """
    Option pour le conjoint survivant.
    
    Sans donation au dernier vivant (Art. 757 CC) :
    - Usufruit de la totalité
    - 1/4 en pleine propriété
    
    Avec donation au dernier vivant (Art. 1094-1 CC) :
    - Usufruit de la totalité
    - 1/4 en pleine propriété
    - Quotité disponible en pleine propriété (1/2 si 1 enfant, 1/3 si 2, 1/4 si 3+)
    """
    choice: SpouseChoiceType

class Debt(BaseModel):
    """
    Dette à déduire de la succession (passif successoral).
    
    Les dettes déductibles réduisent l'actif successoral net.
    Exemples : hypothèques, crédits, impôts dus, frais funéraires.
    """
    id: str
    amount: float  # Montant restant dû (en valeur POSITIVE)
    debt_type: str  # "emprunt immobilier", "crédit à la consommation", "impôts", "frais funéraires", etc.
    is_deductible: bool = True
    linked_asset_id: Optional[str] = None  # Si hypothèque liée à un bien spécifique
    asset_origin: AssetOrigin  # PERSONAL_PROPERTY (dette propre) ou COMMUNITY_PROPERTY (dette commune)
    creditor: Optional[str] = None
    description: Optional[str] = None
    proof_provided: bool = False  # Justificatif fourni ?
    
    # Métadonnées optionnelles
    initial_amount: Optional[float] = None
    remaining_balance: Optional[float] = None
    
    def get_deductible_amount(self) -> float:
        """Retourne le montant déductible (négatif pour calculs)"""
        if self.is_deductible:
            return -abs(self.amount)  # Force négatif
        return 0.0

class Wishes(BaseModel):
    has_spouse_donation: bool = False
    testament_distribution: TestamentDistribution = TestamentDistribution.LEGAL
    specific_bequests: List[SpecificBequest] = Field(default_factory=list)
    custom_shares: List[CustomShare] = Field(default_factory=list)
    spouse_choice: Optional[SpouseChoice] = None  # Option du conjoint (si conjoint présent)

class SimulationInput(BaseModel):
    matrimonial_regime: MatrimonialRegime
    marriage_date: Optional[date] = None
    assets: List[Asset]
    members: List[FamilyMember]
    wishes: Optional[Wishes] = Field(default_factory=Wishes)  # Optional with default
    donations: List[Donation] = Field(default_factory=list)  # Donations antérieures
    debts: List[Debt] = Field(default_factory=list)  # Dettes à déduire
    
    # Avantages matrimoniaux (clauses du contrat de mariage)
    matrimonial_advantages: Optional[MatrimonialAdvantages] = None
    
    # International Context (Phase 11)
    residence_country: str = Field(default="FR", description="Code Pays Résidence Défunt (ISO 2)")

    # Field to store validation warnings (non-blocking)
    heir_warnings: List[str] = Field(default_factory=list)
    
    @model_validator(mode='after')
    def validate_heir_consistency(self):
        """
        Validate heir consistency and apply French succession order rules (Art. 731-755 CC).
        
        French succession order:
        1. Descendants (children, grandchildren, great-grandchildren) - exclude all others except spouse
        2. Spouse with parents - Art. 757-1 CC
        3. Spouse with siblings - Art. 757-2 CC  
        4. Parents alone - if no descendants and no spouse
        5. Siblings - if no descendants, no spouse, no parents
        6. Other relatives (nephews, etc.)
        
        This validator adds warnings but doesn't block - the calculator handles the actual exclusion.
        """
        warnings = []
        
        # Categorize heirs
        spouse = next((m for m in self.members if m.relationship in [HeirRelation.SPOUSE, HeirRelation.PARTNER]), None)
        children = [m for m in self.members if m.relationship == HeirRelation.CHILD]
        grandchildren = [m for m in self.members if m.relationship == HeirRelation.GRANDCHILD]
        great_grandchildren = [m for m in self.members if m.relationship == HeirRelation.GREAT_GRANDCHILD]
        parents = [m for m in self.members if m.relationship == HeirRelation.PARENT]
        siblings = [m for m in self.members if m.relationship == HeirRelation.SIBLING]
        nephews = [m for m in self.members if m.relationship == HeirRelation.NEPHEW_NIECE]
        
        descendants = children + grandchildren + great_grandchildren
        
        # Rule 1: Descendants exclude parents from inheritance (but keep for info)
        if descendants and parents:
            warnings.append(
                f"⚠️ Les {len(parents)} parent(s) déclaré(s) n'hériteront pas car il y a {len(descendants)} descendant(s) (Art. 734 CC)"
            )
        
        # Rule 2: Descendants exclude siblings
        if descendants and siblings:
            warnings.append(
                f"⚠️ Les {len(siblings)} frère(s)/sœur(s) n'hériteront pas car il y a des descendants (Art. 734 CC)"
            )
        
        # Rule 3: Descendants exclude nephews
        if descendants and nephews:
            warnings.append(
                f"⚠️ Les {len(nephews)} neveu(x)/nièce(s) n'hériteront pas car il y a des descendants"
            )
        
        # Rule 4: Spouse + parents = siblings excluded
        if spouse and parents and siblings and not descendants:
            warnings.append(
                f"⚠️ Les {len(siblings)} frère(s)/sœur(s) n'hériteront pas (conjoint + parents présents, Art. 757-1 CC)"
            )
        
        # Rule 5: Parents exclude siblings (if no spouse)
        if parents and siblings and not spouse and not descendants:
            warnings.append(
                f"⚠️ Application fente successorale probable (parents + frères/sœurs, Art. 746-749 CC)"
            )
        
        # Store warnings for output
        self.heir_warnings = warnings
        
        return self


class GlobalMetrics(BaseModel):
    total_estate_value: float
    legal_reserve_value: float
    disposable_quota_value: float
    total_tax_amount: float

class ReceivedAsset(BaseModel):
    """Détail d'un actif reçu via legs particulier"""
    asset_id: str
    asset_name: Optional[str] = None  # Nom lisible (ex: "Maison de vacances")
    share_percentage: float = 100.0
    value: float  # Valeur correspondant au pourcentage

class HeirBreakdown(BaseModel):
    id: str
    name: str
    legal_share_percent: float
    gross_share_value: float
    taxable_base: float
    abatement_used: float
    tax_amount: float
    net_share_value: float
    tax_calculation_details: Optional['TaxCalculationDetail'] = None
    # Legs particuliers reçus par cet héritier
    received_assets: List[ReceivedAsset] = Field(default_factory=list)

class TaxBracketDetail(BaseModel):
    """Details of a single tax bracket application"""
    bracket_min: float
    bracket_max: Optional[float]
    rate: float
    taxable_in_bracket: float
    tax_for_bracket: float

class TaxCalculationDetail(BaseModel):
    """Detailed explanation of tax calculation for an heir"""
    relationship: str
    gross_amount: float
    allowance_name: str
    allowance_amount: float
    net_taxable: float
    brackets_applied: List[TaxBracketDetail]
    total_tax: float

class CalculationStep(BaseModel):
    """A step in the calculation process"""
    step_number: int
    step_name: str
    description: str
    result_summary: str

class AssetBreakdown(BaseModel):
    """Detailed information about an asset"""
    asset_id: str
    asset_value: float
    ownership_mode: str
    asset_origin: str
    notes: List[str] = Field(default_factory=list)

class SpouseDetails(BaseModel):
    """Détails spécifiques au conjoint survivant"""
    has_usufruct: bool = False
    usufruct_value: Optional[float] = None
    usufruct_rate: Optional[float] = None  # Taux selon barème Art. 669 CGI
    bare_ownership_value: Optional[float] = None
    quarter_ownership_value: Optional[float] = None
    choice_made: Optional[str] = None  # USUFRUCT, QUARTER_OWNERSHIP, DISPOSABLE_QUOTA

class LiquidationDetails(BaseModel):
    """Détails de la liquidation du régime matrimonial"""
    regime: str
    community_assets_total: float = 0.0
    spouse_community_share: float = 0.0
    deceased_community_share: float = 0.0
    personal_assets_deceased: float = 0.0
    rewards_to_deceased: float = 0.0
    rewards_to_spouse: float = 0.0
    
    # Avantages matrimoniaux
    has_full_attribution: bool = False
    has_preciput: bool = False
    preciput_value: float = 0.0
    unequal_share_spouse_pct: Optional[float] = None
    
    # Détails textuels
    details: List[str] = Field(default_factory=list)

class FamilyContext(BaseModel):
    """Contexte familial de la succession"""
    has_spouse: bool = False
    spouse_birth_date: Optional[date] = None
    spouse_age: Optional[int] = None
    num_children: int = 0
    has_stepchildren: bool = False  # Enfants d'autre lit
    num_grandchildren_representing: int = 0  # Petits-enfants en représentation

class SuccessionOutput(BaseModel):
    """
    Schema defining the output data returned by the succession calculation.
    Enriched with all calculation details for UI display.
    """
    # Métriques globales
    global_metrics: GlobalMetrics
    
    # Détail par héritier
    heirs_breakdown: List[HeirBreakdown]
    
    # Contexte familial
    family_context: Optional[FamilyContext] = None
    
    # Détails conjoint (si applicable)
    spouse_details: Optional[SpouseDetails] = None
    
    # Liquidation du régime matrimonial
    liquidation_details: Optional[LiquidationDetails] = None
    
    # Détail des actifs
    assets_breakdown: List[AssetBreakdown] = Field(default_factory=list)
    
    # Étapes de calcul (pour transparence)
    calculation_steps: List[CalculationStep] = Field(default_factory=list)
    
    # Alertes structurées (Nouveau système)
    alerts: List[Alert] = Field(default_factory=list)

    # Alertes Legacy (Liste de strings pour backward compatibility)
    warnings: List[str] = Field(default_factory=list)
