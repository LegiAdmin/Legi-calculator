"""
Succession Calculator - Main orchestrator for succession calculations.

This module implements the complete French succession calculation pipeline
following the Code civil and Code général des impôts.

Pipeline:
1. Liquidation du régime matrimonial (Art. 1400+ CC)
2. Reconstitution de la masse successorale (Art. 843+ CC - Rapport civil)
3. Détermination de la dévolution (Art. 913+ CC - Réserve & Quotité)
4. Calcul de la fiscalité (Art. 750+ CGI)
"""

from typing import List, Dict, Tuple

from succession_engine.schemas import (
    SimulationInput, SuccessionOutput, GlobalMetrics,
    HeirBreakdown, HeirRelation, CalculationStep, AssetBreakdown,
    SpouseDetails, FamilyContext, LiquidationDetails
)
from datetime import date
from succession_engine.rules.fiscal import FiscalCalculator
from succession_engine.core.liquidation import MatrimonialLiquidator
from succession_engine.core.estate import get_reportable_donations, reconstitute_estate
from succession_engine.core.devolution import (
    calculate_legal_reserve, process_specific_bequests,
    HeirShareCalculator, check_excessive_liberalities
)


class SuccessionCalculator:
    """
    Main orchestrator for the succession calculation pipeline.
    
    Implements the 4-step succession process according to French law:
    1. Matrimonial Regime Liquidation
    2. Estate Reconstitution (with prior donations)
    3. Devolution Determination (legal reserve & shares)
    4. Taxation Calculation
    """

    def run(self, input_data: SimulationInput) -> SuccessionOutput:
        """
        Execute the complete succession calculation.
        
        Args:
            input_data: Complete simulation input including assets, heirs, wishes, donations
            
        Returns:
            SuccessionOutput with complete breakdown, taxes, and explanations
        """
        calculation_steps = []
        warnings = []
        
        # Initialize liquidator and share calculator
        liquidator = MatrimonialLiquidator()
        share_calculator = HeirShareCalculator()

        # STEP 1: Liquidation du régime matrimonial
        net_assets = liquidator.liquidate(input_data)
        
        liquidation_summary = f"Actif brut successoral: {net_assets:,.2f}€"
        if liquidator.community_total > 0:
            liquidation_summary += f" (dont {liquidator.spouse_share:,.0f}€ au conjoint survivant)"
        
        calculation_steps.append(CalculationStep(
            step_number=1,
            step_name="Liquidation du régime matrimonial",
            description="Séparation des biens du défunt et du conjoint survivant selon le régime matrimonial.",
            result_summary=liquidation_summary
        ))

        # STEP 2: Reconstitution de la masse (Rapport civil - Art. 843+ CC)
        reportable_donations, reportable_donations_value = get_reportable_donations(input_data.donations)
        net_succession_assets, total_debts, debt_warnings = reconstitute_estate(
            net_assets, reportable_donations_value, input_data.debts
        )
        # Phase 11: International Warnings
        warnings.extend(self._generate_international_warnings(input_data))

        # Add debt related warnings
        if debt_warnings:
            warnings.extend(debt_warnings)
        
        # Check for Date Consistency (Phase 9)
        warnings.extend(self._generate_consistency_warnings(input_data))

        donation_summary = (
            f"{len(reportable_donations)} donation(s) rapportable(s) pour {reportable_donations_value:,.2f}€" 
            if reportable_donations else "Aucune donation rapportable"
        )
        
        debts_summary = f", dettes: {total_debts:,.2f}€" if total_debts > 0 else ""
        
        calculation_steps.append(CalculationStep(
            step_number=2,
            step_name="Reconstitution de la masse successorale",
            description="Ajout des donations antérieures (rapport civil) et déduction des dettes.",
            result_summary=f"Actif net: {net_assets:,.2f}€ + {donation_summary}{debts_summary} = Masse: {net_succession_assets:,.2f}€"
        ))

        # STEP 3: Détermination de la dévolution (Réserve & Quotité)
        heirs = input_data.members
        reserve_fraction, reserve_description = calculate_legal_reserve(heirs)
        legal_reserve = net_succession_assets * reserve_fraction
        disposable_quota = net_succession_assets - legal_reserve
        
        # Handle specific bequests
        specific_bequests_info, bequests_total_value = process_specific_bequests(
            input_data.assets, input_data.wishes, heirs
        )
        
        # Calculate heir shares
        heir_shares = share_calculator.calculate(heirs, input_data.wishes, net_succession_assets)
        
        calculation_steps.append(CalculationStep(
            step_number=3,
            step_name="Détermination de la dévolution",
            description="Identification des héritiers et calcul de leurs parts selon la loi et les volontés du défunt.",
            result_summary=(
                f"{len(heirs)} héritier(s) - {reserve_description} - "
                f"Réserve: {legal_reserve:,.2f}€, Quotité disponible: {disposable_quota:,.2f}€, "
                f"Legs: {len(specific_bequests_info)}"
            )
        ))
        
        # Check for excessive liberalities (Art. 920+ CC - Réduction)
        warnings.extend(check_excessive_liberalities(
            reportable_donations_value, bequests_total_value,
            disposable_quota, legal_reserve, reserve_fraction
        ))

        # STEP 4: Calculate taxation and build heir breakdown
        
        # Phase 10: Calculate Global Professional Exemption (Dutreil / Rural)
        # Note: We assume exemptions are shared pro-rata to heir shares for simplicity.
        # Ideally, we should track which asset goes to whom, but simplified devolution assumes universality.
        total_professional_exemption = self._calculate_global_exemption(input_data.assets)
        
        heirs_breakdown, total_tax = self._calculate_taxation_and_breakdown(
            heirs, heir_shares, net_succession_assets,
            reportable_donations, specific_bequests_info,
            total_professional_exemption
        )
        
        calculation_steps.append(CalculationStep(
            step_number=4,
            step_name="Calcul des droits de succession",
            description="Application des abattements et du barème fiscal pour chaque héritier.",
            result_summary=f"Droits totaux: {total_tax:,.2f}€ (dont exonérations professionnelles: {total_professional_exemption:,.2f}€)"
        ))

        # STEP 5: Calculate Life Insurance Taxation (if any)
        life_insurance_total_tax = self._calculate_life_insurance_taxation(
            liquidator.life_insurance_assets, heirs, warnings, calculation_steps
        )

        # Build asset breakdown with donations
        assets_breakdown = self._build_assets_breakdown(
            input_data.assets, specific_bequests_info, reportable_donations
        )

        # Build global metrics
        metrics = GlobalMetrics(
            total_estate_value=net_succession_assets,
            legal_reserve_value=legal_reserve,
            disposable_quota_value=disposable_quota,
            total_tax_amount=total_tax
        )

        # Build SpouseDetails if spouse present
        spouse_details = self._build_spouse_details(
            heirs, share_calculator, input_data.wishes
        )
        
        # Build FamilyContext
        family_context = self._build_family_context(heirs, share_calculator)
        
        # Build LiquidationDetails
        liquidation_details_obj = self._build_liquidation_details(
            input_data, liquidator, net_assets
        )

        return SuccessionOutput(
            global_metrics=metrics,
            heirs_breakdown=heirs_breakdown,
            family_context=family_context,
            spouse_details=spouse_details,
            liquidation_details=liquidation_details_obj,
            warnings=warnings if warnings else ["✅ Aucun problème juridique détecté."],
            calculation_steps=calculation_steps,
            assets_breakdown=assets_breakdown
        )

    def _generate_international_warnings(self, input_data: SimulationInput) -> List[str]:
        """Generate warnings for international context (Phase 11)."""
        wc = []
        if getattr(input_data, 'residence_country', 'FR') != 'FR':
            wc.append(
                f"⚠️ Attention : Le défunt résidait à l'étranger ({input_data.residence_country}). "
                f"La loi successorale française peut ne pas s'appliquer (Règlement UE n°650/2012). "
                f"Vérifiez s'il y a un choix de loi (Professio Juris) ou si la loi de résidence s'applique."
            )
        for asset in input_data.assets:
            if getattr(asset, 'location_country', 'FR') != 'FR':
                 wc.append(
                    f"⚠️ Attention : Le bien '{asset.id}' est situé à l'étranger ({asset.location_country}). "
                    f"Risque de double imposition. Vérifiez les conventions fiscales internationales entre la France et ce pays."
                )
        return wc

    def _generate_consistency_warnings(self, input_data: SimulationInput) -> List[str]:
        """Generate warnings for date and regime consistency (Phase 9)."""
        wc = []
        community_regimes = ["COMMUNITY_LEGAL", "COMMUNITY_UNIVERSAL", "COMMUNITY_REDUCED_TO_ACQUESTS"]
        if input_data.matrimonial_regime.value in community_regimes and input_data.marriage_date:
            from succession_engine.schemas import AssetOrigin
            for asset in input_data.assets:
                if asset.acquisition_date:
                    is_before_marriage = asset.acquisition_date < input_data.marriage_date
                    is_during_marriage = asset.acquisition_date >= input_data.marriage_date
                    
                    if asset.asset_origin == AssetOrigin.COMMUNITY_PROPERTY and is_before_marriage:
                        wc.append(
                            f"📅 Date d'acquisition ({(asset.acquisition_date)}) antérieure au mariage ({input_data.marriage_date}) "
                            f"pour le bien '{asset.id}' déclaré 'Commun'. (Possible si apport à la communauté)"
                        )
                    elif asset.asset_origin == AssetOrigin.PERSONAL_PROPERTY and is_during_marriage:
                        wc.append(
                            f"📅 Date d'acquisition ({(asset.acquisition_date)}) pendant le mariage ({input_data.marriage_date}) "
                            f"pour le bien '{asset.id}' déclaré 'Propre'. (Vérifier clause de remploi ou origine des fonds)"
                        )
        return wc
        
    def _calculate_global_exemption(self, assets: List) -> float:
        """Calculate total amount of professional exemptions (Dutreil, Rural, etc.) on the estate."""
        total_exemption = 0.0
        for asset in assets:
            if asset.professional_exemption:
                # Apply exemption logic
                # Important: CCA (cca_value) is EXCLUDED from Dutreil, only estimated_value (parts) counts
                exempted, _ = FiscalCalculator.calculate_professional_exemption(
                    asset.estimated_value, # Only parts value
                    asset.professional_exemption
                )
                total_exemption += exempted
        return total_exemption

    def _calculate_taxation_and_breakdown(
        self,
        heirs: List,
        heir_shares: Dict[str, float],
        net_succession_assets: float,
        reportable_donations: List[Dict],
        specific_bequests_info: List[Dict],
        total_professional_exemption: float = 0.0
    ) -> Tuple[List[HeirBreakdown], float]:
        """
        Calculate taxation for each heir and build complete breakdown.
        
        For each heir:
        1. Calculate theoretical share
        2. Impute prior donations (rapport civil)
        3. Deduct professional exemptions (pro-rata)
        4. Add specific bequests
        5. Calculate tax with details
        
        Returns:
            Tuple of (list of HeirBreakdown, total tax amount)
        """
        heirs_breakdown = []
        total_tax = 0.0

        for heir in heirs:
            # Base share from devolution
            share_percent = heir_shares.get(heir.id, 0)
            gross_share = net_succession_assets * share_percent
            
            # IMPUTATION: Deduct prior donations from heir's share (Art. 843 CC)
            heir_donations = [d for d in reportable_donations if d['beneficiary_id'] == heir.id]
            donations_to_deduct = sum(d['value'] for d in heir_donations)
            net_hereditary_share = max(0, gross_share - donations_to_deduct)
            
            # Deduct Professional Exemption (Pro-rata share)
            # This reduces the TAXABLE base, but not the legal/civil share
            heir_exemption_share = total_professional_exemption * share_percent
            
            # Add specific bequests (legs particuliers)
            heir_bequests = [b for b in specific_bequests_info if b['beneficiary_id'] == heir.id]
            bequests_value = sum(b['value'] for b in heir_bequests)
            
            # Total to receive (Civil Value)
            total_civil_value = net_hereditary_share + bequests_value
            
            # Taxable Value = Civil Value - Exemptions
            # Note: We ensure taxable value doesn't go below zero
            total_taxable_value = max(0.0, total_civil_value - heir_exemption_share)
            
            # Calculate actual percentage of total estate
            actual_percentage = (total_civil_value / net_succession_assets * 100) if net_succession_assets > 0 else 0
            
            # Calculate 15-year recall: allowance already used by prior declared donations (Art. 784 CGI)
            # Only donations declared to tax authorities within 15 years consume the allowance
            prior_allowance_used = sum(
                d['value'] for d in reportable_donations 
                if d['beneficiary_id'] == heir.id and d.get('is_declared_to_tax', False)
            )
            
            # Calculate tax with detailed breakdown (including disability and 15-year recall)
            is_disabled = getattr(heir, 'is_disabled', False)
            
            # Check for adoption simple (Art. 786 CGI)
            from succession_engine.schemas import AdoptionType
            adoption_type = getattr(heir, 'adoption_type', None)
            is_adopted_simple = adoption_type == AdoptionType.SIMPLE
            has_continuous_care = getattr(heir, 'has_received_continuous_care', False)
            
            tax, tax_details = FiscalCalculator.calculate_inheritance_tax(
                total_taxable_value, heir.relationship, 
                is_disabled=is_disabled,
                prior_allowance_used=prior_allowance_used,
                is_adopted_simple=is_adopted_simple,
                has_continuous_care=has_continuous_care
            )
            total_tax += tax
            
            # Build heir breakdown
            heirs_breakdown.append(HeirBreakdown(
                id=heir.id,
                name=f"Héritier {heir.id}",
                legal_share_percent=actual_percentage,
                gross_share_value=total_civil_value, # Civil value
                taxable_base=tax_details.net_taxable,
                abatement_used=tax_details.allowance_amount,
                tax_amount=tax,
                net_share_value=total_civil_value - tax,
                tax_calculation_details=tax_details
            ))
        
        return heirs_breakdown, total_tax

    def _calculate_life_insurance_taxation(
        self,
        life_insurance_assets: List,
        heirs: List,
        warnings: List[str],
        calculation_steps: List[CalculationStep]
    ) -> float:
        """
        Calculate Life Insurance Taxation (Art. 990 I & 757 B CGI).
        
        Life insurance contracts are outside regular succession.
        """
        if not life_insurance_assets:
            return 0.0
        
        from succession_engine.rules.life_insurance import LifeInsuranceCalculator
        
        life_insurance_total_tax = 0.0
        
        for li_asset in life_insurance_assets:
            # Find beneficiary (simplified - assuming one beneficiary per contract)
            beneficiary_id = getattr(li_asset, 'beneficiary_id', heirs[0].id if heirs else None)
            beneficiary = next((h for h in heirs if h.id == beneficiary_id), heirs[0] if heirs else None)
            
            if beneficiary:
                premiums_before_70 = li_asset.premiums_before_70 or 0.0
                premiums_after_70 = li_asset.premiums_after_70 or 0.0
                
                li_tax, li_details = LifeInsuranceCalculator.calculate_life_insurance_tax(
                    premiums_before_70,
                    premiums_after_70,
                    beneficiary.relationship,
                    num_beneficiaries_after_70=len(life_insurance_assets)
                )
                
                life_insurance_total_tax += li_tax
                
                warnings.append(
                    f"📋 Assurance-vie {li_asset.id}: {li_asset.estimated_value:,.0f}€ (hors succession) - "
                    f"Droits: {li_tax:,.2f}€ "
                    f"(primes avant 70 ans: {premiums_before_70:,.0f}€, après 70 ans: {premiums_after_70:,.0f}€)"
                )
        
        calculation_steps.append(CalculationStep(
            step_number=5,
            step_name="Fiscalité des assurances-vie",
            description="Calcul spécifique pour les contrats d'assurance-vie (hors succession).",
            result_summary=f"{len(life_insurance_assets)} contrat(s) - Droits: {life_insurance_total_tax:,.2f}€"
        ))
        
        return life_insurance_total_tax

    def _build_assets_breakdown(
        self,
        assets: List,
        specific_bequests_info: List[Dict],
        reportable_donations: List[Dict]
    ) -> List[AssetBreakdown]:
        """
        Build complete asset breakdown including real assets and virtual donation assets.
        
        Returns:
            List of AssetBreakdown with notes about ownership, bequests, etc.
        """
        assets_breakdown = []
        
        # Real assets
        for asset in assets:
            notes = []
            if asset.ownership_mode.value == "BARE_OWNERSHIP":
                notes.append(f"Usufruit détenu par un tiers né le {asset.usufructuary_birth_date}")
            if asset.asset_origin.value == "COMMUNITY_PROPERTY":
                notes.append("Bien commun au couple")
            
            # Check if asset is part of a specific bequest
            asset_bequests = [b for b in specific_bequests_info if b['asset_id'] == asset.id]
            if asset_bequests:
                for bequest in asset_bequests:
                    notes.append(f"🎁 Légué à {bequest['beneficiary_name']} ({bequest['share_percentage']:.0f}%)")
            
            assets_breakdown.append(AssetBreakdown(
                asset_id=asset.id,
                asset_value=asset.estimated_value,
                ownership_mode=asset.ownership_mode.value,
                asset_origin=asset.asset_origin.value,
                notes=notes
            ))
        
        # Add donations as "virtual assets" for visibility
        for donation_info in reportable_donations:
            assets_breakdown.append(AssetBreakdown(
                asset_id=f"donation_{donation_info.get('beneficiary_id', 'unknown')}",
                asset_value=donation_info['value'],
                ownership_mode="N/A",
                asset_origin="DONATION",
                notes=[
                    f"📜 Donation du {donation_info['donation_date']} à {donation_info['beneficiary_name']}",
                    f"Type: {donation_info['type']}",
                    "Rapportée à la masse successorale"
                ]
            ))
        
        return assets_breakdown

    def _build_spouse_details(self, heirs: List, share_calculator, wishes) -> SpouseDetails:
        """Build SpouseDetails if spouse is present."""
        spouse = next(
            (h for h in heirs if h.relationship in [HeirRelation.SPOUSE, HeirRelation.PARTNER]),
            None
        )
        
        if not spouse:
            return None
        
        choice_made = None
        if wishes and wishes.spouse_choice:
            choice_made = wishes.spouse_choice.choice.value
        
        return SpouseDetails(
            has_usufruct=share_calculator.spouse_has_usufruct,
            usufruct_value=share_calculator.usufruct_value if share_calculator.spouse_has_usufruct else None,
            usufruct_rate=share_calculator.usufruct_rate if share_calculator.spouse_has_usufruct else None,
            bare_ownership_value=share_calculator.bare_ownership_value if share_calculator.spouse_has_usufruct else None,
            choice_made=choice_made
        )

    def _build_family_context(self, heirs: List, share_calculator) -> FamilyContext:
        """Build FamilyContext from heirs list."""
        spouse = next(
            (h for h in heirs if h.relationship in [HeirRelation.SPOUSE, HeirRelation.PARTNER]),
            None
        )
        children = [h for h in heirs if h.relationship == HeirRelation.CHILD]
        grandchildren_representing = [
            h for h in heirs 
            if h.relationship == HeirRelation.GRANDCHILD and h.represented_heir_id
        ]
        
        spouse_age = None
        if spouse and spouse.birth_date:
            today = date.today()
            spouse_age = today.year - spouse.birth_date.year
            if (today.month, today.day) < (spouse.birth_date.month, spouse.birth_date.day):
                spouse_age -= 1
        
        return FamilyContext(
            has_spouse=spouse is not None,
            spouse_birth_date=spouse.birth_date if spouse else None,
            spouse_age=spouse_age,
            num_children=len(children),
            has_stepchildren=share_calculator.has_stepchildren,
            num_grandchildren_representing=len(grandchildren_representing)
        )

    def _build_liquidation_details(self, input_data, liquidator, net_assets: float) -> LiquidationDetails:
        """Build LiquidationDetails from liquidator state."""
        return LiquidationDetails(
            regime=input_data.matrimonial_regime.value,
            community_assets_total=liquidator.community_total,
            spouse_community_share=liquidator.spouse_share,
            deceased_community_share=liquidator.community_total / 2 if liquidator.community_total > 0 else 0,
            personal_assets_deceased=net_assets - (liquidator.community_total / 2) if liquidator.community_total > 0 else net_assets,
            rewards_to_deceased=liquidator.rewards_deceased,
            rewards_to_spouse=liquidator.rewards_spouse,
            has_full_attribution=liquidator.has_full_attribution,
            has_preciput=liquidator.preciput_value > 0,
            preciput_value=liquidator.preciput_value,
            unequal_share_spouse_pct=liquidator.unequal_share_spouse_pct,
            details=liquidator.liquidation_details
        )
