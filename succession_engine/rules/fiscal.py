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
        has_continuous_care: bool = False
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
        
        Returns:
            tuple: (tax_amount: float, details: TaxCalculationDetail)
        """
        # Fetch active legislation
        try:
            legislation = Legislation.objects.get(is_active=True)
        except Legislation.DoesNotExist:
            # Return empty details if no legislation
            print(f"[DEBUG FISCAL] No active legislation found!")
            return 0.0, None

        # Handle adoption simple (Art. 786 CGI)
        # - Without continuous care: taxed as "OTHER" (60% flat rate)
        # - With continuous care 5+ years during minority: taxed as CHILD
        effective_relationship = relationship
        if is_adopted_simple and relationship == HeirRelation.CHILD:
            if not has_continuous_care:
                effective_relationship = HeirRelation.OTHER  # 60% rate

        # 1. Apply Allowances
        # Use string keys for robust matching (handles both enum and string values)
        relation_map = {
            'CHILD': 'CHILD',
            'GRANDCHILD': 'CHILD',  # Same allowance as children
            'GREAT_GRANDCHILD': 'CHILD',  # Same allowance as children
            'PARENT': 'CHILD',
            'SIBLING': 'SIBLING',
            'SPOUSE': 'SPOUSE',
            'PARTNER': 'SPOUSE',
            'NEPHEW_NIECE': 'NEPHEW_NIECE',  # Specific treatment
        }
        # Normalize to string (handles both HeirRelation enum and string values)
        rel_key = str(effective_relationship.value) if hasattr(effective_relationship, 'value') else str(effective_relationship)
        db_relation = relation_map.get(rel_key, 'OTHER')
        
        # DEBUG: Log key values
        print(f"[DEBUG FISCAL] relationship={relationship}, type={type(relationship)}")
        print(f"[DEBUG FISCAL] effective_relationship={effective_relationship}")
        print(f"[DEBUG FISCAL] rel_key={rel_key}, db_relation={db_relation}")
        
        allowance_obj = Allowance.objects.filter(legislation=legislation, relationship=db_relation).first()
        base_allowance = float(allowance_obj.amount) if allowance_obj else 0.0
        
        # DEBUG: Log allowance result
        print(f"[DEBUG FISCAL] allowance_obj={allowance_obj}, base_allowance={base_allowance}")
        
        # Apply disability allowance (Art. 779 II CGI) - cumulative
        disability_bonus = DISABILITY_ALLOWANCE if is_disabled else 0.0
        
        # Apply 15-year recall: reduce allowance by amount already used (Art. 784 CGI)
        remaining_base_allowance = max(0.0, base_allowance - prior_allowance_used)
        total_allowance = remaining_base_allowance + disability_bonus
        
        allowance_name = f"Abattement {db_relation}"
        if prior_allowance_used > 0:
            allowance_name += f" (- {prior_allowance_used:,.0f}€ rappel fiscal)"
        if is_disabled:
            allowance_name += f" + handicap ({DISABILITY_ALLOWANCE:,.0f}€)"

        # Spouse/Partner exemption
        if relationship in [HeirRelation.SPOUSE, HeirRelation.PARTNER]:
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
        
        if net_taxable == 0:
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
            details = TaxCalculationDetail(
                relationship=relationship.value,
                gross_amount=taxable_amount,
                allowance_name=allowance_name,
                allowance_amount=total_allowance,
                net_taxable=net_taxable,
                brackets_applied=[],
                total_tax=0.0
            )
            return 0.0, details
        
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
