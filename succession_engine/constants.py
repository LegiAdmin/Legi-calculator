"""
Constants for French succession law calculations.
All values according to current legislation (2025).
"""

# Tax Allowances by Relationship (used as fallback if no DB rules)
# Article 779 du Code général des impôts
ALLOWANCES = {
    'CHILD': 100_000.0,      # Enfants et ascendants
    'SIBLING': 15_932.0,     # Frères et sœurs
    'NEPHEW_NIECE': 7_967.0, # Neveux et nièces
    'OTHER': 1_594.0,        # Autres (au-delà du 4ème degré)
    'SPOUSE': float('inf'),  # Conjoint et partenaire PACS (exonération totale - loi TEPA)
    'PARTNER': float('inf'),
}

# Abattement supplémentaire pour handicap (Art. 779 II CGI)
# Cumulable avec les autres abattements
DISABILITY_ALLOWANCE = 159_325.0

# Legal Reserve Fractions (Article 913 du Code civil)
# Réserve héréditaire selon le nombre d'enfants
RESERVE_CHILDREN = {
    1: 1/2,  # 1 enfant : réserve de 1/2, quotité disponible de 1/2
    2: 2/3,  # 2 enfants : réserve de 2/3, quotité disponible de 1/3
    3: 3/4,  # 3+ enfants : réserve de 3/4, quotité disponible de 1/4
}

# Réserve des ascendants (Article 914-1 du Code civil)
# En l'absence de descendants
RESERVE_PARENTS = {
    2: 1/2,  # Les deux parents : 1/4 pour chaque parent
    1: 1/4,  # Un seul parent : 1/4
}

# Life Insurance Thresholds (Assurance-vie)
# Articles 757 B et 990 I du CGI
LIFE_INSURANCE_ALLOWANCE_BEFORE_70 = 152_500.0  # Par bénéficiaire
LIFE_INSURANCE_ALLOWANCE_AFTER_70 = 30_500.0    # Abattement global tous bénéficiaires confondus

# Usufruct Valuation (Maximum age in barème fiscal - Art. 669 CGI)
MAX_USUFRUCT_AGE = 120  # Au-delà de 91 ans : 10%

# Default values
DEFAULT_RESERVE_FRACTION = 0.0  # Pas de réserve si ni enfants ni parents

# Professional Exemptions (Art. 787 B, 793 CGI)
DUTREIL_EXEMPTION_RATE = 0.75  # 75% exonération Pacte Dutreil
RURAL_EXEMPTION_THRESHOLD = 300_000.0  # Plafond première tranche bail rural
RURAL_EXEMPTION_RATE_LOW = 0.75  # 75% jusqu'à 300K€
RURAL_EXEMPTION_RATE_HIGH = 0.50  # 50% au-delà de 300K€
FORESTRY_EXEMPTION_RATE = 0.75  # 75% exonération groupements forestiers

# Liabilities (Passif)
MAX_FUNERAL_DEDUCTION = 1_500.0  # Plafond légal frais funéraires sans justificatifs (Art. 775 CGI)
