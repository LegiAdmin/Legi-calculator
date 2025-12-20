"""
Life Insurance Tax Calculator.

Handles specific French taxation of life insurance contracts (assurance-vie).

Key differences from regular inheritance:
1. Life insurance is OUTSIDE the succession (hors succession)
2. Different taxation based on when premiums were paid:
   - Before 70 years old: 152,500€ allowance per beneficiary (Art. 990 I CGI)
   - After 70 years old: 30,500€ global allowance shared among all beneficiaries (Art. 757 B CGI)
3. Progressive tax rates apply after allowances
"""

from typing import Dict, List, Tuple
from succession_engine.schemas import HeirRelation
from succession_engine.constants import LIFE_INSURANCE_ALLOWANCE_BEFORE_70, LIFE_INSURANCE_ALLOWANCE_AFTER_70


class LifeInsuranceCalculator:
    """
    Calculate taxation on life insurance contracts according to French law.
    
    Art. 990 I CGI (premiums before 70) and Art. 757 B CGI (premiums after 70).
    """
    
    @staticmethod
    def calculate_life_insurance_tax(
        premiums_before_70: float,
        premiums_after_70: float,
        beneficiary_relationship: HeirRelation,
        num_beneficiaries_after_70: int = 1,
        tracer: 'BusinessLogicTracer' = None
    ) -> Tuple[float, Dict]:
        """
        Calculate tax on life insurance benefits.
        
        Args:
            premiums_before_70: Total premiums paid before deceased turned 70
            premiums_after_70: Total premiums paid after deceased turned 70
            beneficiary_relationship: Relationship of beneficiary to deceased
            num_beneficiaries_after_70: Number of beneficiaries sharing after-70 allowance
            tracer: Optional tracer for explicability
            
        Returns:
            Tuple of (total_tax, details_dict)
        """
        total_tax = 0.0
        details = {
            'premiums_before_70': premiums_before_70,
            'premiums_after_70': premiums_after_70,
            'tax_before_70': 0.0,
            'tax_after_70': 0.0,
            'allowance_before_70_used': 0.0,
            'allowance_after_70_used': 0.0,
            'total_tax': 0.0
        }
        
        # ===== TAXATION OF PREMIUMS PAID BEFORE 70 =====
        # Art. 990 I du CGI: 152,500€ allowance PER beneficiary
        if premiums_before_70 > 0:
            if tracer:
                tracer.start_step(4, "Assurance Vie (990 I)", "Primes versées avant 70 ans")
                tracer.add_input("Montant Primes < 70", premiums_before_70)

            allowance_before_70 = LIFE_INSURANCE_ALLOWANCE_BEFORE_70
            taxable_before_70 = max(0, premiums_before_70 - allowance_before_70)
            
            details['allowance_before_70_used'] = min(premiums_before_70, allowance_before_70)
            
            if tracer:
                tracer.add_decision("INFO", "Abattement 990 I", f"{details['allowance_before_70_used']:,.0f}€ (Max 152 500€)")
            
            if taxable_before_70 > 0:
                # Progressive rates after allowance:
                # - 0 to 700,000€: 20%
                # - Above 700,000€: 31.25%
                if taxable_before_70 <= 700_000:
                    tax_before_70 = taxable_before_70 * 0.20
                    if tracer: tracer.add_decision("CALCULATION", "Taxe 20%", f"Sur {taxable_before_70:,.2f}€")
                else:
                    tax_low = 700_000 * 0.20
                    tax_high = (taxable_before_70 - 700_000) * 0.3125
                    tax_before_70 = tax_low + tax_high
                    if tracer: 
                        tracer.add_decision("CALCULATION", "Taxe Mixte (20% + 31.25%)", f"Sur {taxable_before_70:,.2f}€")
                
                details['tax_before_70'] = tax_before_70
                total_tax += tax_before_70
            
            if tracer: tracer.end_step(f"Taxe AV (990 I): {tax_before_70:,.2f}€")
        
        # ===== TAXATION OF PREMIUMS PAID AFTER 70 =====
        # Art. 757 B du CGI: 30,500€ GLOBAL allowance shared among ALL beneficiaries
        if premiums_after_70 > 0:
            if tracer:
                tracer.start_step(4, "Assurance Vie (757 B)", "Primes versées après 70 ans")
                tracer.add_input("Montant Primes > 70", premiums_after_70)

            # Global allowance divided among beneficiaries
            allowance_after_70 = LIFE_INSURANCE_ALLOWANCE_AFTER_70 / num_beneficiaries_after_70
            taxable_after_70 = max(0, premiums_after_70 - allowance_after_70)
            
            details['allowance_after_70_used'] = min(premiums_after_70, allowance_after_70)
            
            if tracer:
                tracer.add_decision("INFO", "Abattement 757 B Partagé", f"{details['allowance_after_70_used']:,.0f}€ (30 500€ / {num_beneficiaries_after_70})")
            
            if taxable_after_70 > 0:
                # Art 757 B: This amount is NOT taxed separately but reintegrated into succession mass.
                # We return 0 tax here, but provide the base for the orchestrator to add to the heir's share.
                tax_after_70 = 0.0
                
                details['tax_after_70'] = 0.0
                details['taxable_base_757b'] = taxable_after_70
                
                if tracer:
                    tracer.add_decision("WARNING", "Réintégration DMTG", f"Le solde ({taxable_after_70:,.0f}€) est ajouté à l'actif successoral taxable.")
            else:
                details['taxable_base_757b'] = 0.0
                if tracer: tracer.add_decision("INFO", "Non Taxable", "Couvert par l'abattement.")
                
            if tracer: tracer.end_step("Traitement 757 B terminé (Voir calcul DMTG).")
        
        details['total_tax'] = total_tax
        
        return total_tax, details
    
    @staticmethod
    def is_life_insurance(asset) -> bool:
        """
        Check if an asset is a life insurance contract.
        
        An asset is considered life insurance if it has premium information.
        """
        return (
            hasattr(asset, 'premiums_before_70') and asset.premiums_before_70 is not None
        ) or (
            hasattr(asset, 'premiums_after_70') and asset.premiums_after_70 is not None
        )
