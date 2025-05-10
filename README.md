# API de Prédiction de Durée de Formation

Cette API permet de prédire la durée de formation en fonction de différents paramètres d'entrée.

---

## Table des Matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Démarrage](#démarrage)
4. [Endpoints](#endpoints)
   - [POST /predict](#post-predict)
   - [GET /health](#get-health)
5. [Structure du Projet](#structure-du-projet)
6. [Sécurité](#sécurité)
7. [Tests](#tests)
8. [Contributeurs](#contributeurs)
9. [Licence](#licence)

---

## Prérequis

- Docker
- Docker Compose
- Python 3.8+ (si vous exécutez l'application localement)

---

## Installation

1. Clonez le repository :
   ```bash
   git clone <URL_DU_REPOSITORY>
   cd <NOM_DU_REPERTOIRE>
   ```

2. Assurez-vous que les fichiers suivants sont présents dans le répertoire :
   - `model.joblib`
   - `scaler.joblib`
   - `features.joblib`

3. Installez les dépendances si vous exécutez l'application localement :
   ```bash
   pip install -r requirements.txt
   ```

---

## Démarrage

### Avec Docker

1. Construisez et démarrez les conteneurs :
   ```bash
   docker-compose up --build
   ```

2. L'API sera accessible à l'adresse : [http://localhost:5000](http://localhost:5000)

### Localement

1. Lancez l'application :
   ```bash
   python app.py
   ```

2. L'API sera accessible à l'adresse : [http://localhost:5000](http://localhost:5000)

---

## Endpoints

### POST /predict

Prédit la durée de formation.

#### Exemple de requête :
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

#### Exemple de réponse :
```json
{
    "Durée_Prévue": 50.5
}
```

---

### GET /health

Vérifie l'état de santé de l'API.

#### Exemple de réponse :
```json
{
    "status": "healthy"
}
```

---

## Structure du Projet

Voici une description des fichiers et répertoires principaux du projet :

- **`app.py`** : Contient le code principal de l'API Flask, y compris les routes `/predict` et `/health`.
- **`train_model.py`** : Script pour entraîner le modèle de prédiction. Il inclut le chargement des données, le prétraitement et l'entraînement du modèle.
- **`model.joblib`** : Modèle de machine learning pré-entraîné utilisé pour les prédictions.
- **`scaler.joblib`** : Scaler pour normaliser les données d'entrée.
- **`features.joblib`** : Liste des caractéristiques utilisées par le modèle.
- **`Prediction_duree_completion_formations.csv`** : Fichier CSV contenant les données utilisées pour entraîner le modèle.
- **`prediction_model_.ipynb`** : Notebook Jupyter pour l'exploration des données et le développement du modèle.
- **`requirements.txt`** : Liste des dépendances Python nécessaires pour exécuter l'application.
- **`Dockerfile`** : Définit l'image Docker pour l'application.
- **`docker-compose.yml`** : Configuration Docker Compose pour orchestrer les conteneurs.
- **`README.md`** : Documentation du projet.
- **`__pycache__/`** : Répertoire contenant les fichiers Python compilés (générés automatiquement).
- **`.idea/`** : Répertoire contenant les fichiers de configuration de l'IDE (générés automatiquement).

---

## Sécurité

- L'API est configurée pour fonctionner en mode production.
- Les modèles sont montés en volumes Docker pour garantir la persistance.
- Un healthcheck est configuré pour surveiller l'état de l'application.

---

## Tests

1. Installez `pytest` si ce n'est pas déjà fait :
   ```bash
   pip install pytest
   ```

2. Exécutez les tests :
   ```bash
   pytest
   ```

---

## Contributeurs

- **Firas Ben Kraiem** - Développeur principal

---

## Licence

Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus d'informations.