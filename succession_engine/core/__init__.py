"""
Core module for succession calculation engine.

This module provides the main calculation logic:
- Calculator: Main orchestrator
- Liquidation: Matrimonial regime handling
- Estate: Estate reconstitution
- Devolution: Heir shares and legal reserve
"""

from succession_engine.core.calculator import SuccessionCalculator
from succession_engine.core.liquidation import MatrimonialLiquidator
from succession_engine.core.estate import get_reportable_donations, reconstitute_estate
from succession_engine.core.devolution import (
    calculate_legal_reserve,
    process_specific_bequests,
    HeirShareCalculator,
    check_excessive_liberalities
)

__all__ = [
    'SuccessionCalculator',
    'MatrimonialLiquidator',
    'get_reportable_donations',
    'reconstitute_estate',
    'calculate_legal_reserve',
    'process_specific_bequests',
    'HeirShareCalculator',
    'check_excessive_liberalities',
]
