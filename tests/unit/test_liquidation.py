"""
Unit tests for liquidation module.

Tests:
- Matrimonial regime liquidation (Art. 1400+ CC)
- Separation of property
- Community property
"""
import pytest
from datetime import date


class TestMatrimonialLiquidator:
    """Tests for MatrimonialLiquidator class."""
    
    def test_separation_personal_property(self):
        """Séparation de biens: biens propres = 100% au défunt."""
        from succession_engine.core.liquidation import MatrimonialLiquidator
        from succession_engine.schemas import (
            SimulationInput, Asset, OwnershipMode, AssetOrigin,
            MatrimonialRegime, FamilyMember, HeirRelation
        )
        
        liquidator = MatrimonialLiquidator()
        
        input_data = SimulationInput(
            matrimonial_regime=MatrimonialRegime.SEPARATION,
            assets=[
                Asset(
                    id="immo1",
                    estimated_value=500000,
                    ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                    asset_origin=AssetOrigin.PERSONAL_PROPERTY
                )
            ],
            members=[
                FamilyMember(
                    id="child1",
                    birth_date=date(1990, 1, 1),
                    relationship=HeirRelation.CHILD
                )
            ]
        )
        
        net_assets = liquidator.liquidate(input_data)
        
        # Séparation = tout au défunt
        assert net_assets == 500000
    
    def test_community_reduced_split(self):
        """Communauté réduite aux acquêts: biens communs = 50%."""
        from succession_engine.core.liquidation import MatrimonialLiquidator
        from succession_engine.schemas import (
            SimulationInput, Asset, OwnershipMode, AssetOrigin,
            MatrimonialRegime, FamilyMember, HeirRelation
        )
        
        liquidator = MatrimonialLiquidator()
        
        input_data = SimulationInput(
            matrimonial_regime=MatrimonialRegime.COMMUNITY_LEGAL,
            assets=[
                Asset(
                    id="immo1",
                    estimated_value=400000,
                    ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                    asset_origin=AssetOrigin.COMMUNITY_PROPERTY  # Bien commun
                )
            ],
            members=[
                FamilyMember(
                    id="spouse",
                    birth_date=date(1960, 5, 15),
                    relationship=HeirRelation.SPOUSE
                )
            ]
        )
        
        net_assets = liquidator.liquidate(input_data)
        
        # Communauté réduite: 50% des biens communs = 200k
        assert net_assets == pytest.approx(200000, rel=0.01)
    
    def test_inheritance_property_not_split(self):
        """Biens hérités: pas de partage même en communauté."""
        from succession_engine.core.liquidation import MatrimonialLiquidator
        from succession_engine.schemas import (
            SimulationInput, Asset, OwnershipMode, AssetOrigin,
            MatrimonialRegime, FamilyMember, HeirRelation
        )
        
        liquidator = MatrimonialLiquidator()
        
        input_data = SimulationInput(
            matrimonial_regime=MatrimonialRegime.COMMUNITY_LEGAL,
            assets=[
                Asset(
                    id="heritage",
                    estimated_value=300000,
                    ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                    asset_origin=AssetOrigin.INHERITANCE  # Hérité = propre
                )
            ],
            members=[
                FamilyMember(
                    id="spouse",
                    birth_date=date(1960, 5, 15),
                    relationship=HeirRelation.SPOUSE
                )
            ]
        )
        
        net_assets = liquidator.liquidate(input_data)
        
        # Hérité = bien propre = 100% au défunt
        assert net_assets == 300000
    
    def test_no_spouse_no_split(self):
        """Pas de conjoint = pas de partage."""
        from succession_engine.core.liquidation import MatrimonialLiquidator
        from succession_engine.schemas import (
            SimulationInput, Asset, OwnershipMode, AssetOrigin,
            MatrimonialRegime, FamilyMember, HeirRelation
        )
        
        liquidator = MatrimonialLiquidator()
        
        input_data = SimulationInput(
            matrimonial_regime=MatrimonialRegime.SEPARATION,
            assets=[
                Asset(
                    id="all",
                    estimated_value=500000,
                    ownership_mode=OwnershipMode.FULL_OWNERSHIP,
                    asset_origin=AssetOrigin.PERSONAL_PROPERTY
                )
            ],
            members=[
                FamilyMember(
                    id="child",
                    birth_date=date(1990, 1, 1),
                    relationship=HeirRelation.CHILD
                )
            ]
        )
        
        net_assets = liquidator.liquidate(input_data)
        
        assert net_assets == 500000


