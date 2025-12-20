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
from succession_engine.schemas import Asset, ExemptionType


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


def get_donations_for_reunion_fictive(donations: List) -> Tuple[List[Dict], float]:
    """
    Get all donations for Reunion Fictive (Art. 922 CC).
    
    This includes:
    - Donations Reportables (Civil)
    - Donations-Partages (Non Reportables but count for Reserve)
    - Donations Hors Part (Préciputaires)
    
    Excludes:
    - Présent d'usage
    
    Returns:
        Tuple of (list of donation info dicts, total value for reunion fictive)
    """
    reunion_donations = []
    reunion_value = 0.0
    
    if donations:
        from succession_engine.schemas import DonationType
        for donation in donations:
            # PRESENT_USAGE is excluded from everything (Art 852 CC)
            if donation.donation_type == DonationType.PRESENT_USAGE:
                continue
            
            # For Donation-Partage, Art 922 uses value at donation date (Art 1078 CC)
            # whereas get_reportable_value returns 0.0 (because it's not reportable).
            if donation.donation_type == DonationType.DONATION_PARTAGE:
                val = donation.original_value
            else:
                val = donation.get_reportable_value()
                
            reunion_value += val
            reunion_donations.append({
                'beneficiary_id': donation.beneficiary_heir_id,
                'beneficiary_name': donation.beneficiary_name,
                'donation_date': donation.donation_date,
                'value': val,
                'type': donation.donation_type.value,
                'is_declared_to_tax': donation.is_declared_to_tax,
                # Tag to distinguish origin
                'is_reportable': donation.is_reportable()
            })
            
    return reunion_donations, reunion_value


def reconstitute_estate(
    net_assets: float,
    reportable_donations_value: float = 0.0,
    debts: List = None,
    assets: List[Asset] = None
) -> Tuple[float, float, List[str]]:
    """
    Reconstitute estate (Masse successorale).
    
    Art. 922 CC: Masse = Actif net + Donations rapportables - Dettes déductibles
    
    Debts are deducted to get the net taxable estate.
    Only deductible debts reduce the estate (mortgages, loans, taxes, funeral costs).
    
    Args:
        net_assets: Net assets from matrimonial liquidation
        reportable_donations_value: Total value of reportable donations
        debts: List of Debt schema objects
        assets: List of Assets (needed for Art. 769 CGI check)
        
    Returns:
        Tuple of (net succession assets, total deductible debts, warnings)
    """
    total_deductible_debts = 0.0
    debt_warnings = []
    
    # Import constant locally to avoid circular imports
    from succession_engine.constants import MAX_FUNERAL_DEDUCTION
    
    if debts:
        for debt in debts:
            if debt.is_deductible:
                amount_to_deduct = debt.amount
                
                # Check for linked asset partial exemption (Art. 769 CGI)
                # "Les dettes contractées pour l'acquisition ou la conservation des biens 
                # sont déductibles dans les mêmes proportions que les biens auxquels elles se rapportent."
                if debt.linked_asset_id and assets:
                    linked_asset = next((a for a in assets if a.id == debt.linked_asset_id), None)
                    if linked_asset and linked_asset.professional_exemption:
                        ex_type = linked_asset.professional_exemption.exemption_type
                        if ex_type in [ExemptionType.DUTREIL, ExemptionType.FORESTRY, ExemptionType.RURAL_LEASE]:
                            # Exonération de 75% => Déductibilité de 25%
                            # Note: Simplification, certains ruraux sont à 50%, mais Dutreil/Forêt majo = 75%
                            amount_to_deduct = amount_to_deduct * 0.25
                            debt_warnings.append(
                                f"⚠️ Dette '{debt.description or debt.id}' plafonnée à 25% "
                                f"car liée à un bien partiellement exonéré ({linked_asset.id}). (Art. 769 CGI)"
                            )

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
                        debt_warnings.append(
                            f"ℹ️ Frais funéraires supérieurs au plafond légal ({MAX_FUNERAL_DEDUCTION}€) "
                            f"acceptés sur justificatifs (montant : {debt.amount}€)."
                        )
                        
                total_deductible_debts += amount_to_deduct
            else:
                if getattr(debt, 'proof_provided', False):
                     debt_warnings.append(
                        f"⚠️ La dette '{debt.description or debt.id}' a un justificatif mais est marquée non déductible."
                     )
    
    net_succession_assets = net_assets + reportable_donations_value - total_deductible_debts
    
    return net_succession_assets, total_deductible_debts, debt_warnings
