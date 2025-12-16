"""
Valorisation de l'usufruit selon le barème fiscal (Art. 669 CGI).
"""

from succession_engine.models import Legislation, UsufructScale
from datetime import date
from typing import Optional, Tuple
from decimal import Decimal


class UsufructValuator:
    """
    Calcule la valeur de l'usufruit et de la nue-propriété selon l'âge de l'usufruitier.
    
    Art. 669 CGI - Barème fiscal de l'usufruit:
    < 21 ans : 90% usufruit / 10% nue-propriété
    21-30 ans : 80% / 20%
    31-40 ans : 70% / 30%
    41-50 ans : 60% / 40%
    51-60 ans : 50% / 50%
    61-70 ans : 40% / 60%
    71-80 ans : 30% / 70%
    81-90 ans : 20% / 80%
    > 91 ans : 10% / 90%
    """
    
    # Barème par défaut (si pas en DB)
    DEFAULT_SCALE = [
        (21, 0.90),   # < 21 ans
        (31, 0.80),   # 21-30 ans
        (41, 0.70),   # 31-40 ans
        (51, 0.60),   # 41-50 ans
        (61, 0.50),   # 51-60 ans
        (71, 0.40),   # 61-70 ans
        (81, 0.30),   # 71-80 ans
        (91, 0.20),   # 81-90 ans
        (999, 0.10),  # > 91 ans
    ]
    
    @classmethod
    def get_usufruct_rate(cls, age: int) -> float:
        """
        Retourne le taux de l'usufruit selon l'âge de l'usufruitier.
        
        Args:
            age: Âge de l'usufruitier
            
        Returns:
            float: Taux de l'usufruit (0.0 à 1.0)
        """
        # Try to get from database
        try:
            legislation = Legislation.objects.filter(is_active=True).first()
            if legislation:
                scale_entries = legislation.usufruct_scales.all().order_by('max_age')
                for entry in scale_entries:
                    if age < entry.max_age:
                        return float(entry.rate)
        except Exception:
            pass  # Fallback to default scale
        
        # Use default scale
        for max_age, rate in cls.DEFAULT_SCALE:
            if age < max_age:
                return rate
        
        return 0.10  # Default for very old
    
    @classmethod
    def calculate_temporary_usufruct(cls, total_value: float, duration_years: int) -> Tuple[float, float, float]:
        """
        Calcule l'usufruit temporaire (Art. 669 II CGI).
        
        Règle: 23% de la valeur en pleine propriété par période de 10 ans.
        Sans fraction et sans égard à l'âge de l'usufruitier.
        
        Exemple: 
        - 5 ans -> 1 tranche -> 23%
        - 11 ans -> 2 tranches -> 46%
        """
        import math
        num_periods = math.ceil(duration_years / 10)
        usufruct_rate = min(1.0, num_periods * 0.23)
        
        usufruct_value = total_value * usufruct_rate
        bare_ownership_value = total_value * (1 - usufruct_rate)
        
        return usufruct_value, bare_ownership_value, usufruct_rate

    @classmethod
    def calculate_value(
        cls, 
        total_value: float, 
        usufructuary_birth_date: Optional[date] = None,
        reference_date: Optional[date] = None,
        duration_years: Optional[int] = None,
        usufruct_type: str = "VIAGER"  # "VIAGER" or "TEMPORAIRE"
    ) -> Tuple[float, float, float]:
        """
        Calcule la valeur de l'usufruit (viager ou temporaire).
        
        Args:
            total_value: Valeur totale du bien en pleine propriété
            usufructuary_birth_date: Date de naissance (pour viager)
            reference_date: Date de référence (défaut: today)
            duration_years: Durée en années (pour temporaire)
            usufruct_type: "VIAGER" ou "TEMPORAIRE"
            
        Returns:
            Tuple (usufruct_value, bare_ownership_value, usufruct_rate)
        """
        # Usufruit Temporaire (Art. 669 II CGI)
        if usufruct_type == "TEMPORAIRE":
            if not duration_years:
                # Fallback to viager if no duration provided (or error)
                pass 
            else:
                return cls.calculate_temporary_usufruct(total_value, duration_years)
                
        # Usufruit Viager (Art. 669 I CGI)
        if reference_date is None:
            reference_date = date.today()
            
        if not usufructuary_birth_date:
            # If no birth date, assume 100% usufruct (or handle error)
            return total_value, 0.0, 1.0
        
        # Calculate age
        age = reference_date.year - usufructuary_birth_date.year
        if (reference_date.month, reference_date.day) < (usufructuary_birth_date.month, usufructuary_birth_date.day):
            age -= 1
        
        usufruct_rate = cls.get_usufruct_rate(age)
        usufruct_value = total_value * usufruct_rate
        bare_ownership_value = total_value * (1 - usufruct_rate)
        
        return usufruct_value, bare_ownership_value, usufruct_rate
    
    @classmethod
    def get_bare_ownership_rate(cls, age: int) -> float:
        """Retourne le taux de la nue-propriété (Viager)."""
        return 1.0 - cls.get_usufruct_rate(age)
