FROM python:3.8.3

WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY app.py .
COPY model.joblib .
COPY scaler.joblib .
COPY features.joblib .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 5000

# Commande pour démarrer l'application
CMD ["python", "app.py"]