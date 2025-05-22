# PKMN.DB

Application centralisant les données Pokémon des jeux principaux et Pokémon GO en une base de données unifiée.

## Description

PKMN.DB est un projet permettant de :
- Extraire des données Pokémon depuis diverses sources
- Nettoyer et normaliser ces données 
- Fusionner les différentes bases en un jeu de données unifié
- Exposer ces données via une API REST
- Proposer une application web d'analyse et de visualisation

## Environnement et reproductibilité

### Prérequis

- Python 3.11+
- SQLite et PostgreSQL (pour les bases de données)
- Un environnement virtuel Python

### Installation de l'environnement

```bash
# Cloner le repo
git clone https://github.com/votre-username/PKMN.DB.git
cd PKMN.DB

# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
# OU avec Poetry
# poetry install
```

## Sources de données

Le projet s'appuie sur plusieurs sources de données :

1. **PokeAPI** - Pour les données des jeux principaux
   - Accédée via API REST
   - Contient les détails des Pokémon, types, attaques, etc.

2. **Pokémon GO Hub** - Pour les données spécifiques à Pokémon GO
   - Obtenues par web scraping
   - Contient stats, CP, movesets spécifiques à Pokémon GO

3. **Fichiers CSV/XLSX**
   - Pour les tableaux d'efficacité des types
   - Autres données statiques

## Construction des bases de données

### 1. Construire la base Pokémon principale

```bash
# Depuis la racine du projet
python app/db/PKMNdb_local_build.py
```

Cette commande extrait les données de PokeAPI et crée le fichier `app/db/PKMN.db`.

### 2. Construire la base Pokémon GO

```bash
# Depuis la racine du projet
python app/db/PKMNGOdb_local_build.py
```

Cette commande effectue le scraping de Pokémon GO Hub et crée le fichier `app/db/PKMNGO.db`.

### 3. Fusionner les bases de données

```bash
# Depuis la racine du projet
python app/db/merge.py
```

Cette commande fusionne les deux bases de données en une seule base unifiée `app/db/V2_PKMN.db`.

## Migrations vers Supabase

Pour migrer la base de données SQLite vers Supabase (PostgreSQL) :

```bash
# Configuration des variables d'environnement (à faire avant la migration)
export SUPABASE_URL="https://votre-projet.supabase.co"
export SUPABASE_KEY="votre-clé-secrète"

# Migration
python app/db/supabase_migration.py
```

## Applications déployées

### API REST

- **URL** : https://pkmn-db-api.onrender.com
- **Documentation** : https://pkmn-db-api.onrender.com/docs
- **Utilisation** : Requiert un token API dans l'en-tête des requêtes

### Application Web

- **URL** : https://pkmn-db.streamlit.app
- **Fonctionnalités** : Recherche, filtrage, statistiques, visualisations
- **Accessibilité** : Contraste optimisé et navigation clavier

### Modèle de Machine Learning

- **URL** : https://pkmn-ml-api.onrender.com
- **Documentation** : https://pkmn-ml-api.onrender.com/docs
- **Utilisation** : Requiert une clé API dans l'en-tête des requêtes

## Structure du projet

```
PKMN.DB/
├── app/
│   ├── db/                # Scripts de base de données
│   ├── models/            # Modèles SQLModel
│   ├── api/               # API REST
│   └── web/               # Application Streamlit
├── data/                  # Données statiques
├── ml/                    # Modèle de machine learning
├── tests/                 # Tests automatisés
├── requirements.txt       # Dépendances
└── README.md              # Ce fichier
```

## Tests et qualité

Exécuter les tests :

```bash
pytest
```

Linting et formatage :

```bash
flake8 .
black .
```

## Licence

Ce projet est sous licence MIT.