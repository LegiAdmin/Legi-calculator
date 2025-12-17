# Mission Lovable - Étape 4 : Stratégie & Volontés (Wishes)

**Note au développeur** : Ce document liste les **possibilités fonctionnelles** offertes par le moteur de calcul. Ton objectif est de concevoir l'expérience utilisateur (UX) la plus fluide pour recueillir ces intentions, sans te sentir contraint par une forme de formulaire précise.

L'objectif est de répondre à la question : *"Qui reçoit quoi ?"* (Donations passées et transmission future).

> **Philosophie "Permissive UI"** :
> L'utilisateur ne connait pas le droit. Laisse-le exprimer ses souhaits (même s'ils semblent mathématiquement ou légalement "cassés").
> *Exemple : Il peut léguer 100% de sa maison à Paul ET 50% de cette même maison à Jacques. Laisse passer, le moteur renverra une alerte.*

---

## 1. LE CHAMP DES POSSIBLES (Ce que le moteur sait gérer)

Voici les scénarios que ton interface peut proposer à l'utilisateur, du plus simple au plus complexe. Tu peux les combiner.

### A. Les Donations Passées (Le Passé)
Le moteur a besoin de connaître l'historique pour équilibrer les comptes.
*   **Types supportés** : Don Manuel (Cash/Meuble), Donation Partage (Figée), Donation Immo.
*   **Champs clés** : Date, Bénéficiaire, Montant/Bien.
*   **Subtilité** : Idéalement, distinguer si la donation est "Avance de part" (avance sur héritage) ou "Hors part" (avantage définitif). Par défaut le moteur gère le standard, mais l'option existe.

### B. Le Testament : "Qui reçoit quoi ?" (Le Futur)

Le moteur permet une **double distribution** logicielle :

#### 1. Les Legs Particuliers (Biens Spécifiques)
L'utilisateur peut désigner des biens précis pour des personnes précises.
*   **Un bien -> Une personne** : *"La Maison à Paul à 100%".*
*   **Un bien -> Plusieurs personnes** : *"L'Appartement à 50% pour Paul et 50% pour Jacques".* (Le moteur supporte le champ `share_percentage` sur un legs).
*   **Cumul** : On peut faire autant de legs qu'on veut.

#### 2. La Répartition du "Reste" (Quote-part résiduelle)
Une fois les biens spécifiques distribués, il reste un "solde" (comptes bancaires non légués, meubles, soulte...).
*   **Option "Légale"** : Par défaut, le reste est partagé selon la loi (Enfants puis Conjoint etc.).
*   **Option "Sur-Mesure"** : L'utilisateur peut dire *"Tout le reste est partagé : 40% à l'Association ABC, 60% à mes petits-enfants"*.
    *   Le moteur attend ici une liste `custom_shares` (Bénéficiaire -> %).

### C. Le Conjoint Survivant (Si marié)
Si un conjoint existe, deux mécanismes s'ajoutent :
*   **Donation au Dernier Vivant (DDV)** : Une simple case à cocher ("Aviez-vous fait une donation entre époux ?"). Cela débloque des options.
*   **L'Option** : Le conjoint a souvent le choix (Usufruit, 1/4 Propriété, etc.). Tu peux soit le demander, soit afficher ces options comme des **scénarios de résultats** (ex: "Voir les résultats si Madame choisit l'Usufruit").

### D. Le Passif (Dettes)
Pour avoir un net taxable juste, il faut déduire les dettes.
*   **Lien Dette-Actif** : Le moteur permet de lier un emprunt à un actif (ex: Prêt Immo sur la Maison). C'est crucial pour la fiscalité de certains biens exonérés (Dutreil, Forêt).
*   **Justificatifs** : Pour les dettes > 1500€ (frais obsèques), un flag `proof_provided` existe.

---

## 2. LOGIQUE DE PERSISTANCE

*   Tout doit être sauvegardé dans le JSON `SimulationInput` en base de données.
*   Le calcul est stateless : il a besoin de TOUT recharger (Membres + Actifs + Volontés) pour tourner.

---

## 3. SUGGESTIONS UX (À toi de jouer)

*   **Approche Storytelling** : *"Avez-vous déjà donné de l'argent à vos enfants ?"* -> *"Et pour votre succession, avez-vous des souhaits particuliers pour certains biens ?"*
*   **Approche Visuelle** : Pour la répartition du reste, des sliders ou un camembert interactif fonctionnent bien.
*   **Gestion des Erreurs** : Si l'utilisateur distribue 120% du reste, ne le bloque pas forcément, mais affiche un warning visuel ("Attention, le total dépasse 100%").

---

## 4. RÉCAPITULATIF TECHNIQUE (`Wishes` Schema)

Pour rappel, voici ce que le moteur attend dans l'objet `wishes` :

```json
{
  "has_spouse_donation": true/false, // DDV
  "testament_distribution": "CUSTOM", // ou LEGAL
  "specific_bequests": [ // Legs particuliers
    { "asset_id": "Maison", "beneficiary_id": "Paul", "share_percentage": 100 },
    { "asset_id": "Appart", "beneficiary_id": "Paul", "share_percentage": 50 },
    { "asset_id": "Appart", "beneficiary_id": "Jacques", "share_percentage": 50 }
  ],
  "custom_shares": [ // Répartition du reste
    { "beneficiary_id": "AssocABC", "percentage": 40 },
    { "beneficiary_id": "PetitsEnfants", "percentage": 60 }
  ]
}
```
Laisse ta créativité UX organiser cela !
