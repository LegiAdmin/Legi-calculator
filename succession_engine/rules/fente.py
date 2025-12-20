from typing import List, Dict, Optional
from succession_engine.schemas import HeirRelation, FamilyMember

class FenteDevolution:
    """
    Handles 'Fente Successorale' (Art. 746-749 CC).
    
    When established (no spouse, no descendants), the estate splits 50/50 
    between paternal and maternal lines.
    Inside each line, the 'Degree Rule' (Art. 744 CC) applies: closest degree excludes others.
    """

    @staticmethod
    def get_degree(relation: HeirRelation) -> int:
        """Return the degree of kinship for a given relationship."""
        if relation == HeirRelation.CHILD: return 1
        if relation == HeirRelation.PARENT: return 1
        if relation == HeirRelation.SIBLING: return 2
        if relation == HeirRelation.GRANDCHILD: return 2
        if relation == HeirRelation.NEPHEW_NIECE: return 3
        if relation == HeirRelation.AUNT_UNCLE: return 3
        if relation == HeirRelation.GREAT_GRANDCHILD: return 3
        if relation == HeirRelation.COUSIN: return 4
        if relation == HeirRelation.GREAT_UNCLE_AUNT: return 4
        return 99

    @staticmethod
    def apply_fente(
        potential_heirs: List[FamilyMember],
        heir_shares: Dict[str, float],
        tracer=None
    ) -> Dict[str, float]:
        """
        Apply fente logic to update heir shares.
        
        Args:
            potential_heirs: List of heirs (should be filtered for renunciation already, or re-filter here)
            heir_shares: Existing shares dict (will be updated)
            tracer: Optional tracer
        
        Returns:
            Updated heir_shares
        """
        # Filter renouncing heirs just in case
        active_heirs = [
            h for h in potential_heirs 
            if getattr(h, 'acceptance_option', 'PURE_SIMPLE') != 'RENUNCIATION'
        ]

        paternal_heirs = [h for h in active_heirs if getattr(h, 'paternal_line', None) is True]
        maternal_heirs = [h for h in active_heirs if getattr(h, 'paternal_line', None) is False]
        
        if tracer:
            tracer.start_step(3, "Application de la Fente Successorale", "Division Paternelle / Maternelle (Art. 746 CC).")
            tracer.add_input("Héritiers Ligne Paternelle", len(paternal_heirs))
            tracer.add_input("Héritiers Ligne Maternelle", len(maternal_heirs))

        # Select Best Paternal
        best_paternal_heirs = []
        if paternal_heirs:
            min_degree_pat = min(FenteDevolution.get_degree(h.relationship) for h in paternal_heirs)
            best_paternal_heirs = [
                h for h in paternal_heirs 
                if FenteDevolution.get_degree(h.relationship) == min_degree_pat
            ]
            if tracer:
                tracer.add_decision("INCLUDED", "Meilleurs Héritiers Pater.", f"{len(best_paternal_heirs)} héritiers au degré {min_degree_pat}")

        # Select Best Maternal
        best_maternal_heirs = []
        if maternal_heirs:
            min_degree_mat = min(FenteDevolution.get_degree(h.relationship) for h in maternal_heirs)
            best_maternal_heirs = [
                h for h in maternal_heirs 
                if FenteDevolution.get_degree(h.relationship) == min_degree_mat
            ]
            if tracer:
                tracer.add_decision("INCLUDED", "Meilleurs Héritiers Mater.", f"{len(best_maternal_heirs)} héritiers au degré {min_degree_mat}")

        # Distribute
        if best_paternal_heirs and best_maternal_heirs:
            # 50% / 50%
            paternal_share = 0.5 / len(best_paternal_heirs)
            maternal_share = 0.5 / len(best_maternal_heirs)
            
            for h in best_paternal_heirs:
                heir_shares[h.id] = paternal_share
            for h in best_maternal_heirs:
                heir_shares[h.id] = maternal_share
                
            if tracer:
                tracer.add_decision("CALCULATION", "Split 50/50", "Chaque ligne reçoit la moitié de la succession.")
                
        elif best_paternal_heirs:
            # 100% Paternal
            share = 1.0 / len(best_paternal_heirs)
            for h in best_paternal_heirs:
                heir_shares[h.id] = share
            if tracer:
                tracer.add_decision("CALCULATION", "100% Ligne Paternelle", "Aucun héritier maternel trouvé.")

        elif best_maternal_heirs:
            # 100% Maternal
            share = 1.0 / len(best_maternal_heirs)
            for h in best_maternal_heirs:
                heir_shares[h.id] = share
            if tracer:
                 tracer.add_decision("CALCULATION", "100% Ligne Maternelle", "Aucun héritier paternel trouvé.")

        if tracer:
            tracer.end_step("Fente appliquée.")
            
        return heir_shares
