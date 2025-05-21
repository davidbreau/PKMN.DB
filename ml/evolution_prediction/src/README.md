# API de Prédiction d'Évolution Pokémon

Cette API permet de prédire les statistiques d'un Pokémon après évolution en utilisant un modèle d'apprentissage automatique entrainé sur des données de Méga-Évolutions.

## Installation

### Option 1: Installation locale

1. Cloner le dépôt
2. Installer les dépendances:
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer l'API:
   ```bash
   uvicorn api:app --reload
   ```

### Option 2: Utilisation de Docker

1. Construire l'image Docker:
   ```bash
   docker build -t pokemon-evolution-api .
   ```
2. Lancer le conteneur:
   ```bash
   docker run -p 8000:8000 pokemon-evolution-api
   ```

## Utilisation

Une fois l'API lancée, vous pouvez accéder à:

- Documentation interactive: `http://localhost:8000/docs`
- Documentation alternative: `http://localhost:8000/redoc`
- Endpoint racine: `http://localhost:8000/`
- Endpoint de prédiction: `http://localhost:8000/predict` (POST)

### Exemple de requête

```bash
curl -X 'POST' \
  'http://localhost:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "base_hp": 78,
  "base_attack": 84,
  "base_defense": 78,
  "base_sp_attack": 109,
  "base_sp_defense": 85,
  "base_speed": 100,
  "base_height": 0.6,
  "base_weight": 19.0,
  "base_experience": 240
}'
```

## Déploiement

Cette API peut être déployée sur différentes plateformes:

1. **BentoML Cloud**: Plateforme spécialisée pour le déploiement de modèles ML
2. **Hugging Face Spaces**: Solution gratuite pour les projets ML
3. **Railway**: Platform-as-a-Service simple avec période d'essai généreuse
4. **Render**: Service de cloud computing avec un plan gratuit

## Structure du projet

```
ml/evolution_prediction/
├── models/                # Modèles entraînés
│   ├── evolution_model.joblib
│   ├── evolution_scaler_X.joblib
│   ├── evolution_scaler_y.joblib
│   └── evolution_columns.json
├── src/
│   ├── api.py            # Code de l'API FastAPI
│   ├── requirements.txt  # Dépendances
│   ├── Dockerfile        # Configuration Docker
│   └── README.md         # Documentation
``` 