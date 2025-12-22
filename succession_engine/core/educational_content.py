"""
Centralized repository for Educational Content used in Explicability Steps.
"""

EDUCATIONAL_CONTENT = {
    "LIQUIDATION": {
        "title": "Patrimoine et Régime Matrimonial",
        "definition": "Inventaire de vos biens et application des règles de votre mariage pour déterminer ce qui vous appartient en propre.",
        "why_it_matters": "Seule la part des biens qui vous appartient réellement entrera dans votre succession. Le régime matrimonial protège ou partage certains biens.",
        "legal_references": ["Art. 1400 Code Civil (Communauté)", "Art. 1536 Code Civil (Séparation)"]
    },
    "RECONSTITUTION": {
        "title": "La Masse à Partager",
        "definition": "Calcul de la valeur totale réelle de votre succession, en réintégrant fictivement ce que vous avez déjà donné.",
        "why_it_matters": "La loi vérifie que vos donations passées n'ont pas défavorisé vos héritiers réservataires (enfants). Tout est remis dans le pot commun pour le calcul.",
        "legal_references": ["Art. 922 Code Civil", "Art. 843 Code Civil (Rapport)"]
    },
    "DEVOLUTION": {
        "title": "La Répartition",
        "definition": "Identification de vos héritiers et distribution des parts selon la loi et votre testament.",
        "why_it_matters": "C'est ici que l'on détermine qui reçoit quoi. La loi impose une part minimale aux enfants (réserve), le reste peut être distribué librement (quotité).",
        "legal_references": ["Art. 734 Code Civil (Ordre)", "Art. 912 Code Civil (Réserve)"]
    },
    "FISCAL": {
        "title": "Simulateur Fiscal",
        "definition": "Estimation des droits de succession que chaque héritier devra payer à l'État.",
        "why_it_matters": "L'impôt est calculé individuellement après application d'abattements (réductions) spécifiques à chaque lien de parenté.",
        "legal_references": ["Art. 777 CGI (Barème)", "Art. 779 CGI (Abattements)"]
    }
}
