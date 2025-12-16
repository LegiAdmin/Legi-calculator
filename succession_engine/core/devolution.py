"""
Devolution Module - Heir Shares Calculation.

This module handles Step 3 of the succession calculation:
Détermination de la dévolution (Art. 913+ Code civil).

Responsibilities:
- Calculate legal reserve (réserve héréditaire)
- Process specific bequests (legs particuliers)
- Calculate heir shares based on law and wishes
- Handle representation (Art. 751+ CC)
"""

from typing import List, Dict, Tuple
from datetime import date

from succession_engine.schemas import HeirRelation
from succession_engine.constants import RESERVE_CHILDREN, RESERVE_PARENTS, DEFAULT_RESERVE_FRACTION


def calculate_legal_reserve(heirs: List) -> Tuple[float, str]:
    """
    Calculate legal reserve (réserve héréditaire) according to French law.
    
    Art. 913 CC (Descendants):
    - 1 child: 1/2 reserve
    - 2 children: 2/3 reserve
    - 3+ children: 3/4 reserve
    
    Art. 914-1 CC (Ascendants, if no descendants):
    - 2 parents: 1/2 reserve (1/4 each)
    - 1 parent: 1/4 reserve
    
    Args:
        heirs: List of FamilyMember objects
        
    Returns:
        Tuple of (reserve_fraction, description)
    """
    children = [h for h in heirs if h.relationship == HeirRelation.CHILD]
    grandchildren = [h for h in heirs if h.relationship == HeirRelation.GRANDCHILD]
    
    # Filter children for reserve (Art. 913 CC):
    # Renouncing child does NOT count, unless represented.
    counting_children = []
    for child in children:
        is_renouncing = getattr(child, 'acceptance_option', 'PURE_SIMPLE') == 'RENUNCIATION'
        if not is_renouncing:
            counting_children.append(child)
        else:
            # Check if represented by a grandchild
            is_represented = any(gc.represented_heir_id == child.id for gc in grandchildren)
            if is_represented:
                counting_children.append(child)
                
    num_children = len(counting_children)
    
    if num_children >= 1:
        # Reserve for descendants
        if num_children == 1:
            return RESERVE_CHILDREN[1], "1 enfant (ou représenté) : réserve de 1/2"
        elif num_children == 2:
            return RESERVE_CHILDREN[2], "2 enfants (ou représentés) : réserve de 2/3"
        else:  # 3+
            return RESERVE_CHILDREN[3], f"{num_children} enfants (ou représentés) : réserve de 3/4"
    else:
        # Reserve for ascendants (Art. 914-1 CC)
        parents = [h for h in heirs if h.relationship == HeirRelation.PARENT]
        active_parents = [
            p for p in parents 
            if getattr(p, 'acceptance_option', 'PURE_SIMPLE') != 'RENUNCIATION'
        ]
        
        if len(active_parents) == 2:
            return RESERVE_PARENTS[2], "2 parents vivants (acceptants) : réserve de 1/2 (1/4 chacun)"
        elif len(active_parents) == 1:
            return RESERVE_PARENTS[1], "1 parent vivant (acceptant) : réserve de 1/4"
        else:
            # No descendants, no parents → no reserve
            return DEFAULT_RESERVE_FRACTION, "Aucun descendant ni ascendant réservataire"


def process_specific_bequests(assets: List, wishes, heirs: List) -> Tuple[List[Dict], float]:
    """
    Process specific bequests (legs particuliers) from testament.
    
    Args:
        assets: List of Asset objects
        wishes: Wishes object containing bequests
        heirs: List of FamilyMember objects
        
    Returns:
        Tuple of (list of bequest info dicts, total bequests value)
    """
    specific_bequests_info = []
    bequests_total_value = 0.0
    
    if wishes and wishes.specific_bequests:
        for bequest in wishes.specific_bequests:
            asset = next((a for a in assets if a.id == bequest.asset_id), None)
            if asset:
                beneficiary = next((h for h in heirs if h.id == bequest.beneficiary_id), None)
                if beneficiary:
                    share = bequest.share_percentage / 100.0
                    value = asset.estimated_value * share
                    bequests_total_value += value
                    specific_bequests_info.append({
                        'asset_id': bequest.asset_id,
                        'beneficiary_id': bequest.beneficiary_id,
                        'beneficiary_name': f"Héritier {bequest.beneficiary_id}",
                        'value': value,
                        'share_percentage': bequest.share_percentage
                    })
    
    return specific_bequests_info, bequests_total_value


class HeirShareCalculator:
    """
    Calculate heir share percentages.
    
    Handles:
    - Spouse option (usufruct vs 1/4 ownership - Art. 757 CC)
    - Représentation (Art. 751+ CC) - grandchildren representing deceased parent
    - Custom shares from testament
    - Equal distribution by default
    """
    
    def __init__(self):
        """Initialize calculator with tracking fields."""
        self.spouse_has_usufruct = False
        self.usufruct_value = 0.0
        self.usufruct_rate = 0.0
        self.bare_ownership_value = 0.0
        self.spouse_birth_date = None
        self.has_stepchildren = False
    
    def calculate(self, heirs: List, wishes, net_succession_assets: float) -> Dict[str, float]:
        """
        Calculate share percentage for each heir.
        
        Args:
            heirs: List of FamilyMember objects
            wishes: Wishes object with distribution preferences
            net_succession_assets: Total estate value
            
        Returns:
            Dict mapping heir_id -> share_percentage (0.0 to 1.0)
        """
        heir_shares = {}
        
        # Build representation map
        representation_map = self._build_representation_map(heirs)
        
        # Check for spouse and stepchildren
        spouse = self._find_spouse(heirs)
        children = [h for h in heirs if h.relationship == HeirRelation.CHILD]
        self.has_stepchildren = any(
            not getattr(child, 'is_from_current_union', True) for child in children
        )
        
        # Process based on wishes
        if spouse and wishes and wishes.spouse_choice:
            heir_shares = self._apply_spouse_choice(
                heirs, wishes, spouse, net_succession_assets, representation_map
            )
        elif wishes and hasattr(wishes, 'custom_shares') and wishes.custom_shares:
            heir_shares = self._apply_custom_shares(wishes)
        else:
            heir_shares = self._apply_default_distribution(heirs, representation_map)
        
        return heir_shares
    
    def _build_representation_map(self, heirs: List) -> Dict[str, List]:
        """Build mapping of represented heirs to their representatives."""
        representation_map = {}
        for heir in heirs:
            if heir.represented_heir_id:
                if heir.represented_heir_id not in representation_map:
                    representation_map[heir.represented_heir_id] = []
                representation_map[heir.represented_heir_id].append(heir)
        return representation_map
    
    def _find_spouse(self, heirs: List):
        """Find spouse or partner in heirs list."""
        return next(
            (h for h in heirs if h.relationship in [HeirRelation.SPOUSE, HeirRelation.PARTNER]),
            None
        )
    
    def _apply_spouse_choice(
        self, heirs: List, wishes, spouse, net_succession_assets: float,
        representation_map: Dict[str, List]
    ) -> Dict[str, float]:
        """Apply spouse choice (Art. 757 CC options)."""
        from succession_engine.schemas import SpouseChoiceType
        
        heir_shares = {}
        choice = wishes.spouse_choice.choice
        children = [h for h in heirs if h.relationship == HeirRelation.CHILD]
        
        if choice == SpouseChoiceType.USUFRUCT:
            heir_shares = self._apply_usufruct_option(
                heirs, spouse, net_succession_assets, representation_map
            )
        elif choice == SpouseChoiceType.QUARTER_OWNERSHIP:
            heir_shares = self._apply_quarter_ownership(spouse, children)
        elif choice == SpouseChoiceType.DISPOSABLE_QUOTA:
            heir_shares = self._apply_disposable_quota(wishes, spouse, children)
        
        return heir_shares
    
    def _apply_usufruct_option(
        self, heirs: List, spouse, net_succession_assets: float,
        representation_map: Dict[str, List]
    ) -> Dict[str, float]:
        """Apply usufruct option (Art. 757 CC)."""
        heir_shares = {}
        heir_shares[spouse.id] = 0.0  # Usufruit (pas de part en PP)
        
        children = [h for h in heirs if h.relationship == HeirRelation.CHILD]
        
        # Handle representation: count souches
        souches = set()
        for child in children:
            souches.add(child.id)
        for represented_id in representation_map.keys():
            souches.add(represented_id)
        
        num_souches = len(souches)
        
        if num_souches > 0:
            souche_share = 1.0 / num_souches
            
            for child in children:
                heir_shares[child.id] = souche_share
            
            for represented_id, representatives in representation_map.items():
                grandchild_share = souche_share / len(representatives)
                for grandchild in representatives:
                    heir_shares[grandchild.id] = grandchild_share
        
        # Store usufruct info
        self.spouse_has_usufruct = True
        self.usufruct_value = net_succession_assets
        self.spouse_birth_date = spouse.birth_date
        
        # Calculate fiscal valuation
        try:
            from succession_engine.rules.usufruct import UsufructValuator
            
            usufruct_val, bare_ownership_val, usufruct_rate = UsufructValuator.calculate_value(
                net_succession_assets,
                spouse.birth_date,
                date.today()
            )
            self.usufruct_value = usufruct_val
            self.bare_ownership_value = bare_ownership_val
            self.usufruct_rate = usufruct_rate
        except Exception:
            self.usufruct_value = net_succession_assets
            self.bare_ownership_value = 0.0
            self.usufruct_rate = 1.0
        
        return heir_shares
    
    def _apply_quarter_ownership(self, spouse, children: List) -> Dict[str, float]:
        """Apply 1/4 ownership option (Art. 757 CC)."""
        heir_shares = {}
        heir_shares[spouse.id] = 0.25
        
        if children:
            remaining_share = 0.75 / len(children)
            for child in children:
                heir_shares[child.id] = remaining_share
        
        self.spouse_has_usufruct = False
        return heir_shares
    
    def _apply_disposable_quota(self, wishes, spouse, children: List) -> Dict[str, float]:
        """Apply disposable quota option (Art. 1094-1 CC)."""
        if not wishes.has_spouse_donation:
            raise ValueError(
                "L'option 'quotité disponible' nécessite une donation au dernier vivant. "
                "Veuillez définir has_spouse_donation=True dans wishes."
            )
        
        heir_shares = {}
        num_children = len(children)
        
        if num_children == 1:
            spouse_share = 0.5
        elif num_children == 2:
            spouse_share = 1/3
        else:
            spouse_share = 0.25
        
        heir_shares[spouse.id] = spouse_share
        
        if children:
            child_share = (1.0 - spouse_share) / num_children
            for child in children:
                heir_shares[child.id] = child_share
        
        self.spouse_has_usufruct = False
        return heir_shares
    
    def _apply_custom_shares(self, wishes) -> Dict[str, float]:
        """Apply custom distribution from testament."""
        heir_shares = {}
        for custom_share in wishes.custom_shares:
            heir_shares[custom_share.beneficiary_id] = custom_share.percentage / 100.0
        return heir_shares
    
    def _apply_default_distribution(
        self, heirs: List, representation_map: Dict[str, List]
    ) -> Dict[str, float]:
        """
        Apply default legal distribution.
        
        Handles:
        - Spouse alone (Art. 757-2 CC): 100% in full ownership
        - Children with spouse: spouse gets nothing by default (must choose option)
        - Children only: equal by souche
        - Other combinations: equal distribution
        """
        heir_shares = {}
        
        # Check for spouse-only case (Art. 757-2 CC)
        spouse = self._find_spouse(heirs)
        children = [h for h in heirs if h.relationship == HeirRelation.CHILD]
        grandchildren = [
            h for h in heirs 
            if h.relationship == HeirRelation.GRANDCHILD and h.represented_heir_id
        ]
        great_grandchildren = [
            h for h in heirs
            if h.relationship == HeirRelation.GREAT_GRANDCHILD and h.represented_heir_id
        ]
        parents = [h for h in heirs if h.relationship == HeirRelation.PARENT]
        
        # Spouse alone: 100% in full ownership (Art. 757-2 CC)
        if spouse and len(children) == 0 and len(grandchildren) == 0 and len(parents) == 0:
            # Check if only spouse (no siblings either)
            siblings = [h for h in heirs if h.relationship == HeirRelation.SIBLING]
            if len(siblings) == 0:
                # Spouse is sole heir
                heir_shares[spouse.id] = 1.0
                self.spouse_has_usufruct = False
                return heir_shares
            else:
                # Spouse with siblings: spouse gets 1/2 in full ownership (Art. 757-2)
                # Siblings share the other 1/2
                heir_shares[spouse.id] = 0.5
                sibling_share = 0.5 / len(siblings)
                for sibling in siblings:
                    heir_shares[sibling.id] = sibling_share
                self.spouse_has_usufruct = False
                return heir_shares
        
        # Spouse with parents (no children): Art. 757-1 CC
        # Spouse gets 1/2, each parent gets 1/4
        if spouse and len(children) == 0 and len(grandchildren) == 0 and len(parents) > 0:
            if len(parents) == 2:
                heir_shares[spouse.id] = 0.5
                for parent in parents:
                    heir_shares[parent.id] = 0.25
            elif len(parents) == 1:
                # One parent: spouse gets 3/4, parent gets 1/4
                heir_shares[spouse.id] = 0.75
                heir_shares[parents[0].id] = 0.25
            self.spouse_has_usufruct = False
            return heir_shares
        
        # Standard distribution by souche for children/grandchildren
        # When children/grandchildren exist, exclude parents (Art. 734 CC)
        if children or grandchildren or great_grandchildren:
            # Descendants exist: parents don't inherit, only keep spouse and siblings
            other_heirs = [
                h for h in heirs 
                if h.relationship not in [
                    HeirRelation.CHILD, HeirRelation.GRANDCHILD, 
                    HeirRelation.GREAT_GRANDCHILD, HeirRelation.PARENT
                ]
            ]
        else:
            other_heirs = [
                h for h in heirs 
                if h.relationship not in [HeirRelation.CHILD, HeirRelation.GRANDCHILD, HeirRelation.GREAT_GRANDCHILD]
            ]
        
        # ===================== ORDRE DES HÉRITIERS (Art 731-755 CC) =====================
        
        # CAS 1: Parents ET Frères/Sœurs (Art. 738 CC)
        # Si le défunt laisse père et mère et des frères et sœurs (ou neveux/nièces) :
        # - Père : 1/4
        # - Mère : 1/4
        # - Frères/Sœurs : Moitié restante (1/2)
        # Si un seul parent : 1/4 pour lui, 3/4 pour les frères/sœurs.
        
        siblings_or_nephews = [
            h for h in other_heirs 
            if h.relationship in [HeirRelation.SIBLING, HeirRelation.NEPHEW_NIECE]
        ]
        
        if not spouse and not children and not grandchildren and not great_grandchildren:
            if parents and siblings_or_nephews:
                num_parents = len(parents)
                
                # Part des parents
                if num_parents == 2:
                    heir_shares[parents[0].id] = 0.25
                    heir_shares[parents[1].id] = 0.25
                    siblings_share_total = 0.5
                else: # 1 parent
                    heir_shares[parents[0].id] = 0.25
                    siblings_share_total = 0.75
                
                # Part des frères/sœurs (égalitaire entre eux pour l'instant)
                # Note: On devrait gérer la représentation ici aussi (neveux)
                # Simplification: partage égal entre têtes de souche sibling
                if siblings_or_nephews:
                    # On utilise la logique de souche pour les siblings (car neveux peuvent représenter)
                    pass # Will fall through to standard distribution if we just return here? No.
                    
                    # Manual distribution for siblings
                    sib_souches = {}
                    for sib in [h for h in heirs if h.relationship == HeirRelation.SIBLING]:
                        sib_souches[sib.id] = [sib]
                    
                    # Nephews representing
                    nephews = [h for h in heirs if h.relationship == HeirRelation.NEPHEW_NIECE]
                    for neph in nephews:
                        if neph.represented_heir_id:
                            if neph.represented_heir_id not in sib_souches:
                                sib_souches[neph.represented_heir_id] = []
                            sib_souches[neph.represented_heir_id].append(neph)
                    
                    # Only keep valid souches (non-renouncing)
                    valid_sib_souches = []
                    for sid, members in sib_souches.items():
                        if any(getattr(h, 'acceptance_option', 'PURE_SIMPLE') != 'RENUNCIATION' for h in members):
                            valid_sib_souches.append(members)
                    
                    if valid_sib_souches:
                        share_per_souche = siblings_share_total / len(valid_sib_souches)
                        for members in valid_sib_souches:
                            share_per_member = share_per_souche / len(members)
                            for m in members:
                                heir_shares[m.id] = share_per_member
                                
                return heir_shares

        # ===================== FENTE SUCCESSORALE (Art. 746-749 CC) =====================
        # When no spouse and no descendants, check if we should apply fente
        # The estate is split 50/50 between paternal and maternal lines
        if not spouse and not children and not grandchildren and not great_grandchildren:
            # Filter renouncing heirs from other lines
            paternal_heirs = [
                h for h in other_heirs 
                if getattr(h, 'paternal_line', None) is True
                and getattr(h, 'acceptance_option', 'PURE_SIMPLE') != 'RENUNCIATION'
            ]
            maternal_heirs = [
                h for h in other_heirs 
                if getattr(h, 'paternal_line', None) is False
                and getattr(h, 'acceptance_option', 'PURE_SIMPLE') != 'RENUNCIATION'
            ]
            
            # Only apply fente if we have heirs in both lines
            if paternal_heirs and maternal_heirs:
                # 50% to each line
                paternal_share = 0.5 / len(paternal_heirs)
                maternal_share = 0.5 / len(maternal_heirs)
                
                for heir in paternal_heirs:
                    heir_shares[heir.id] = paternal_share
                for heir in maternal_heirs:
                    heir_shares[heir.id] = maternal_share
                
                return heir_shares
            
            # If only one line has heirs, they get 100%
            elif paternal_heirs:
                share = 1.0 / len(paternal_heirs)
                for heir in paternal_heirs:
                    heir_shares[heir.id] = share
                return heir_shares
            elif maternal_heirs:
                share = 1.0 / len(maternal_heirs)
                for heir in maternal_heirs:
                    heir_shares[heir.id] = share
                return heir_shares
            # Otherwise, fall through to default distribution
        
        # Build souches
        souches = {}
        for child in children:
            souches[child.id] = [child]
        
        for gc in grandchildren:
            souche_id = gc.represented_heir_id
            if souche_id not in souches:
                souches[souche_id] = []
            souches[souche_id].append(gc)
        
        # Great-grandchildren represent their grandparent (or great-grandparent souche)
        for ggc in great_grandchildren:
            souche_id = ggc.represented_heir_id
            # Find the root souche (child of deceased)
            # The represented_heir_id should point to the grandchild, we need to find which child souche
            parent_gc = next((gc for gc in grandchildren if gc.id == souche_id), None)
            if parent_gc and parent_gc.represented_heir_id:
                # The grandchild represents a child, so great-grandchild goes to that souche
                root_souche = parent_gc.represented_heir_id
                if root_souche not in souches:
                    souches[root_souche] = []
                souches[root_souche].append(ggc)
            elif souche_id not in souches:
                souches[souche_id] = [ggc]
            else:
                souches[souche_id].append(ggc)
        
        for heir in other_heirs:
            souches[heir.id] = [heir]
        
        # PRUNE SOUCHES containing only renouncing heirs (without representation)
        # If an heir renounces but has descendants representing them, the souche remains valid
        valid_souches = {}
        
        for souche_id, members in souches.items():
            # Eligible members are those who are NOT renouncing
            eligible_members = [
                h for h in members 
                if getattr(h, 'acceptance_option', 'PURE_SIMPLE') != 'RENUNCIATION'
            ]
            
            # A souche is valid if it has at least one eligible member
            # OR if the root heir renounced but is represented (implied if eligible_members > 0)
            if eligible_members:
                valid_souches[souche_id] = eligible_members
        
        if valid_souches:
            num_souches = len(valid_souches)
            souche_share = 1.0 / num_souches
            
            for souche_id, eligible_heirs in valid_souches.items():
                individual_share = souche_share / len(eligible_heirs)
                for heir in eligible_heirs:
                    heir_shares[heir.id] = individual_share
        else:
            # Fallback for other cases (e.g. no descendants, strict equality)
            # Filter renouncing heirs
            active_heirs = [
                h for h in heirs 
                if getattr(h, 'acceptance_option', 'PURE_SIMPLE') != 'RENUNCIATION'
            ]
            
            num_heirs = len(active_heirs)
            share_percent = 1.0 / num_heirs if num_heirs > 0 else 0
            for heir in active_heirs:
                heir_shares[heir.id] = share_percent
        
        return heir_shares


def check_excessive_liberalities(
    reportable_donations_value: float,
    bequests_total_value: float,
    disposable_quota: float,
    legal_reserve: float,
    reserve_fraction: float
) -> List[str]:
    """
    Check if donations + bequests exceed disposable quota (Art. 920+ CC).
    
    If yes, heirs with reserve rights can request reduction (action en réduction).
    
    Args:
        reportable_donations_value: Total value of reportable donations
        bequests_total_value: Total value of bequests
        disposable_quota: Available disposable quota
        legal_reserve: Total legal reserve amount
        reserve_fraction: Reserve as fraction of estate
        
    Returns:
        List of warning messages
    """
    warnings = []
    total_liberalities = reportable_donations_value + bequests_total_value
    
    if total_liberalities > disposable_quota and reserve_fraction > 0:
        excess = total_liberalities - disposable_quota
        warnings.append(
            f"⚠️ ATTENTION : Libéralités excessives ! "
            f"Total des donations et legs ({total_liberalities:,.2f}€) dépasse la quotité disponible ({disposable_quota:,.2f}€). "
            f"Excédent de {excess:,.2f}€ réductible par les héritiers réservataires (action en réduction possible)."
        )
        warnings.append(
            f"💡 Les héritiers réservataires peuvent demander la réduction des libéralités les plus récentes "
            f"pour reconstituer leur réserve de {legal_reserve:,.2f}€."
        )
    
    return warnings


def calculate_droit_de_retour(
    assets: List,
    heirs: List,
    net_succession_assets: float
) -> Tuple[Dict[str, float], float, List[str]]:
    """
    Calculate droit de retour (Art. 738-2 CC).
    
    When a child dies without descendants, assets they received by donation
    from their parents return to those parents (in kind or by value),
    limited to 1/4 of the estate per parent.
    
    Args:
        assets: List of Asset objects
        heirs: List of FamilyMember objects
        net_succession_assets: Total estate value
        
    Returns:
        Tuple of:
        - Dict mapping parent_id -> return value
        - Total return value
        - List of warning messages
    """
    warnings = []
    return_amounts = {}
    total_return = 0.0
    
    # Only applies if no descendants
    children = [h for h in heirs if h.relationship == HeirRelation.CHILD]
    grandchildren = [h for h in heirs if h.relationship == HeirRelation.GRANDCHILD]
    
    if children or grandchildren:
        # Descendants exist, no droit de retour
        return return_amounts, 0.0, warnings
    
    # Check parents in heirs
    parents = [h for h in heirs if h.relationship == HeirRelation.PARENT]
    if not parents:
        return return_amounts, 0.0, warnings
    
    # Find assets received from parents
    max_return_per_parent = net_succession_assets * 0.25  # 1/4 limit
    
    for asset in assets:
        parent_id = getattr(asset, 'received_from_parent_id', None)
        if parent_id and parent_id in [p.id for p in parents]:
            current_return = return_amounts.get(parent_id, 0.0)
            asset_value = asset.estimated_value
            
            # Apply 1/4 limit
            allowed_return = min(asset_value, max_return_per_parent - current_return)
            if allowed_return > 0:
                return_amounts[parent_id] = current_return + allowed_return
                total_return += allowed_return
                
                warnings.append(
                    f"🔄 DROIT DE RETOUR (Art. 738-2 CC): {asset.id} ({asset_value:,.0f}€) "
                    f"retourne au parent donateur ({parent_id}). "
                    f"Valeur restituée: {allowed_return:,.0f}€"
                )
    
    if total_return > 0:
        warnings.insert(0, 
            f"💡 Droit de retour applicable: {total_return:,.0f}€ "
            f"(biens donnés par les parents reviennent à eux, limite: 1/4 par parent)"
        )
    
    return return_amounts, total_return, warnings

