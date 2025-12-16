"""
Rules module for succession calculations.

This module contains the business logic for French succession law,
separated by domain:
- fiscal: Tax calculations (inheritance tax, allowances, brackets)
- usufruct: Usufruct/bare ownership valuation (Art. 669 CGI)
- reduction: Reduction of excessive liberalities (Art. 920+ CC)
- life_insurance: Life insurance taxation (Art. 990 I & 757 B CGI)
- civil: Civil law calculations (legacy, uses UsufructValuator)
"""

from succession_engine.rules.fiscal import FiscalCalculator
from succession_engine.rules.usufruct import UsufructValuator
from succession_engine.rules.reduction import ReductionCalculator, Liberality, ReductionResult
from succession_engine.rules.life_insurance import LifeInsuranceCalculator

__all__ = [
    'FiscalCalculator',
    'UsufructValuator',
    'ReductionCalculator',
    'Liberality',
    'ReductionResult',
    'LifeInsuranceCalculator',
]
