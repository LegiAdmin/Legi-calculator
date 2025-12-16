"""
Civil law calculations for succession.

Note: Usufruct calculations have been moved to usufruct.py (UsufructValuator).
Reserve and quotity calculations are handled directly in the calculator.
"""

# Import from usufruct module for backward compatibility
from succession_engine.rules.usufruct import UsufructValuator

# Expose UsufructValuator through CivilCalculator for legacy code
CivilCalculator = UsufructValuator
