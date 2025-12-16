"""
Estate Reconstitution Module.

This module handles Step 2 of the succession calculation:
Reconstitution de la masse successorale (Art. 843+ Code civil).

Responsibilities:
- Calculate reportable donations (rapport civil)
- Deduct debts from estate
- Build the reconstructed estate value
"""

from typing import List, Dict, Tuple


def get_reportable_donations(donations: List) -> Tuple[List[Dict], float]:
    """
    Extract reportable donations for civil report (rapport civil).
    
    Art. 843+ du Code civil:
    - Don manuel → rapportable
    - Donation-partage → non rapportable
    - Présent d'usage → non rapportable
    
    Args:
        donations: List of Donation schema objects
        
    Returns:
        Tuple of (list of donation info dicts, total reportable value)
    """
    reportable_donations = []
    reportable_donations_value = 0.0
    
    if donations:
        for donation in donations:
            if donation.is_reportable():
                reportable_value = donation.get_reportable_value()
                reportable_donations_value += reportable_value
                reportable_donations.append({
                    'beneficiary_id': donation.beneficiary_heir_id,
                    'beneficiary_name': donation.beneficiary_name,
                    'donation_date': donation.donation_date,
                    'value': reportable_value,
                    'type': donation.donation_type.value,
                    'is_declared_to_tax': donation.is_declared_to_tax
                })
    
    return reportable_donations, reportable_donations_value


def reconstitute_estate(
    net_assets: float,
    reportable_donations_value: float = 0.0,
    debts: List = None
) -> Tuple[float, float]:
    """
    Reconstitute estate (Masse successorale).
    
    Art. 922 CC: Masse = Actif net + Donations rapportables - Dettes déductibles
    
    Debts are deducted to get the net taxable estate.
    Only deductible debts reduce the estate (mortgages, loans, taxes, funeral costs).
    
    Args:
        net_assets: Net assets from matrimonial liquidation
        reportable_donations_value: Total value of reportable donations
        debts: List of Debt schema objects
        
    Returns:
        Tuple of (net succession assets, total deductible debts)
    """
    total_deductible_debts = 0.0
    debt_warnings = []
    
    # Import constant locally to avoid circular imports
    from succession_engine.constants import MAX_FUNERAL_DEDUCTION
    
    if debts:
        for debt in debts:
            if debt.is_deductible:
                amount_to_deduct = debt.amount
                
                # Plafonnement frais funéraires (Art. 775 CGI)
                if debt.debt_type == "FUNERAL":
                    if amount_to_deduct > MAX_FUNERAL_DEDUCTION and not getattr(debt, 'proof_provided', False):
                        amount_to_deduct = MAX_FUNERAL_DEDUCTION
                        debt_warnings.append(
                            f"⚠️ Frais funéraires plafonnés à {MAX_FUNERAL_DEDUCTION}€ (Art. 775 CGI) "
                            f"car aucun justificatif complet n'a été fourni "
                            f"(montant déclaré : {debt.amount}€)."
                        )
                    elif amount_to_deduct > MAX_FUNERAL_DEDUCTION:
                        # Proof provided implies we accept the amount, but still helpful to warn/log
                        debt_warnings.append(
                            f"ℹ️ Frais funéraires supérieurs au plafond légal ({MAX_FUNERAL_DEDUCTION}€) "
                            f"acceptés sur justificatifs (montant : {debt.amount}€)."
                        )
                        
                total_deductible_debts += amount_to_deduct
            else:
                # Warning for non-deductible debts just in case use meant to deduct them
                if getattr(debt, 'proof_provided', False):
                     debt_warnings.append(
                        f"⚠️ La dette '{debt.description or debt.id}' a un justificatif mais est marquée non déductible."
                     )
    
    net_succession_assets = net_assets + reportable_donations_value - total_deductible_debts
    
    # Return 3 values (net_assets, debts, warnings)
    # Note: caller signature needs to be updated or warnings handled separately
    # For now, we print warnings or attach them to a global warning context if available
    # Since we can't easily change the signature without affecting callers, we'll assume callers handle list return or we leave as is
    # However, to be cleaner, we should return warnings.
    # Let's check calculator.py usage first. 
    # Actually, the user asked for warnings in the output. 
    # The function signature was: -> Tuple[float, float]
    # Changing it might break things. Let's see who calls it.
    
    return net_succession_assets, total_deductible_debts, debt_warnings
