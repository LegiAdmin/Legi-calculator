from typing import List, Optional
from succession_engine.schemas import Alert, AlertSeverity, AlertAudience, AlertCategory

class AlertManager:
    """
    Gestionnaire centralisé des alertes pour le moteur de succession.
    Permet de créer des alertes structurées pour l'utilisateur (guidage) et le notaire (vigilance).
    """

    def __init__(self):
        self.alerts: List[Alert] = []

    def add(
        self,
        severity: AlertSeverity,
        audience: AlertAudience,
        category: AlertCategory,
        message: str,
        details: Optional[str] = None
    ):
        """Ajoute une alerte structurée."""
        self.alerts.append(Alert(
            severity=severity,
            audience=audience,
            category=category,
            message=message,
            details=details
        ))

    def get_legacy_warnings(self) -> List[str]:
        """Retourne une liste de strings pour la rétro-compatibilité."""
        return [f"{a.message} ({a.category.value})" for a in self.alerts]

    # --- Helpers métiers (Shorthands) ---

    def add_legal_warning(self, message: str, details: str = None, audience: AlertAudience = AlertAudience.USER):
        """Alerte sur les règles de dévolution (ex: Réserve, ordre héritiers)."""
        self.add(AlertSeverity.WARNING, audience, AlertCategory.LEGAL, message, details)

    def add_fiscal_note(self, message: str, details: str = None):
        """Note fiscale pour le notaire (ex: Abattement spécifique, exonération)."""
        self.add(AlertSeverity.INFO, AlertAudience.NOTARY, AlertCategory.FISCAL, message, details)

    def add_data_warning(self, message: str):
        """Incohérence des données (dates, montants)."""
        self.add(AlertSeverity.WARNING, AlertAudience.USER, AlertCategory.DATA, message)

    def add_critical_error(self, message: str):
        """Erreur bloquante ou problème majeur."""
        self.add(AlertSeverity.CRITICAL, AlertAudience.USER, AlertCategory.LEGAL, message)
