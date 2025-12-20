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
    
    
    def liquidate(self, input_data: 'SimulationInput', tracer: 'BusinessLogicTracer' = None) -> float:
        """
        Execute the matrimonial regime liquidation with optional tracing.
        """
        if tracer:
            tracer.start_step(
                step_number=1,
                step_name="Liquidation du régime matrimonial",
                description="Séparation des biens entre le défunt et le conjoint survivant."
            )
            tracer.explain(
                what=f"Application des règles du régime '{input_data.matrimonial_regime.value}'.",
                why="Le régime matrimonial définit la propriété des biens (Art. 1400+ CC). Seule la part du défunt entre dans la succession."
            )
            tracer.add_input("Régime Matrimonial", input_data.matrimonial_regime.value)
            tracer.add_input("Date Mariage", str(input_data.marriage_date) if input_data.marriage_date else "Non renseignée")

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
                life_insurance_assets.append(asset)
                liquidation_details.append(
                    f"  • {asset.id}: {asset.estimated_value:,.0f}€ (assurance-vie, hors succession)"
                )
                if tracer:
                    tracer.add_decision(
                        "EXCLUDED", 
                        f"Assurance-vie ({asset.id})", 
                        "Hors succession (Art. L132-12 C. Assurances)"
                    )
                continue
            
            try:
                owner = asset.determine_owner(
                    input_data.matrimonial_regime,
                    input_data.marriage_date
                )
                
                # Phase 10: Include Compte Courant d'Associé (CCA)
                cca_amt = getattr(asset, 'cca_value', 0.0)
                base_value = asset.estimated_value + cca_amt
                
                actual_value = base_value
                deceased_percentage = 100.0  # Default: 100% owned by deceased (if personal) or 100% of community
                
                # Handle Indivision
                from succession_engine.schemas import OwnershipMode
                if asset.ownership_mode == OwnershipMode.INDIVISION and asset.indivision_details:
                    deceased_percentage = asset.indivision_details.get_deceased_share_percentage()
                    actual_value = base_value * (deceased_percentage / 100.0)
                    liquidation_details.append(f"  • {asset.id}: Part indivise {deceased_percentage}% ({actual_value:,.0f}€)")
                
                # Apply main residence 20% allowance (Art. 764 bis CGI)
                main_residence_allowance = 0.0
                if asset.is_main_residence and asset.spouse_occupies_property:
                    real_estate_share = asset.estimated_value * (deceased_percentage / 100.0)
                    main_residence_allowance = real_estate_share * 0.20
                    actual_value = actual_value - main_residence_allowance
                    liquidation_details.append(
                        f"  🏠 Résidence principale {asset.id}: abattement 20% (-{main_residence_allowance:,.0f}€)"
                    )
                    if tracer:
                         tracer.add_decision(
                            "INFO",
                            f"Abattement 20% Résidence Principale ({asset.id})",
                            "Art. 764 bis CGI (Conjoint survivant occupant)"
                        )

                if owner == "DECEASED":
                    deceased_assets += actual_value
                    liquidation_details.append(f"  • {asset.id}: Bien propre du défunt ({actual_value:,.0f}€)")
                    if tracer:
                        tracer.add_decision("INCLUDED", f"{asset.id} (Propre)", f"Valeur: {actual_value:,.2f}€")
                    
                elif owner == "SPOUSE":
                    spouse_assets += actual_value
                    liquidation_details.append(f"  • {asset.id}: Bien propre du conjoint (Exclu)")
                    if tracer:
                        tracer.add_decision("EXCLUDED", f"{asset.id} (Conjoint)", "Bien propre du conjoint")
                    
                elif owner == "COMMUNITY":
                    half_value = actual_value / 2
                    community_assets += actual_value
                    
                    # Calculate REWARDS (Récompenses)
                    if asset.community_funding_percentage > 0 and asset.community_funding_percentage < 100:
                        personal_funding_percent = 100 - asset.community_funding_percentage
                        reward_amount = actual_value * (personal_funding_percent / 100)
                        
                        rewards_owed_to_deceased += reward_amount / 2
                        rewards_owed_to_spouse += reward_amount / 2
                        
                        deceased_assets += half_value
                        liquidation_details.append(
                            f"  • {asset.id}: Bien commun ({half_value:,.0f}€ part sucession) + Récompense"
                        )
                        if tracer:
                             tracer.add_decision(
                                 "INCLUDED", 
                                 f"{asset.id} (Commun)", 
                                 f"50% Valeur: {half_value:,.2f}€ + Récompense due: {reward_amount/2:,.2f}€"
                            )
                    else:
                        deceased_assets += half_value
                        liquidation_details.append(f"  • {asset.id}: Bien commun (50% = {half_value:,.0f}€)")
                        if tracer:
                            tracer.add_decision("INCLUDED", f"{asset.id} (Commun)", f"50% Valeur: {half_value:,.2f}€")
                    
            except ValueError as e:
                liquidation_details.append(f"  ⚠️ {asset.id}: Erreur - {str(e)}")
                deceased_assets += asset.estimated_value
        
        # Apply rewards
        deceased_assets += rewards_owed_to_deceased
        spouse_community_share = (community_assets / 2) + rewards_owed_to_spouse
        
        if (rewards_owed_to_deceased > 0 or rewards_owed_to_spouse > 0) and tracer:
            tracer.add_output("Récompenses dues au défunt", rewards_owed_to_deceased)
            tracer.add_output("Récompenses dues au conjoint", rewards_owed_to_spouse)

        # Apply matrimonial advantages
        deceased_assets = self._apply_matrimonial_advantages(
            input_data, deceased_assets, community_assets, liquidation_details, 
            members=input_data.members, tracer=tracer
        )
        
        # Store details
        self.liquidation_details = liquidation_details
        self.community_total = community_assets
        self.spouse_share = spouse_community_share
        self.life_insurance_assets = life_insurance_assets
        self.rewards_deceased = rewards_owed_to_deceased
        self.rewards_spouse = rewards_owed_to_spouse
        
        if tracer:
            tracer.add_output("Part Communauté Défunt", community_assets / 2)
            tracer.add_output("Biens Propres Défunt", deceased_assets - (community_assets/2) if community_assets > 0 else deceased_assets)
            tracer.add_output("Actif Brut Successoral", deceased_assets)
            tracer.end_step(f"Actif brut: {deceased_assets:,.2f}€")

        return deceased_assets
    
    def _apply_matrimonial_advantages(
        self,
        input_data: 'SimulationInput',
        deceased_assets: float,
        community_assets: float,
        liquidation_details: List[str],
        members: List = None,
        tracer: 'BusinessLogicTracer' = None
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
            # Calculate the advantage (amount spouses takes explicitly beyond 50%)
            # Standard: 50%. Full: 100%. Advantage = 50% of community.
            advantage_value = community_assets / 2
            
            # Art. 1527 CC: Action en Retranchement
            # If stepchildren exist, advantage is limited to Disposable Quota
            excess_advantage = 0.0
            
            if members:
                from succession_engine.schemas import HeirRelation
                stepchildren = [m for m in members if m.relationship == HeirRelation.CHILD and not getattr(m, 'is_from_current_union', True)]
                all_children = [m for m in members if m.relationship == HeirRelation.CHILD]
                
                if stepchildren:
                    # Calculate QD (Quotité Disponible)
                    num_children = len(all_children)
                    reserve_rate = 0.5 if num_children == 1 else (2/3 if num_children == 2 else 0.75)
                    qd_rate = 1.0 - reserve_rate
                    
                    # Fictitious Reunion for Calculation (Biens Propres + 1/2 Community)
                    # Note: deceased_assets at this point includes Personal + Rewards + 1/2 Community (before full attrib removal)
                    # Wait, deceased_assets passed effectively holds the "standard share"
                    theoretical_mass = deceased_assets 
                    
                    available_quota = theoretical_mass * qd_rate
                    
                    if advantage_value > available_quota:
                        excess_advantage = advantage_value - available_quota
                        
                        if tracer:
                             tracer.add_decision(
                                "WARNING",
                                "Action en Retranchement (Art. 1527 CC)", 
                                f"Enfants d'un autre lit détectés. Avantage ({advantage_value:,.0f}€) réduit à la QD ({available_quota:,.0f}€). Excès réintégré: {excess_advantage:,.0f}€"
                             )
                        liquidation_details.append(
                            f"  ⚠️ ACTION EN RETRANCHEMENT (Art 1527 CC): Avantage réduit de {excess_advantage:,.0f}€"
                        )

            deceased_assets = deceased_assets - (community_assets / 2) + excess_advantage
            
            liquidation_details.append(
                f"\n  📜 CLAUSE D'ATTRIBUTION INTÉGRALE (Art. 1524 CC)"
            )
            if excess_advantage > 0:
                 liquidation_details.append(
                    f"    → Conjoint reçoit: {community_assets - excess_advantage:,.0f}€ (100% com. - réduction)"
                )
                 liquidation_details.append(
                    f"    → Succession (Réserve Enfants): {excess_advantage:,.0f}€"
                )
            else:
                liquidation_details.append(
                    f"    → Conjoint reçoit 100% des biens communs: {community_assets:,.0f}€"
                )
                liquidation_details.append(
                    f"    → Succession réduite de {deceased_assets + (community_assets/2) - excess_advantage:,.0f}€ à {deceased_assets:,.0f}€"
                )

            self.has_full_attribution = True
            if tracer:
                tracer.add_decision(
                    "INFO",
                    "Clause d'attribution intégrale",
                    "Le conjoint récupère toute la communauté (Art. 1524 CC), réduisant la succession aux seuls biens propres."
                )
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
                    
                    if preciput_type.value == "RESIDENCE_PRINCIPALE" and asset.is_main_residence:
                        is_match = True
                    elif preciput_type.value.lower() in asset_id_lower:
                        is_match = True
                    
                    if is_match:
                        asset_val = asset.estimated_value
                        preciput_value += asset_val
                        preciput_details.append(f"{asset.id}: {asset_val:,.0f}€")
                        
                        value_to_subtract = asset_val
                        if asset.is_main_residence and asset.spouse_occupies_property:
                            value_to_subtract = asset_val * 0.8
                        
                        if asset.asset_origin.value == "COMMUNITY_PROPERTY":
                            deceased_assets = max(0, deceased_assets - (value_to_subtract / 2))
                        elif asset.asset_origin.value == "PERSONAL_PROPERTY" and asset.determine_owner(input_data.matrimonial_regime, input_data.marriage_date) == "DECEASED":
                             deceased_assets = max(0, deceased_assets - value_to_subtract)
                        
                        if tracer:
                            tracer.add_decision(
                                "INFO",
                                f"Préciput sur {asset.id}",
                                f"Prélevé hors part par le conjoint (Art. 1515 CC). Valeur: {asset_val:,.0f}€"
                            )
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
            
            if tracer:
                tracer.add_decision(
                    "INFO",
                    f"Partage Inégal ({matrimonial_advantages.spouse_share_percentage}% Conjoint)",
                    f"Modification du partage 50/50 de la communauté."
                )
        else:
            self.unequal_share_spouse_pct = None
        
        return deceased_assets
