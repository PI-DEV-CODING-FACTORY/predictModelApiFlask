import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Charger les données
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# Prétraitement des données
def preprocess_data(data):
    # Encoder les variables catégorielles
    le = LabelEncoder()
    data['Niveau_Éducation'] = le.fit_transform(data['Niveau_Éducation'])
    data['Difficulté_Formation'] = le.fit_transform(data['Difficulté_Formation'])
    
    # Sélection des features
    features = ['Âge', 'Niveau_Éducation', 'Expérience_Formation', 
               'Heures_Étude_Par_Semaine', 'Note_Moyenne_Antérieure', 
               'Difficulté_Formation', 'Durée_Formation_Réelle']
    
    X = data[features]
    #Cible
    y = data['Durée_Formation_Prévue']
    
    # Normalisation des features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, scaler, features

# Entraînement du modèle avec optimisation des hyperparamètres
def train_model(X, y):
    # Définir des hyperparamètres plus simples et stables
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 15],
        'min_samples_split': [5],
        'min_samples_leaf': [2],
        'max_features': ['sqrt']
    }
    
    # Initialiser le modèle RandomForest
    rf = RandomForestRegressor(random_state=42)
    
    # Recherche par grille avec validation croisée
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid,
                             cv=5, n_jobs=-1, scoring='neg_mean_squared_error')
    grid_search.fit(X, y)
    
    # Retourner le meilleur modèle
    return grid_search.best_estimator_

# Évaluation du modèle
def evaluate_model(model, X, y):
    # Validation croisée avec plus de folds pour une meilleure estimation
    cv_scores = cross_val_score(model, X, y, cv=10, scoring='neg_mean_squared_error')
    rmse_scores = np.sqrt(-cv_scores)
    
    # Prédictions sur l'ensemble complet
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    # Calculer l'erreur moyenne absolue pour une meilleure interprétation
    mae = np.mean(np.abs(y - y_pred))
    
    # Calculer les intervalles de confiance
    confidence_level = 0.95
    std_error = np.std(y - y_pred)
    margin_error = std_error * 1.96  # Pour un niveau de confiance de 95%
    
    return {
        'rmse_cv_mean': rmse_scores.mean(),
        'rmse_cv_std': rmse_scores.std(),
        'r2_score': r2,
        'rmse': rmse,
        'mae': mae,
        'confidence_interval': margin_error
    }

def main():
    # Charger et prétraiter les données
    data = load_data('Prediction_duree_completion_formations.csv')
    X_scaled, y, scaler, features = preprocess_data(data)
    
    # Diviser les données
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42)
    
    # Entraîner le modèle
    model = train_model(X_train, y_train)
    
    # Évaluer le modèle
    metrics = evaluate_model(model, X_test, y_test)
    print("Résultats de l'évaluation:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # Sauvegarder le modèle et le scaler
    joblib.dump(model, 'model.joblib')
    joblib.dump(scaler, 'scaler.joblib')
    joblib.dump(features, 'features.joblib')

if __name__ == '__main__':
    main()