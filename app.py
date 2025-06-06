from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# Configuration de Swagger UI via Flask-RESTx
api = Api(
    app,
    version='1.0',
    title='API de Prédiction de Durée de Formation',
    description='API pour prédire la durée d\'une formation basée sur différents paramètres',
    doc='/swagger/',
    validate=True
)


# Charger le modèle et les composants nécessaires
model = joblib.load('model.joblib')
scaler = joblib.load('scaler.joblib')
features = joblib.load('features.joblib')

# Initialiser les encodeurs pour les variables catégorielles
le_education = LabelEncoder()
le_education.fit(['Bac', 'Bac+2', 'Bac+3', 'Bac+5', 'Doctorat'])

le_difficulte = LabelEncoder()
le_difficulte.fit(['Facile', 'Moyen', 'Difficile'])

def calculate_confidence_interval(prediction, model_input):
    # Calculer un intervalle de confiance dynamique basé sur la complexité des données
    # Obtenir la prédiction et l'erreur standard estimée
    prediction_std = np.std(model.predict(model_input))
    confidence_factor = 1.96  # Pour un niveau de confiance de 95%
    margin_of_error = prediction_std * confidence_factor
    
    # Ajuster les bornes en fonction de la durée prédite
    lower_bound = max(0, prediction - margin_of_error)
    upper_bound = prediction + margin_of_error
    
    # Assurer que l'intervalle reste réaliste
    if upper_bound > prediction * 2:
        upper_bound = prediction * 1.5
    
    return lower_bound, upper_bound

def validate_input_data(data):
    # Vérifier si tous les champs requis sont présents
    for field in features:
        if field not in data:
            raise ValueError(f'Le champ {field} est requis')
    
    # Validation des valeurs numériques
    numeric_fields = [f for f in features if f not in ['Niveau_Éducation', 'Difficulté_Formation']]
    for field in numeric_fields:
        if not isinstance(data[field], (int, float)):
            raise ValueError(f'Le champ {field} doit être numérique')
        
        # Validation des plages de valeurs
        if field == 'Âge' and (data[field] < 16 or data[field] > 100):
            raise ValueError('L\'âge doit être compris entre 16 et 100 ans')
        elif field == 'Heures_Étude_Par_Semaine' and (data[field] < 1 or data[field] > 80):
            raise ValueError('Les heures d\'étude par semaine doivent être comprises entre 1 et 80')
        elif field == 'Note_Moyenne_Antérieure' and (data[field] < 0 or data[field] > 20):
            raise ValueError('La note moyenne doit être comprise entre 0 et 20')
        elif field == 'Expérience_Formation' and (data[field] < 0 or data[field] > 50):
            raise ValueError('L\'expérience en formation doit être comprise entre 0 et 50 ans')
        elif field == 'Durée_Formation_Prévue' and (data[field] < 1 or data[field] > 156):
            raise ValueError('La durée de formation prévue doit être comprise entre 1 et 156 semaines')
    
    # Validation des champs catégoriels
    valid_education = ['Bac', 'Bac+2', 'Bac+3', 'Bac+5', 'Doctorat']
    if data['Niveau_Éducation'] not in valid_education:
        raise ValueError(f'Le niveau d\'éducation doit être l\'un des suivants: {", ".join(valid_education)}')
    
    valid_difficulty = ['Facile', 'Moyen', 'Difficile']
    if data['Difficulté_Formation'] not in valid_difficulty:
        raise ValueError(f'La difficulté de formation doit être l\'une des suivantes: {", ".join(valid_difficulty)}')

# Définir les modèles de données pour la documentation Swagger
input_model = api.model('DonnéesEntrée', {
    'Âge': fields.Integer(required=True, description='Âge de l\'apprenant (16-100)', example=30),
    'Niveau_Éducation': fields.String(required=True, description='Niveau d\'éducation', enum=['Bac', 'Bac+2', 'Bac+3', 'Bac+5', 'Doctorat'], example='Bac+3'),
    'Note_Moyenne_Antérieure': fields.Float(required=True, description='Note moyenne antérieure (0-20)', example=14.5),
    'Heures_Étude_Par_Semaine': fields.Integer(required=True, description='Heures d\'étude par semaine (1-80)', example=20),
    'Expérience_Formation': fields.Integer(required=True, description='Expérience en formation (années, 0-50)', example=2),
    'Difficulté_Formation': fields.String(required=True, description='Niveau de difficulté de la formation', enum=['Facile', 'Moyen', 'Difficile'], example='Moyen'),
    'Durée_Formation_Prévue': fields.Integer(required=True, description='Durée de formation prévue (semaines, 1-156)', example=52)
})

output_model = api.model('RésultatPrédiction', {
    'success': fields.Boolean(description='Statut de la requête'),
    'prediction': fields.Nested(api.model('Prédiction', {
        'duree_semaines': fields.Float(description='Durée prédite en semaines'),
        'duree_mois': fields.Float(description='Durée prédite en mois'),
        'intervalle_confiance': fields.Nested(api.model('IntervalleConfiance', {
            'minimum': fields.Float(description='Borne inférieure de l\'intervalle de confiance'),
            'maximum': fields.Float(description='Borne supérieure de l\'intervalle de confiance'),
            'niveau_confiance': fields.Integer(description='Niveau de confiance en pourcentage')
        }))
    })),
    'message': fields.String(description='Message explicatif'),
    'details': fields.Nested(api.model('Détails', {
        'precision': fields.String(description='Informations sur la précision'),
        'recommandation': fields.String(description='Recommandations supplémentaires')
    }))
})

error_model = api.model('Erreur', {
    'success': fields.Boolean(description='Statut de la requête'),
    'error': fields.String(description='Message d\'erreur'),
    'message': fields.String(description='Description de l\'erreur')
})

# Endpoint de prédiction avec documentation Swagger
@api.route('/predict')
class PredictionResource(Resource):
    @api.doc(description='Prédire la durée d\'une formation')
    @api.expect(input_model)
    @api.response(200, 'Succès', output_model)
    @api.response(400, 'Erreur de validation des données', error_model)
    def post(self):
        try:
            data = api.payload
            validate_input_data(data)
            
            # Prétraiter les variables catégorielles
            processed_data = data.copy()
            if 'Niveau_Éducation' in processed_data:
                processed_data['Niveau_Éducation'] = le_education.transform([processed_data['Niveau_Éducation']])[0]
            if 'Difficulté_Formation' in processed_data:
                processed_data['Difficulté_Formation'] = le_difficulte.transform([processed_data['Difficulté_Formation']])[0]
        
            # Préparer les données dans le bon ordre selon les features
            input_data = np.array([[processed_data[feature] for feature in features]])
            
            # Normaliser les données
            input_scaled = scaler.transform(input_data)
            
            # Faire la prédiction
            prediction = model.predict(input_scaled)[0]
            prediction = max(1, min(prediction, 156))  # Limiter la prédiction entre 1 et 156 semaines
            
            # Calculer l'intervalle de confiance
            lower_bound, upper_bound = calculate_confidence_interval(prediction, input_scaled)
            
            # Calculer la durée en mois (arrondie à 0.5 mois près)
            duree_mois = round(prediction / 4.345 * 2) / 2
            
            # Calculer le niveau de confiance
            confidence_level = 95  # Basé sur le facteur 1.96 utilisé dans l'intervalle
            
            return {
                'success': True,
                'prediction': {
                    'duree_semaines': round(prediction, 1),
                    'duree_mois': duree_mois,
                    'intervalle_confiance': {
                        'minimum': round(lower_bound, 1),
                        'maximum': round(upper_bound, 1),
                        'niveau_confiance': confidence_level
                    }
                },
                'message': f'La durée estimée de la formation est de {round(prediction, 1)} semaines ({duree_mois} mois)',
                'details': {
                    'precision': 'Estimation basée sur les données historiques',
                    'recommandation': 'Cette estimation peut varier selon votre rythme d\'apprentissage'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la prédiction'
            }, 400

@api.route('/health')
class HealthCheckResource(Resource):
    @api.doc(description='Vérifier l\'état de santé de l\'API')
    @api.response(200, 'API en bon état de fonctionnement')
    def get(self):
        return {'status': 'healthy'}

# Ajouter un namespace pour la documentation
ns = api.namespace('api', description='Opérations de prédiction')

if __name__ == '__main__':
    app.run(debug=True, port=5545)