from succession_engine.schemas import HeirRelation, TaxCalculationDetail, TaxBracketDetail, ExemptionType, ProfessionalExemption
from succession_engine.models import Legislation, Allowance, TaxBracket
from succession_engine.constants import (
    DISABILITY_ALLOWANCE,
    DUTREIL_EXEMPTION_RATE,
    RURAL_EXEMPTION_THRESHOLD,
    RURAL_EXEMPTION_RATE_LOW,
    RURAL_EXEMPTION_RATE_HIGH,
    FORESTRY_EXEMPTION_RATE,
)

class FiscalCalculator:
    """
    Responsible for all tax-related calculations in the succession process.
    Handles inheritance tax, allowances, and duties.
    """

    @staticmethod
    def calculate_professional_exemption(
        asset_value: float,
        exemption: ProfessionalExemption = None
    ) -> tuple:
        """
        Calcule l'exonération professionnelle applicable à un actif.
        
        Art. 787 B CGI: Pacte Dutreil - 75% d'exonération
        Art. 793 CGI: Biens ruraux - 75% jusqu'à 300K€, 50% au-delà
        Art. 793 CGI: Groupements forestiers - 75% d'exonération
        
        Args:
            asset_value: Valeur de l'actif
            exemption: Configuration de l'exonération professionnelle
            
        Returns:
            tuple: (montant_exonéré, montant_taxable)
        """
        if not exemption or exemption.exemption_type == ExemptionType.NONE:
            return 0.0, asset_value
        
        if exemption.exemption_type == ExemptionType.DUTREIL:
            # 75% d'exonération si engagements collectif ET individuel respectés
            if exemption.dutreil_is_collective and exemption.dutreil_is_individual:
                exempted = asset_value * DUTREIL_EXEMPTION_RATE
                return exempted, asset_value - exempted
        
        elif exemption.exemption_type == ExemptionType.RURAL_LEASE:
            # Bail rural long terme: 75% jusqu'à 300K€, 50% au-delà
            if exemption.lease_duration_years and exemption.lease_duration_years >= 18:
                if asset_value <= RURAL_EXEMPTION_THRESHOLD:
                    exempted = asset_value * RURAL_EXEMPTION_RATE_LOW
                else:
                    exempted_low = RURAL_EXEMPTION_THRESHOLD * RURAL_EXEMPTION_RATE_LOW
                    exempted_high = (asset_value - RURAL_EXEMPTION_THRESHOLD) * RURAL_EXEMPTION_RATE_HIGH
                    exempted = exempted_low + exempted_high
                return exempted, asset_value - exempted
        
        elif exemption.exemption_type == ExemptionType.FORESTRY:
            # Groupement forestier: 75% d'exonération
            exempted = asset_value * FORESTRY_EXEMPTION_RATE
            return exempted, asset_value - exempted
        
        # Exonération non applicable
        return 0.0, asset_value

    @staticmethod
    def calculate_inheritance_tax(
        taxable_amount: float, 
        relationship: HeirRelation,
        is_disabled: bool = False,
        prior_allowance_used: float = 0.0,
        is_adopted_simple: bool = False,
        has_continuous_care: bool = False,
        tracer: 'BusinessLogicTracer' = None
    ):
        """
        Calculates the inheritance tax based on the taxable amount and the relationship.
        Applies allowances and tax scales from the active Legislation.
        
        Args:
            taxable_amount: Amount subject to taxation
            relationship: Relationship to deceased (HeirRelation enum)
            is_disabled: If True, applies additional 159 325€ allowance (Art. 779 II CGI)
            prior_allowance_used: Allowance already used by donations within 15 years (Art. 784 CGI)
                                  This amount is deducted from the available allowance.
            tracer: Optional tracer for explicability
        
        Returns:
            tuple: (tax_amount: float, details: TaxCalculationDetail)
        """
        if tracer:
            tracer.add_sub_step(f"Fiscalité {relationship}: Part brute: {taxable_amount:,.2f}€")

        # Fetch active legislation
        try:
            legislation = Legislation.objects.get(is_active=True)
        except Legislation.DoesNotExist:
            print(f"[DEBUG FISCAL] No active legislation found!")
            if tracer: tracer.add_decision("ERROR", "Pas de législation active trouvée.")
            return 0.0, None

        # Handle adoption simple (Art. 786 CGI)
        effective_relationship = relationship
        if is_adopted_simple and relationship == HeirRelation.CHILD:
            if has_continuous_care:
                if tracer:
                    tracer.add_decision(
                        "INCLUDED", 
                        "Adoption Simple : Assimilation Enfant", 
                        "Preuve de soins continus apportée (Art. 786 CGI)."
                    )
            else:
                effective_relationship = HeirRelation.OTHER
                if tracer:
                    tracer.add_decision(
                        "EXCLUDED", 
                        "Adoption Simple : Taxation Tiers (60%)", 
                        "Absence de soins continus durant minorité (Art. 786 CGI)."
                    )

        # 1. Apply Allowances
        relation_map = {
            'CHILD': 'CHILD',
            'GRANDCHILD': 'CHILD',
            'GREAT_GRANDCHILD': 'CHILD',
            'PARENT': 'CHILD',
            'SIBLING': 'SIBLING',
            'SPOUSE': 'SPOUSE',
            'PARTNER': 'SPOUSE',
            'NEPHEW_NIECE': 'NEPHEW_NIECE',
            'AUNT_UNCLE': 'RELATIVES_UP_TO_4TH_DEGREE',
            'COUSIN': 'RELATIVES_UP_TO_4TH_DEGREE',
            'GREAT_UNCLE_AUNT': 'RELATIVES_UP_TO_4TH_DEGREE',
        }
        rel_key = str(effective_relationship.value) if hasattr(effective_relationship, 'value') else str(effective_relationship)
        db_relation = relation_map.get(rel_key, 'OTHER')
        
        allowance_obj = Allowance.objects.filter(legislation=legislation, relationship=db_relation).first()
        base_allowance = float(allowance_obj.amount) if allowance_obj else 0.0
        
        # Apply disability allowance (Art. 779 II CGI)
        disability_bonus = DISABILITY_ALLOWANCE if is_disabled else 0.0
        if is_disabled and tracer:
            tracer.add_decision("INCLUDED", "Abattement Handicap", f"+ {DISABILITY_ALLOWANCE:,.0f}€ (Art. 779 II CGI)")
        
        # Apply 15-year recall
        remaining_base_allowance = max(0.0, base_allowance - prior_allowance_used)
        if prior_allowance_used > 0 and tracer:
            tracer.add_decision("EXCLUDED", "Rappel Fiscal", f"Abattement réduit de {prior_allowance_used:,.0f}€ (Donations < 15 ans).")

        total_allowance = remaining_base_allowance + disability_bonus
        
        allowance_name = f"Abattement {db_relation}"
        if prior_allowance_used > 0:
            allowance_name += f" (- {prior_allowance_used:,.0f}€ rappel)"
        if is_disabled:
            allowance_name += " + handicap"

        if tracer:
            tracer.add_output("Abattement Total", total_allowance)

        # Spouse/Partner exemption
        if relationship in [HeirRelation.SPOUSE, HeirRelation.PARTNER]:
            if tracer:
                tracer.add_decision("EXEMPT", "Exonération Totale", "Conjoint/Partenaire (Loi TEPA).")
                tracer.end_step("Exonéré.")
            details = TaxCalculationDetail(
                relationship=relationship.value,
                gross_amount=taxable_amount,
                allowance_name="Exonération conjoint/partenaire",
                allowance_amount=taxable_amount,
                net_taxable=0.0,
                brackets_applied=[],
                total_tax=0.0
            )
            return 0.0, details

        net_taxable = max(0.0, taxable_amount - total_allowance)
        if tracer:
            tracer.add_output("Base Net Taxable", net_taxable)
        
        if net_taxable == 0:
            if tracer: tracer.end_step("Non imposable (couvert par abattement).")
            details = TaxCalculationDetail(
                relationship=relationship.value,
                gross_amount=taxable_amount,
                allowance_name=allowance_name,
                allowance_amount=total_allowance,
                net_taxable=0.0,
                brackets_applied=[],
                total_tax=0.0
            )
            return 0.0, details

        # 2. Apply Tax Scale
        tax = 0.0
        brackets_details = []
        brackets = TaxBracket.objects.filter(legislation=legislation, relationship=db_relation).order_by('min_amount')
        
        if not brackets.exists():
            if tracer: tracer.add_decision("WARNING", f"Aucun barème trouvé pour {db_relation}!")
            # Logic here falls through to return 0 tax
        
        for bracket in brackets:
            limit = float(bracket.max_amount) if bracket.max_amount else float('inf')
            rate = float(bracket.rate)
            min_amt = float(bracket.min_amount)
            
            if net_taxable > min_amt:
                upper_bound = min(net_taxable, limit)
                taxable_in_bracket = max(0.0, upper_bound - min_amt)
                tax_for_bracket = taxable_in_bracket * rate
                tax += tax_for_bracket
                
                brackets_details.append(TaxBracketDetail(
                    bracket_min=min_amt,
                    bracket_max=limit if limit != float('inf') else None,
                    rate=rate,
                    taxable_in_bracket=taxable_in_bracket,
                    tax_for_bracket=tax_for_bracket
                ))
                if tracer:
                    limit_str = f"{limit:,.0f}€" if limit != float('inf') else "∞"
                    tracer.add_decision(
                        "CALCULATION", 
                        f"Tranche {rate*100:.1f}%", 
                        f"Sur {taxable_in_bracket:,.2f}€ ({min_amt:,.0f}€ - {limit_str}) = {tax_for_bracket:,.2f}€"
                    )
        
        if tracer:
            tracer.add_output("Droits à payer", tax)
            tracer.end_step(f"Droits calculés : {tax:,.2f}€")

        details = TaxCalculationDetail(
            relationship=relationship.value,
            gross_amount=taxable_amount,
            allowance_name=allowance_name,
            allowance_amount=total_allowance,
            net_taxable=net_taxable,
            brackets_applied=brackets_details,
            total_tax=tax
        )
        
        return tax, details
