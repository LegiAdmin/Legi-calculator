"""
Matrimonial Regime Liquidation Module.

This module handles Step 1 of the succession calculation:
Liquidation du régime matrimonial (Art. 1400+ Code civil).

Separates property between deceased and surviving spouse:
- Biens propres (personal property) → 100% to deceased or spouse
- Biens communs (community property) → 50% each
- Récompenses (rewards) → adjustments based on funding
- Assurances-vie → EXCLUDED from succession (hors succession)
"""

from typing import List, Dict, TYPE_CHECKING
from succession_engine.rules.life_insurance import LifeInsuranceCalculator

if TYPE_CHECKING:
    from succession_engine.schemas import SimulationInput


class MatrimonialLiquidator:
    """
    Handles the liquidation of the matrimonial regime.
    
    Art. 1400+ Code civil:
    - Community/separation of property
    - Récompenses (rewards between estates)
    - Matrimonial advantages (clauses)
    """
    
    def __init__(self):
        """Initialize the liquidator with tracking fields."""
        self.community_total = 0.0
        self.spouse_share = 0.0
        self.life_insurance_assets = []
        self.rewards_deceased = 0.0
        self.rewards_spouse = 0.0
        self.liquidation_details = []
        self.has_full_attribution = False
        self.preciput_value = 0.0
        self.unequal_share_spouse_pct = None
    
    def liquidate(self, input_data: 'SimulationInput') -> float:
        """
        Execute the matrimonial regime liquidation.
        
        Args:
            input_data: Complete simulation input
            
        Returns:
            Net assets belonging to the deceased's estate (excluding life insurance)
        """
        deceased_assets = 0.0
        spouse_assets = 0.0
        community_assets = 0.0
        life_insurance_assets = []
        
        # Track rewards (récompenses)
        rewards_owed_to_deceased = 0.0
        rewards_owed_to_spouse = 0.0
        
        liquidation_details = []
        
        for asset in input_data.assets:
            # Check if this is a life insurance contract
            if LifeInsuranceCalculator.is_life_insurance(asset):
                # Life insurance is OUTSIDE succession
                life_insurance_assets.append(asset)
                liquidation_details.append(
                    f"  • {asset.id}: {asset.estimated_value:,.0f}€ (assurance-vie, hors succession)"
                )
                continue
            
            try:
                owner = asset.determine_owner(
                    input_data.matrimonial_regime,
                    input_data.marriage_date
                )
                
                # Calculate actual value based on indivision and CCA
                from succession_engine.schemas import OwnershipMode
                
                # Phase 10: Include Compte Courant d'Associé (CCA)
                cca_amt = getattr(asset, 'cca_value', 0.0)
                base_value = asset.estimated_value + cca_amt
                
                actual_value = base_value
                deceased_percentage = 100.0  # Default: 100% owned by deceased
                
                if asset.ownership_mode == OwnershipMode.INDIVISION and asset.indivision_details:
                    # Asset in indivision: only count deceased's share
                    deceased_percentage = asset.indivision_details.get_deceased_share_percentage()
                    actual_value = base_value * (deceased_percentage / 100.0)
                    
                    indiv_info = []
                    if asset.indivision_details.withSpouse and asset.indivision_details.spouseShare:
                        indiv_info.append(f"conjoint {asset.indivision_details.spouseShare}%")
                    if asset.indivision_details.withOthers and asset.indivision_details.othersShare:
                        indiv_info.append(f"autres {asset.indivision_details.othersShare}%")
                    
                    details_str = f"  • {asset.id}: {base_value:,.0f}€ total "
                    if cca_amt > 0:
                        details_str += f"(dont CCA: {cca_amt:,.0f}€) "
                    details_str += f"(défunt {deceased_percentage:.1f}% = {actual_value:,.0f}€, {', '.join(indiv_info)})"
                    
                    liquidation_details.append(details_str)
                else:
                    # Specific logging for single owner with CCA
                    if cca_amt > 0:
                         liquidation_details.append(
                            f"  ℹ️ {asset.id} inclut un Compte Courant d'Associé de {cca_amt:,.0f}€ (ajouté à la valeur)"
                        )
                
                # Apply main residence 20% allowance (Art. 764 bis CGI)
                main_residence_allowance = 0.0
                if asset.is_main_residence and asset.spouse_occupies_property:
                    # Allowance likely does NOT apply to CCA, only to real property value?
                    # Art 764 bis: "valeur vénale de l'immeuble". CCA is a claim.
                    # Technically we should only apply 20% to the estimated_value part.
                    # Correction: Apply allowance only to the Real Estate part (estimated_value)
                    
                    # Calculate share of real estate in actual_value
                    # If indivision, real_estate_share = estimated_value * pct
                    real_estate_share = asset.estimated_value * (deceased_percentage / 100.0)
                    
                    main_residence_allowance = real_estate_share * 0.20
                    actual_value = actual_value - main_residence_allowance
                    
                    liquidation_details.append(
                        f"  🏠 Résidence principale {asset.id}: abattement 20% sur la valeur immobilière = -{main_residence_allowance:,.0f}€ "
                        f"(valeur retenue: {actual_value:,.0f}€)"
                    )

                
                if owner == "DECEASED":
                    # Bien propre du défunt
                    deceased_assets += actual_value
                    if not (asset.ownership_mode == OwnershipMode.INDIVISION and asset.indivision_details):
                        liquidation_details.append(
                            f"  • {asset.id}: {actual_value:,.0f}€ (bien propre défunt)"
                        )
                    
                elif owner == "SPOUSE":
                    # Bien propre du conjoint → 0% dans la succession
                    spouse_assets += actual_value
                    liquidation_details.append(
                        f"  • {asset.id}: {actual_value:,.0f}€ (bien propre conjoint, exclu)"
                    )
                    
                elif owner == "COMMUNITY":
                    # Bien commun → 50% dans la succession, 50% au conjoint
                    half_value = actual_value / 2
                    community_assets += actual_value
                    
                    # Calculate REWARDS (Récompenses) if funded by personal funds
                    if asset.community_funding_percentage > 0 and asset.community_funding_percentage < 100:
                        personal_funding_percent = 100 - asset.community_funding_percentage
                        reward_amount = actual_value * (personal_funding_percent / 100)
                        
                        # Split rewards equally as we don't have that info
                        rewards_owed_to_deceased += reward_amount / 2
                        rewards_owed_to_spouse += reward_amount / 2
                        
                        deceased_assets += half_value  # Base community share
                        
                        liquidation_details.append(
                            f"  • {asset.id}: {actual_value:,.0f}€ (bien commun) → "
                            f"{half_value:,.0f}€ chacun + récompense {reward_amount:,.0f}€ "
                            f"(financé à {personal_funding_percent:.0f}% par fonds propres)"
                        )
                    else:
                        # Pure community property, no rewards
                        deceased_assets += half_value
                        liquidation_details.append(
                            f"  • {asset.id}: {actual_value:,.0f}€ (bien commun) → {half_value:,.0f}€ dans succession"
                        )
                    
            except ValueError as e:
                # Asset configuration error
                liquidation_details.append(
                    f"  ⚠️ {asset.id}: Erreur de configuration - {str(e)}"
                )
                # For safety, include full value in succession
                deceased_assets += asset.estimated_value
        
        # Apply rewards: Community owes to each spouse
        deceased_assets += rewards_owed_to_deceased
        
        # Spouse gets: base share + reward owed to them (not in succession)
        spouse_community_share = (community_assets / 2) + rewards_owed_to_spouse
        
        # Add rewards details if any
        if rewards_owed_to_deceased > 0 or rewards_owed_to_spouse > 0:
            liquidation_details.append(
                f"\n  💰 Récompenses matrimoniales :"
            )
            if rewards_owed_to_deceased > 0:
                liquidation_details.append(
                    f"    → Défunt : +{rewards_owed_to_deceased:,.0f}€"
                )
            if rewards_owed_to_spouse > 0:
                liquidation_details.append(
                    f"    → Conjoint : +{rewards_owed_to_spouse:,.0f}€ (exclu succession)"
                )
        
        # Apply matrimonial advantages
        deceased_assets = self._apply_matrimonial_advantages(
            input_data, deceased_assets, community_assets, liquidation_details
        )
        
        # Store details for later display
        self.liquidation_details = liquidation_details
        self.community_total = community_assets
        self.spouse_share = spouse_community_share
        self.life_insurance_assets = life_insurance_assets
        self.rewards_deceased = rewards_owed_to_deceased
        self.rewards_spouse = rewards_owed_to_spouse
        
        return deceased_assets
    
    def _apply_matrimonial_advantages(
        self,
        input_data: 'SimulationInput',
        deceased_assets: float,
        community_assets: float,
        liquidation_details: List[str]
    ) -> float:
        """
        Apply matrimonial advantages (Art. 1527 Code civil).
        
        Handles:
        - Clause d'attribution intégrale (Art. 1524 CC)
        - Clause de préciput (Art. 1515 CC)
        - Clause de partage inégal
        
        Returns:
            Updated deceased_assets after advantages applied
        """
        matrimonial_advantages = getattr(input_data, 'matrimonial_advantages', None)
        if not matrimonial_advantages:
            return deceased_assets
        
        # 1. Clause d'attribution intégrale (Art. 1524 CC)
        if matrimonial_advantages.has_full_attribution:
            old_deceased = deceased_assets
            deceased_assets = deceased_assets - (community_assets / 2)
            liquidation_details.append(
                f"\n  📜 CLAUSE D'ATTRIBUTION INTÉGRALE (Art. 1524 CC)"
            )
            liquidation_details.append(
                f"    → Conjoint reçoit 100% des biens communs: {community_assets:,.0f}€"
            )
            liquidation_details.append(
                f"    → Succession réduite de {old_deceased:,.0f}€ à {deceased_assets:,.0f}€"
            )
            self.has_full_attribution = True
        else:
            self.has_full_attribution = False
        
        # 2. Clause de préciput (Art. 1515 CC)
        if matrimonial_advantages.has_preciput and matrimonial_advantages.preciput_assets:
            preciput_value = 0.0
            preciput_details = []
            
            for asset in input_data.assets:
                asset_id_lower = asset.id.lower()
                for preciput_type in matrimonial_advantages.preciput_assets:
                    # Match by Property (Robust) or by Name (Fallback)
                    is_match = False
                    
                    # 1. Check Main Residence property
                    # Note: We need to import PreciputType or compare by string value if import is tricky here
                    # Since preciput_type is an Enum member (from Pydantic model), we can compare keys or values
                    if preciput_type.value == "RESIDENCE_PRINCIPALE" and asset.is_main_residence:
                        is_match = True
                    
                    # 2. Check Name string match
                    elif preciput_type.value.lower() in asset_id_lower:
                        is_match = True
                    
                    if is_match:
                        
                        asset_val = asset.estimated_value
                        preciput_value += asset_val
                        preciput_details.append(f"{asset.id}: {asset_val:,.0f}€")
                        
                        # Remove asset from Deceased Assets
                        # Logic:
                        # - If Community Asset: Deceased currently holds 50% in 'deceased_assets'.
                        #   Preciput removes it entirely to give to spouse.
                        #   So we subtract 50% of its value (the part included in deceased_assets).
                        # - If Deceased Own Property (unlikely for Preciput but possible):
                        #   We subtract 100% of its value.
                        
                        # We check origin
                        if asset.asset_origin.value == "COMMUNITY_PROPERTY":
                            deceased_assets = max(0, deceased_assets - (asset_val / 2))
                        elif asset.asset_origin.value == "PERSONAL_PROPERTY" and asset.determine_owner(input_data.matrimonial_regime, input_data.marriage_date) == "DECEASED":
                             deceased_assets = max(0, deceased_assets - asset_val)
                        
                        break
            
            if preciput_value > 0:
                liquidation_details.append(
                    f"\n  🎯 CLAUSE DE PRÉCIPUT (Art. 1515 CC)"
                )
                liquidation_details.append(
                    f"    → Conjoint prélève hors partage: {preciput_value:,.0f}€"
                )
                for detail in preciput_details:
                    liquidation_details.append(f"      • {detail}")
            
            self.preciput_value = preciput_value
        else:
            self.preciput_value = 0.0
        
        # 3. Clause de partage inégal
        if matrimonial_advantages.has_unequal_share and matrimonial_advantages.spouse_share_percentage:
            spouse_pct = matrimonial_advantages.spouse_share_percentage / 100.0
            deceased_pct = 1.0 - spouse_pct
            
            old_community_share = community_assets / 2
            new_community_share = community_assets * deceased_pct
            adjustment = old_community_share - new_community_share
            deceased_assets -= adjustment
            
            liquidation_details.append(
                f"\n  ⚖️ CLAUSE DE PARTAGE INÉGAL ({matrimonial_advantages.spouse_share_percentage:.0f}% / {100-matrimonial_advantages.spouse_share_percentage:.0f}%)"
            )
            liquidation_details.append(
                f"    → Part du défunt: {deceased_pct*100:.0f}% de {community_assets:,.0f}€ = {new_community_share:,.0f}€"
            )
            
            self.unequal_share_spouse_pct = spouse_pct
        else:
            self.unequal_share_spouse_pct = None
        
        return deceased_assets
