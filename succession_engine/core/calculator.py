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
    HeirShareCalculator, check_excessive_liberalities,
    calculate_droit_de_retour
)


from succession_engine.core.alerts import AlertManager
from succession_engine.schemas import AlertAudience, AlertCategory, AlertSeverity

class SuccessionCalculator:
    """
    Main orchestrator for the succession calculation pipeline.
    """

    def run(self, input_data: SimulationInput) -> SuccessionOutput:
        """
        Execute the complete succession calculation.
        """
        calculation_steps = []
        alert_manager = AlertManager()
        
        # Initialize Tracer for Explicability (Phase 9)
        from succession_engine.core.tracer import BusinessLogicTracer
        tracer = BusinessLogicTracer()
        
        # Initialize liquidator and share calculator
        liquidator = MatrimonialLiquidator()
        share_calculator = HeirShareCalculator()

        # STEP 1: Liquidation du régime matrimonial
        net_assets = liquidator.liquidate(input_data, tracer=tracer)
        
        # STEP 2: Reconstitution de la masse (Rapport civil - Art. 843+ CC)
        tracer.start_step(
            step_number=2, 
            step_name="Reconstitution de la masse successorale",
            description="Reconstitution de la masse de calcul en réintégrant les donations antérieures et en déduisant les dettes."
        )
        tracer.explain(
            what="Calcul de la 'Masse de Calcul' (Art. 922 CC).",
            why="Pour vérifier la réserve héréditaire, on doit tenir compte de tout ce que le défunt a donné de son vivant."
        )
        
        reportable_donations, reportable_donations_value = get_reportable_donations(input_data.donations)
        
        tracer.add_input("Actif Brut", net_assets)
        if reportable_donations_value > 0:
            tracer.add_input("Donations Rapportables", reportable_donations_value)
            tracer.add_decision("INFO", f"{len(reportable_donations)} donation(s) rapportée(s)", f"Montant: {reportable_donations_value:,.2f}€")

        net_succession_assets, total_debts, debt_warnings = reconstitute_estate(
            net_assets, reportable_donations_value, input_data.debts, input_data.assets
        )
        
        if total_debts > 0:
            tracer.add_decision("INFO", "Déduction du Passif", f"Dettes déductibles: -{total_debts:,.2f}€")
            for dw in debt_warnings:
                tracer.add_decision("WARNING", "Alerte Dette", dw)
        
        tracer.add_output("Masse Successorale", net_succession_assets)
        tracer.end_step(f"Masse recalculée: {net_succession_assets:,.2f}€")
        
        # Phase 11: International Warnings
        self._generate_international_warnings(input_data, alert_manager)

        # Add debt related warnings
        if debt_warnings:
             for dw in debt_warnings:
                 alert_manager.add_legal_warning(dw, audience=AlertAudience.USER)
        
        # Check for Date Consistency (Phase 9)
        self._generate_consistency_warnings(input_data, alert_manager)
        
        # Capture Pydantic validation warnings (Heir consistency)
        if input_data.heir_warnings:
            for hw in input_data.heir_warnings:
                alert_manager.add_legal_warning(hw, audience=AlertAudience.USER)
        
        # Phase 16: Droit de Retour (Art 738-2 CC)
        # Check if assets return to parents before reserve calculation
        return_amounts, total_return, return_warnings = calculate_droit_de_retour(
            input_data.assets, input_data.members, net_succession_assets
        )
        if total_return > 0:
            net_succession_assets -= total_return
            if return_warnings:
                for rw in return_warnings:
                    alert_manager.add_legal_warning(rw, audience=AlertAudience.NOTARY)
            
            calculation_steps.append(CalculationStep(
                step_number=2, # sub-step
                step_name="Application Droit de Retour (Art. 738-2 CC)",
                description="Les biens reçus par donation d'ascendants retournent à ces derniers (en l'absence de descendants).",
                result_summary=f"Valeur retournée: {total_return:,.2f}€. Nouvelle masse: {net_succession_assets:,.2f}€"
            ))

        # STEP 3: Détermination de la dévolution (Réserve & Quotité)
        heirs = input_data.members
        reserve_fraction, reserve_description = calculate_legal_reserve(heirs)
        legal_reserve = net_succession_assets * reserve_fraction
        disposable_quota = net_succession_assets - legal_reserve
        
        # Handle specific bequests
        specific_bequests_info, bequests_total_value, bequest_warnings = process_specific_bequests(
            input_data.assets, input_data.wishes, heirs
        )
        
        # Add bequest over-allocation warnings
        for bw in bequest_warnings:
            alert_manager.add(AlertSeverity.WARNING, AlertAudience.USER, AlertCategory.LEGAL, bw)
        
        # Calculate heir shares (Instrumented)
        heir_shares = share_calculator.calculate(heirs, input_data.wishes, net_succession_assets, tracer=tracer)
        
        # Check for excessive liberalities (Art. 920+ CC - Réduction)
        excessive_lib_warnings = check_excessive_liberalities(
            reportable_donations_value, bequests_total_value,
            disposable_quota, legal_reserve, reserve_fraction
        )
        for elw in excessive_lib_warnings:
            alert_manager.add(AlertSeverity.CRITICAL, AlertAudience.USER, AlertCategory.LEGAL, elw)

        # Phase 10: Early Calculation of Life Insurance for 757 B Reintegration
        # (Must be done before Taxation Step 4 to inject taxable base addbacks)
        av_tax_990i, av_757b_addbacks, _ = self._calculate_life_insurance_taxation(
            liquidator.life_insurance_assets, heirs, alert_manager, tracer=tracer
        )
        if av_757b_addbacks and tracer:
             total_757b = sum(av_757b_addbacks.values())
             tracer.add_decision("INFO", "Assurance-Vie 757B", f"Réintégration de primes > 70 ans dans la succession: {total_757b:,.2f}€")

        # STEP 4: Calculate taxation and build heir breakdown
        tracer.start_step(
            step_number=4,
            step_name="Calcul des droits de succession",
            description="Application des abattements et du barème fiscal pour chaque héritier."
        )
        tracer.explain(
            what="Calcul de l'impôt sur la part reçue.",
            why="Les droits de succession sont calculés sur la part nette taxable après abattement (Art. 777+ CGI)."
        )
        
        # Phase 10: Calculate Global Professional Exemption (Dutreil / Rural)
        # Note: We assume exemptions are shared pro-rata to heir shares for simplicity.
        # Ideally, we should track which asset goes to whom, but simplified devolution assumes universality.
        total_professional_exemption = self._calculate_global_exemption(input_data.assets)
        if total_professional_exemption > 0:
            tracer.add_decision("INFO", "Exonération Professionnelle", f"Montant total exonéré: {total_professional_exemption:,.2f}€")
        
        spouse_heir = next((h for h in heirs if h.relationship in [HeirRelation.SPOUSE, HeirRelation.PARTNER]), None)
        spouse_id = spouse_heir.id if spouse_heir else None

        heirs_breakdown, total_tax = self._calculate_taxation_and_breakdown(
            heirs, heir_shares, net_succession_assets,
            reportable_donations, specific_bequests_info,
            total_professional_exemption,
            spouse_id=spouse_id,
            usufruct_value=share_calculator.usufruct_value if share_calculator.spouse_has_usufruct else 0.0,
            has_usufruct=share_calculator.spouse_has_usufruct,
            heir_757b_addbacks=av_757b_addbacks,
            tracer=tracer
        )
        
        # Trace tax results for each heir
        for hb in heirs_breakdown:
            details_text = f"Part brute: {hb.gross_share_value:,.2f}€ | Abattement: {hb.abatement_used:,.2f}€ | Taxable: {hb.taxable_base:,.2f}€"
            tracer.add_decision("INFO", f"Fiscalité {hb.id}", details_text)
            if hb.tax_amount > 0:
                tracer.add_decision("WARNING", f"Droits {hb.id}", f"A payer: {hb.tax_amount:,.2f}€")
        
        tracer.add_output("Droits Totaux", total_tax)
        tracer.end_step(f"Droits totaux à payer: {total_tax:,.2f}€")

        # STEP 5: Add Life Insurance Tax Summary to Tracer
        if liquidator.life_insurance_assets and tracer:
            tracer.add_output("Droits Assurance-Vie Total (990 I)", av_tax_990i)
            # Detailed steps are already logged by LifeInsuranceCalculator called in Phase 10
            
            life_insurance_total_tax = av_tax_990i
        else:
            life_insurance_total_tax = 0.0

        # Build asset breakdown with donations
        assets_breakdown = self._build_assets_breakdown(
            input_data.assets, specific_bequests_info, reportable_donations
        )

        # Build global metrics
        metrics = GlobalMetrics(
            total_estate_value=net_succession_assets,
            legal_reserve_value=legal_reserve,
            disposable_quota_value=disposable_quota,
            total_tax_amount=total_tax + life_insurance_total_tax
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
        
        # Get alerts and legacy warnings
        final_alerts = alert_manager.alerts
        legacy_warnings = alert_manager.get_legacy_warnings()
        if not legacy_warnings:
            legacy_warnings = ["✅ Aucun problème juridique détecté."]

        return SuccessionOutput(
            global_metrics=metrics,
            heirs_breakdown=heirs_breakdown,
            family_context=family_context,
            spouse_details=spouse_details,
            liquidation_details=liquidation_details_obj,
            alerts=final_alerts,
            warnings=legacy_warnings,
            calculation_steps=tracer.get_steps(),
            assets_breakdown=assets_breakdown
        )

    def _generate_international_warnings(self, input_data: SimulationInput, alert_manager: AlertManager):
        """Generate warnings for international context (Phase 11)."""
        if getattr(input_data, 'residence_country', 'FR') != 'FR':
            alert_manager.add(
                AlertSeverity.WARNING, AlertAudience.NOTARY, AlertCategory.LEGAL,
                f"Résidence à l'étranger ({input_data.residence_country})",
                "Risque d'application d'une loi successorale étrangère (Règlement UE n°650/2012). Vérifier Professio Juris."
            )

        for asset in input_data.assets:
            if getattr(asset, 'location_country', 'FR') != 'FR':
                 alert_manager.add(
                    AlertSeverity.WARNING, AlertAudience.NOTARY, AlertCategory.FISCAL,
                    f"Bien à l'étranger ({asset.id} en {asset.location_country})",
                    "Risque de double imposition. Vérifiez les conventions fiscales bilatérales."
                )


    def _generate_consistency_warnings(self, input_data: SimulationInput, alert_manager: AlertManager):
        """Generate warnings for date and regime consistency (Phase 9)."""
        community_regimes = ["COMMUNITY_LEGAL", "COMMUNITY_UNIVERSAL", "COMMUNITY_REDUCED_TO_ACQUESTS"]
        if input_data.matrimonial_regime.value in community_regimes and input_data.marriage_date:
            from succession_engine.schemas import AssetOrigin
            for asset in input_data.assets:
                if asset.acquisition_date:
                    is_before_marriage = asset.acquisition_date < input_data.marriage_date
                    is_during_marriage = asset.acquisition_date >= input_data.marriage_date
                    
                    if asset.asset_origin == AssetOrigin.COMMUNITY_PROPERTY and is_before_marriage:
                        alert_manager.add_data_warning(
                            f"Incohérence Date/Régime : Bien '{asset.id}' acquis AVANT mariage déclaré 'Commun'. (Possible si apport)"
                        )
                    elif asset.asset_origin == AssetOrigin.PERSONAL_PROPERTY and is_during_marriage:
                        alert_manager.add_data_warning(
                            f"Incohérence Date/Régime : Bien '{asset.id}' acquis PENDANT mariage déclaré 'Propre'. (Clause de remploi ?)"
                        )
        
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
        total_professional_exemption: float = 0.0,
        spouse_id: str = None,
        usufruct_value: float = 0.0,
        has_usufruct: bool = False,
        heir_757b_addbacks: Dict[str, float] = None,
        tracer: 'BusinessLogicTracer' = None
    ) -> Tuple[List[HeirBreakdown], float]:
        """
        Calculate taxation for each heir and build complete breakdown.
        Includes 757 B reintegration.
        """
        heirs_breakdown = []
        total_tax = 0.0
        heir_757b_addbacks = heir_757b_addbacks or {}
        
        # Calculate total value of specific bequests (charged to estate)
        bequests_total_value_sum = sum(b['value'] for b in specific_bequests_info)
        
        # Determine distributable residue for legal heirs
        # Legal shares apply to the residue (Active Assets - Liabilities - Specific Bequests)
        distributable_residue = max(0.0, net_succession_assets - bequests_total_value_sum)

        for heir in heirs:
            # Base share from devolution
            share_percent = heir_shares.get(heir.id, 0)
            gross_share = distributable_residue * share_percent
            
            # USUFRUCT ADJUSTMENT
            if has_usufruct and usufruct_value > 0:
                if heir.id == spouse_id:
                    # Spouse gets the Usufruct Value added to their share (which might be 0% in PP)
                    gross_share += usufruct_value
                elif heir.relationship == HeirRelation.CHILD: # Assuming children are the bare owners
                    # Deduct usufruct value from bare owners proportionally
                    gross_share -= usufruct_value * share_percent
            
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
            
            # --- 757 B Reintegration (Life Insurance Premiums > 70) ---
            addback_757b = heir_757b_addbacks.get(heir.id, 0.0)
            
            # Taxable Value = Civil Value + 757B - Exemptions
            gross_taxable_value = total_civil_value + addback_757b
            
            # Ensure taxable value doesn't go below zero
            total_taxable_value = max(0.0, gross_taxable_value - heir_exemption_share)
            
            # Metrics
            actual_percentage = (total_civil_value / net_succession_assets * 100) if net_succession_assets > 0 else 0
            
            # Trace
            if tracer:
                 details = f"Civil: {total_civil_value:,.0f}€"
                 if addback_757b > 0:
                     details += f" + AV 757B: {addback_757b:,.0f}€"
                 if heir_exemption_share > 0:
                     details += f" - Exon. Pro: {heir_exemption_share:,.0f}€"
                 tracer.add_decision("INFO", f"Base Taxable {heir.id}", details)

            # Calculate 15-year recall: allowance already used by prior declared donations (Art. 784 CGI)
            prior_allowance_used = sum(
                d['value'] for d in reportable_donations 
                if d['beneficiary_id'] == heir.id and d.get('is_declared_to_tax', False)
            )
            
            is_disabled = getattr(heir, 'is_disabled', False)
            from succession_engine.schemas import AdoptionType
            adoption_type = getattr(heir, 'adoption_type', None)
            is_adopted_simple = adoption_type == AdoptionType.SIMPLE
            has_continuous_care = getattr(heir, 'has_received_continuous_care', False)
            
            tax, tax_details = FiscalCalculator.calculate_inheritance_tax(
                total_taxable_value, heir.relationship, 
                is_disabled=is_disabled,
                prior_allowance_used=prior_allowance_used,
                is_adopted_simple=is_adopted_simple,
                has_continuous_care=has_continuous_care,
                tracer=tracer
            )
            total_tax += tax
            
            if tracer and tax > 0:
                 tracer.add_decision("INCLUDED", f"Taxation {heir.id}", f"Droits: {tax:,.2f}€")
            
            # Build received_assets list from specific bequests
            from succession_engine.schemas import ReceivedAsset, ExplanationKey
            received_assets = [
                ReceivedAsset(
                    asset_id=b['asset_id'],
                    asset_name=b.get('asset_name', b['asset_id']),
                    share_percentage=b.get('share_percentage', 100.0),
                    value=b['value']
                )
                for b in heir_bequests
            ]
            
            # Build explanation keys for this heir
            heir_explanation_keys = []
            
            # Explain share source
            if heir.relationship == HeirRelation.CHILD:
                num_children = len([h for h in heirs if h.relationship == HeirRelation.CHILD])
                heir_explanation_keys.append(ExplanationKey(
                    key="SHARE_CHILDREN_EQUAL",
                    context={"num_children": num_children}
                ))
            elif heir.relationship == HeirRelation.SPOUSE:
                heir_explanation_keys.append(ExplanationKey(
                    key="SHARE_SPOUSE",
                    context={"share_percent": actual_percentage}
                ))
            elif heir.relationship == HeirRelation.GRANDCHILD and heir.represented_heir_id:
                heir_explanation_keys.append(ExplanationKey(
                    key="SHARE_REPRESENTATION",
                    context={"represented_id": heir.represented_heir_id}
                ))
            elif heir.relationship == HeirRelation.SIBLING:
                heir_explanation_keys.append(ExplanationKey(
                    key="SHARE_SIBLINGS",
                    context={"share_percent": actual_percentage}
                ))
            
            # Explain abatement
            if tax_details.allowance_amount > 0:
                if heir.relationship == HeirRelation.CHILD:
                    heir_explanation_keys.append(ExplanationKey(
                        key="ABATEMENT_CHILD_100K",
                        context={"amount": tax_details.allowance_amount}
                    ))
                elif heir.relationship == HeirRelation.SIBLING:
                    heir_explanation_keys.append(ExplanationKey(
                        key="ABATEMENT_SIBLING_15K",
                        context={"amount": tax_details.allowance_amount}
                    ))
            
            if is_disabled:
                heir_explanation_keys.append(ExplanationKey(
                    key="ABATEMENT_DISABILITY_159K",
                    context={}
                ))
            
            if prior_allowance_used > 0:
                heir_explanation_keys.append(ExplanationKey(
                    key="ABATEMENT_CONSUMED_15Y",
                    context={"amount_used": prior_allowance_used}
                ))
            
            # Explain tax exemption for spouse
            if heir.relationship in [HeirRelation.SPOUSE, HeirRelation.PARTNER]:
                heir_explanation_keys.append(ExplanationKey(
                    key="TAX_SPOUSE_EXEMPT",
                    context={}
                ))
            
            # Build heir breakdown
            heirs_breakdown.append(HeirBreakdown(
                id=heir.id,
                name=heir.id,
                relationship=heir.relationship,
                legal_share_percent=share_percent * 100,
                gross_share_value=total_civil_value,
                taxable_base=tax_details.net_taxable,
                abatement_used=tax_details.allowance_amount,
                tax_amount=tax,
                net_share_value=(total_civil_value + addback_757b) - tax,
                tax_calculation_details=tax_details,
                received_assets=received_assets,
                explanation_keys=heir_explanation_keys
            ))
        
        return heirs_breakdown, total_tax

    def _calculate_life_insurance_taxation(
        self,
        life_insurance_assets: List,
        heirs: List,
        alert_manager: AlertManager,
        tracer=None
    ) -> Tuple[float, Dict[str, float], List[Dict]]:
        """
        Calculate Life Insurance Taxation (Art. 990 I & 757 B CGI).
        Returns:
            - total_tax_990i: Tax amount for premiums < 70 (Art 990 I)
            - heir_757b_addbacks: Dictionary {heir_id: taxable_base_757b} to be added to succession mass
            - trace_info: List of decisions/info to be logged by the tracer later
        """
        if not life_insurance_assets:
            return 0.0, {}, []
        
        from succession_engine.rules.life_insurance import LifeInsuranceCalculator
        
        life_insurance_total_tax_990i = 0.0
        heir_757b_addbacks = {}
        trace_info = []
        
        for li_asset in life_insurance_assets:
            # Determine beneficiaries list
            beneficiaries = []
            if li_asset.life_insurance_beneficiaries:
                beneficiaries = li_asset.life_insurance_beneficiaries
            else:
                # Legacy fallback
                beneficiary_id = getattr(li_asset, 'beneficiary_id', heirs[0].id if heirs else None)
                if beneficiary_id:
                     from succession_engine.schemas import LifeInsuranceBeneficiary, OwnershipMode
                     beneficiaries.append(
                         LifeInsuranceBeneficiary(
                             beneficiary_id=beneficiary_id,
                             share_percent=100.0,
                             ownership_type=OwnershipMode.FULL_OWNERSHIP
                         )
                     )

            # Pre-scan for Usufructuary to determine rate (Art 669 CGI)
            from succession_engine.schemas import OwnershipMode
            usufruct_rate = 1.0 # Default 100% if no dismemberment
            usufruct_beneficiary = next((b for b in beneficiaries if b.ownership_type == OwnershipMode.USUFRUCT), None)
            
            if usufruct_beneficiary:
                # Find age of this beneficiary
                u_heir = next((h for h in heirs if h.id == usufruct_beneficiary.beneficiary_id), None)
                if u_heir and u_heir.birth_date:
                    age = date.today().year - u_heir.birth_date.year
                    # Simple fiscal scale (Art 669 CGI)
                    if age < 21: usufruct_rate = 0.9
                    elif age < 31: usufruct_rate = 0.8
                    elif age < 41: usufruct_rate = 0.7
                    elif age < 51: usufruct_rate = 0.6
                    elif age < 61: usufruct_rate = 0.5
                    elif age < 71: usufruct_rate = 0.4
                    elif age < 81: usufruct_rate = 0.3
                    elif age < 91: usufruct_rate = 0.2
                    else: usufruct_rate = 0.1
                    
                    if tracer:
                         tracer.add_decision("INFO", f"Démembrement AV {li_asset.id}", f"Usufruitier {u_heir.id} ({age} ans) -> Taux {usufruct_rate*100:.0f}%")

            # Phase 15: Gestion des contrats spécifiques
            from succession_engine.schemas import LifeInsuranceContractType
            contract_type = getattr(li_asset, 'life_insurance_contract_type', LifeInsuranceContractType.STANDARD)
            
            premiums_before_70 = li_asset.premiums_before_70 or 0.0
            premiums_after_70 = li_asset.premiums_after_70 or 0.0

            # Cas 1: Exonéré (Ancien Contrat)
            if contract_type == LifeInsuranceContractType.ANCIEN_CONTRAT:
                alert_manager.add_fiscal_note(
                    f"Assurance-vie {li_asset.id}: Exonérée",
                    "Ancien contrat (primes < 98 / souscrit < 91) - Hors succession."
                )
                if tracer:
                    tracer.add_decision(
                        "INFO", 
                        f"Contrat {li_asset.id}", 
                        "Exonéré (Ancien Contrat)"
                    )
                continue

            # Process each beneficiary
            for ben_info in beneficiaries:
                beneficiary = next((h for h in heirs if h.id == ben_info.beneficiary_id), None)
                if not beneficiary:
                    continue
                
                share_fraction = ben_info.share_percent / 100.0
                
                # Adjust share for dismemberment
                from succession_engine.schemas import OwnershipMode
                if ben_info.ownership_type == OwnershipMode.USUFRUCT:
                    share_fraction *= usufruct_rate
                elif ben_info.ownership_type == OwnershipMode.BARE_OWNERSHIP:
                    # Assumption: Bare owners share the complement
                    # If multiple bare owners, their share_percent sums to 100?
                    # SC_CHAOS_2: NP1(25) + NP2(25) + NP3(50) = 100.
                    # Adjusted = 25% of Remainder(40%) = 10%. Correct.
                    share_fraction *= (1.0 - usufruct_rate)
                
                ben_premiums_before_70 = premiums_before_70 * share_fraction
                ben_premiums_after_70 = premiums_after_70 * share_fraction

                # Cas 2: Vie-Génération (-20% abattement sur l'assiette avant abattement fixe)
                adjusted_primes_before_70 = ben_premiums_before_70
                if contract_type == LifeInsuranceContractType.VIE_GENERATION:
                    adjusted_primes_before_70 = ben_premiums_before_70 * 0.80
                
                # Check num beneficiaries for 757 B splitting
                num_bens = len(beneficiaries) if premiums_after_70 > 0 else 1

                li_tax, li_details = LifeInsuranceCalculator.calculate_life_insurance_tax(
                    adjusted_primes_before_70,
                    ben_premiums_after_70,
                    beneficiary.relationship,
                    num_beneficiaries_after_70=num_bens,
                    tracer=tracer
                )
                
                # Accumulate 990 I tax
                life_insurance_total_tax_990i += li_tax
                
                # Accumulate 757 B addback
                taxable_base_757b = li_details.get('taxable_base_757b', 0.0)
                if taxable_base_757b > 0:
                     current_addback = heir_757b_addbacks.get(beneficiary.id, 0.0)
                     heir_757b_addbacks[beneficiary.id] = current_addback + taxable_base_757b
                     
                     if tracer:
                         tracer.add_decision(
                            "INFO",
                            f"Réintégration 757B {li_asset.id} -> {beneficiary.id}",
                            f"Base taxable {taxable_base_757b:,.2f}€ ajoutée à la succession."
                         )
                
                # Details string for alerts/trace
                details_str = f"sur base part {adjusted_primes_before_70:,.0f}€"
                if ben_premiums_after_70 > 0:
                    details_str += f" + primes>70: {ben_premiums_after_70:,.0f}€ (Art. 757B)"

                if li_tax > 0:
                    alert_manager.add_fiscal_note(
                        f"Assurance-vie {li_asset.id} ({beneficiary.id})",
                        f"Droits 990 I: {li_tax:,.2f}€"
                    )
                    if tracer:
                        tracer.add_decision(
                            "INFO",
                            f"Taxe 990 I {li_asset.id} -> {beneficiary.id}", 
                            f"Taxe: {li_tax:,.2f}€ ({details_str})"
                        )
                elif taxable_base_757b > 0:
                     # Just informational if no 990 I tax but 757 B reintegration
                     pass
        
        return life_insurance_total_tax_990i, heir_757b_addbacks, trace_info

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
