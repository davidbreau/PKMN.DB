FROM python:3.12-slim

WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers
COPY . .
COPY ../models ./models/

# Exposer le port utilisé par l'application
EXPOSE 8000

# Commande pour démarrer l'application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 