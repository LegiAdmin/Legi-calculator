"""
Calcul de l'indemnité de réduction (Art. 920+ Code civil).

Quand les donations et legs dépassent la quotité disponible, 
les héritiers réservataires peuvent demander la réduction.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import date


@dataclass
class Liberality:
    """Représente une libéralité (donation ou legs)."""
    id: str
    type: str  # "DONATION" ou "BEQUEST"
    beneficiary_id: str
    value: float
    date: date  # Pour l'ordre de réduction (plus récent en premier)
    
    
@dataclass  
class ReductionResult:
    """Résultat du calcul de réduction."""
    total_excess: float  # Montant total à réduire
    reduced_liberalities: List[Dict]  # Liste des libéralités réduites
    reserve_restored: float  # Montant de réserve restauré


class ReductionCalculator:
    """
    Calcule l'indemnité de réduction selon l'Art. 920+ du Code civil.
    
    Ordre de réduction (Art. 923 CC):
    1. D'abord les legs (testamentaires)
    2. Ensuite les donations (du plus récent au plus ancien)
    """
    
    @classmethod
    def calculate_reduction(
        cls,
        liberalities: List[Liberality],
        disposable_quota: float,
        legal_reserve: float
    ) -> ReductionResult:
        """
        Calcule la réduction nécessaire pour restaurer la réserve héréditaire.
        
        Args:
            liberalities: Liste des libéralités (donations + legs)
            disposable_quota: Quotité disponible
            legal_reserve: Réserve héréditaire
            
        Returns:
            ReductionResult avec les détails de la réduction
        """
        total_liberalities = sum(lib.value for lib in liberalities)
        
        if total_liberalities <= disposable_quota:
            # Pas d'excès → pas de réduction
            return ReductionResult(
                total_excess=0.0,
                reduced_liberalities=[],
                reserve_restored=0.0
            )
        
        excess = total_liberalities - disposable_quota
        remaining_excess = excess
        reduced = []
        
        # Trier: d'abord les legs, puis les donations par date décroissante
        sorted_liberalities = cls._sort_for_reduction(liberalities)
        
        for lib in sorted_liberalities:
            if remaining_excess <= 0:
                break
                
            # Réduire cette libéralité
            reduction_amount = min(lib.value, remaining_excess)
            reduced_value = lib.value - reduction_amount
            
            reduced.append({
                "liberality_id": lib.id,
                "type": lib.type,
                "beneficiary_id": lib.beneficiary_id,
                "original_value": lib.value,
                "reduction_amount": reduction_amount,
                "reduced_value": reduced_value
            })
            
            remaining_excess -= reduction_amount
        
        return ReductionResult(
            total_excess=excess,
            reduced_liberalities=reduced,
            reserve_restored=excess - remaining_excess
        )
    
    @classmethod
    def _sort_for_reduction(cls, liberalities: List[Liberality]) -> List[Liberality]:
        """
        Trie les libéralités selon l'ordre de réduction légal.
        
        Art. 923 CC: D'abord les legs, puis les donations du plus récent au plus ancien.
        """
        # Séparer legs et donations
        bequests = [lib for lib in liberalities if lib.type == "BEQUEST"]
        donations = [lib for lib in liberalities if lib.type == "DONATION"]
        
        # Trier les donations par date décroissante (plus récent en premier)
        donations.sort(key=lambda d: d.date, reverse=True)
        
        # Legs d'abord, puis donations
        return bequests + donations
    
    @classmethod
    def generate_reduction_warning(cls, result: ReductionResult) -> List[str]:
        """Génère des messages d'avertissement pour la réduction."""
        warnings = []
        
        if result.total_excess > 0:
            warnings.append(
                f"⚠️ RÉDUCTION NÉCESSAIRE : Les libéralités dépassent la quotité disponible de {result.total_excess:,.2f}€."
            )
            
            for reduced in result.reduced_liberalities:
                warnings.append(
                    f"  → {reduced['type']} {reduced['liberality_id']}: "
                    f"{reduced['original_value']:,.0f}€ → {reduced['reduced_value']:,.0f}€ "
                    f"(réduction de {reduced['reduction_amount']:,.0f}€)"
                )
            
            warnings.append(
                f"💡 Les héritiers réservataires peuvent exercer l'action en réduction (Art. 920+ CC)."
            )
        
        return warnings
