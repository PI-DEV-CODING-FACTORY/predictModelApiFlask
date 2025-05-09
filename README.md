# API de Prédiction de Durée de Formation

Cette API permet de prédire la durée de formation en fonction de différents paramètres d'entrée.

## Prérequis

- Docker
- Docker Compose

## Installation

1. Clonez le repository
2. Assurez-vous que les fichiers suivants sont présents dans le répertoire :
   - model.joblib
   - scaler.joblib
   - features.joblib

## Démarrage

```bash
docker-compose up --build
```

L'API sera accessible à l'adresse : http://localhost:5000

## Endpoints

### POST /predict

Prédit la durée de formation.

Exemple de requête :
```json
{
    "Âge": 25,
    "Niveau_Éducation": "Bac+3",
    "Expérience_Formation": 2,
    "Heures_Étude_Par_Semaine": 20,
    "Note_Moyenne_Antérieure": 15,
    "Difficulté_Formation": "Moyen",
    "Durée_Formation_Prévue": 52
}
```

### GET /health

Vérifie l'état de santé de l'API.

## Sécurité

- L'API est configurée pour fonctionner en mode production
- Les modèles sont montés en volumes Docker pour la persistance
- Healthcheck configuré pour la surveillance de l'application