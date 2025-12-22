"""
Centralized repository for Educational Content used in Explicability Steps.
Human-First Design: Plain French sentences, no jargon.
"""

EDUCATIONAL_CONTENT = {
    "LIQUIDATION": {
        "title": "Que possédez-vous vraiment ?",
        "definition": "Inventaire de vos biens et calcul de ce qui vous appartient personnellement, selon les règles de votre mariage.",
        "why_it_matters": "Seule votre part personnelle entrera dans la succession. Si vous étiez marié en communauté, la moitié des biens communs revient à votre conjoint.",
        "legal_references": ["Art. 1400 Code Civil (communauté)", "Art. 1536 Code Civil (séparation)"]
    },
    "RECONSTITUTION": {
        "title": "Quel est le vrai total à partager ?",
        "definition": "On additionne vos biens au jour du décès avec les donations que vous avez faites de votre vivant.",
        "why_it_matters": "La loi oblige à réintégrer les donations passées pour vérifier que personne n'a été défavorisé. C'est le calcul de la 'masse de calcul'.",
        "legal_references": ["Art. 922 Code Civil (réunion fictive)", "Art. 843 Code Civil (rapport des donations)"]
    },
    "DEVOLUTION": {
        "title": "Qui reçoit quoi ?",
        "definition": "Identification de vos héritiers et calcul de la part de chacun selon la loi et votre testament.",
        "why_it_matters": "Vos enfants ont une part minimale garantie (la 'réserve'). Le reste, appelé 'quotité disponible', peut être distribué librement.",
        "legal_references": ["Art. 734 Code Civil (ordre des héritiers)", "Art. 912 Code Civil (réserve héréditaire)"]
    },
    "FISCAL": {
        "title": "Combien chacun doit-il à l'État ?",
        "definition": "Calcul des droits de succession que chaque héritier devra payer, après application des abattements.",
        "why_it_matters": "L'impôt dépend du lien de parenté. Les enfants bénéficient d'un abattement de 100 000 € et d'un barème progressif. Les personnes sans lien familial paient 60 %.",
        "legal_references": ["Art. 779 CGI (abattements)", "Art. 777 CGI (barème progressif)"]
    }
}
