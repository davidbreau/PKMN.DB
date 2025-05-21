from typing import Dict, List, Tuple, Union, Optional
import numpy as np
import polars as pl
import mlflow


class PokemonStatPredictor:
    """Prédicteur de stats pour l'évolution des Pokémon.
    
    Pipeline de prédiction :
    1. Définition des features/targets
    2. Préparation des données (encodage des types)
    3. Split train/test
    4. Standardisation
    5. Entraînement du modèle choisi
    6. Prédiction
    """
    
    def __init__(self, experiment_name: str = "pokemon_evolution"):
        self.scaler_X = None
        self.scaler_y = None
        self.model = None
        self.type_mapping: Dict[str, int] = {}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
        # Configuration MLflow
        mlflow.set_experiment(experiment_name)
        
    def define_features(self) -> List[str]:
        """Définit les colonnes d'entrée du modèle."""
        return [
            'base_type_1', 'base_type_2', 'base_hp',
            'base_attack', 'base_defense', 'base_sp_attack', 
            'base_sp_defense', 'base_speed'
        ]
    
    def define_targets(self) -> List[str]:
        """Définit les colonnes à prédire."""
        return [
            'evolved_attack', 'evolved_defense', 
            'evolved_sp_attack', 'evolved_sp_defense', 'evolved_speed'
        ]

    def encode_pokemon_types(self, df: pl.DataFrame) -> Dict[str, int]:
        """Encode les types de Pokémon en valeurs numériques."""
        unique_types = df.select('base_type_1').unique().to_series().sort()
        return {type_: idx for idx, type_ in enumerate(unique_types)}

    def prepare_features(self, df: pl.DataFrame) -> np.ndarray:
        """Prépare les features pour l'entraînement."""
        self.type_mapping = self.encode_pokemon_types(df)
        
        return df.select(self.define_features()).with_columns([
            pl.col('base_type_1').map_dict(self.type_mapping).alias('base_type_1'),
            pl.col('base_type_2').fill_null(pl.col('base_type_1')).map_dict(self.type_mapping).alias('base_type_2')
        ]).to_numpy()

    def prepare_targets(self, df: pl.DataFrame) -> np.ndarray:
        """Prépare les targets pour l'entraînement."""
        return df.select(self.define_targets()).to_numpy()

    def split_data(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> None:
        """Divise les données en ensembles d'entraînement et de test."""
        from sklearn.model_selection import train_test_split
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

    def standardize_data(self) -> None:
        """Standardise les données d'entraînement et de test."""
        from sklearn.preprocessing import StandardScaler
        
        if self.scaler_X is None:
            self.scaler_X = StandardScaler()
            self.scaler_y = StandardScaler()
            
            self.X_train = self.scaler_X.fit_transform(self.X_train)
            self.y_train = self.scaler_y.fit_transform(self.y_train)
            
            self.X_test = self.scaler_X.transform(self.X_test)
            self.y_test = self.scaler_y.transform(self.y_test)

    def _log_training(self, model_type: str, params: Dict = None):
        """Log les paramètres et métriques d'entraînement dans MLflow."""
        with mlflow.start_run(run_name=model_type):
            # Log des paramètres
            if params:
                mlflow.log_params(params)
            
            # Log du type de modèle
            mlflow.log_param("model_type", model_type)
            
            # Log des métriques d'évaluation
            metrics = self.evaluate_model()
            for stat, stat_metrics in metrics.items():
                for metric_name, value in stat_metrics.items():
                    mlflow.log_metric(f"{stat}_{metric_name}", value)
            
            # Log du modèle
            mlflow.sklearn.log_model(self.model, "model")

    def train_decision_tree(self, params: Optional[Dict] = None) -> None:
        """Entraîne un DecisionTreeRegressor.
        
        Args:
            params: Dictionnaire des paramètres du modèle. Si None, utilise les valeurs par défaut.
                   Paramètres possibles: max_depth, min_samples_split, min_samples_leaf
        """
        from sklearn.tree import DecisionTreeRegressor
        
        default_params = {
            'max_depth': 5,
            'min_samples_split': 5,
            'min_samples_leaf': 3,
            'random_state': 42
        }
        
        if params:
            default_params.update(params)
        
        self.model = DecisionTreeRegressor(**default_params)
        self.model.fit(self.X_train, self.y_train)
        
        # Log dans MLflow
        self._log_training("decision_tree", default_params)

    def train_random_forest(self, params: Optional[Dict] = None) -> None:
        """Entraîne un RandomForestRegressor.
        
        Args:
            params: Dictionnaire des paramètres du modèle. Si None, utilise les valeurs par défaut.
                   Paramètres possibles: n_estimators, max_depth, min_samples_split
        """
        from sklearn.ensemble import RandomForestRegressor
        
        default_params = {
            'n_estimators': 100,
            'max_depth': None,
            'min_samples_split': 2,
            'random_state': 42
        }
        
        if params:
            default_params.update(params)
        
        self.model = RandomForestRegressor(**default_params)
        self.model.fit(self.X_train, self.y_train)
        
        # Log dans MLflow
        self._log_training("random_forest", default_params)

    def train_chained_gradient_boosting(self, params: Optional[Dict] = None) -> None:
        """Entraîne un modèle de GradientBoosting en chaîne pour la prédiction multi-output.
        
        Args:
            params: Dictionnaire des paramètres du modèle. Si None, utilise les valeurs par défaut.
                   Paramètres possibles: n_estimators, learning_rate, max_depth
        """
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.multioutput import RegressorChain
        
        default_params = {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 3,
            'random_state': 42
        }
        
        if params:
            default_params.update(params)
        
        base_model = GradientBoostingRegressor(**default_params)
        self.model = RegressorChain(base_model, order=[0, 1, 2, 3, 4], random_state=42)
        self.model.fit(self.X_train, self.y_train)
        
        # Log dans MLflow
        self._log_training("chained_gradient_boosting", default_params)

    def train_multi_output_gradient_boosting(self, params: Optional[Dict] = None) -> None:
        """Entraîne un modèle de GradientBoosting avec MultiOutputRegressor.
        
        Args:
            params: Dictionnaire des paramètres du modèle. Si None, utilise les valeurs par défaut.
                   Paramètres possibles: n_estimators, learning_rate, max_depth
        """
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.multioutput import MultiOutputRegressor
        
        default_params = {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 3,
            'random_state': 42
        }
        
        if params:
            default_params.update(params)
        
        base_model = GradientBoostingRegressor(**default_params)
        self.model = MultiOutputRegressor(base_model)
        self.model.fit(self.X_train, self.y_train)
        
        # Log dans MLflow
        self._log_training("multi_output_gradient_boosting", default_params)

    def train_svr(self, params: Optional[Dict] = None) -> None:
        """Entraîne un modèle SVR (Support Vector Regression) pour la prédiction multi-output.
        
        Args:
            params: Dictionnaire des paramètres du modèle. Si None, utilise les valeurs par défaut.
                   Paramètres possibles: kernel, C, epsilon, gamma
        """
        from sklearn.svm import SVR
        from sklearn.multioutput import MultiOutputRegressor
        
        default_params = {
            'kernel': 'rbf',
            'C': 1.0,
            'epsilon': 0.1,
            'verbose': True
        }
        
        if params:
            default_params.update(params)
        
        base_model = SVR(**default_params)
        self.model = MultiOutputRegressor(base_model)
        self.model.fit(self.X_train, self.y_train)
        
        # Log dans MLflow
        self._log_training("svr", default_params)

    def evaluate_model(self) -> Dict[str, Dict[str, float]]:
        """Évalue les performances du modèle sur le jeu de test."""
        from sklearn.metrics import mean_squared_error, r2_score
        
        y_pred_scaled = self.model.predict(self.X_test)
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled)
        y_true = self.scaler_y.inverse_transform(self.y_test)
        
        metrics = {}
        stat_names = ['Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
        
        for i, stat in enumerate(stat_names):
            mse = mean_squared_error(y_true[:, i], y_pred[:, i])
            metrics[stat] = {
                'rmse': np.sqrt(mse),
                'r2': r2_score(y_true[:, i], y_pred[:, i])
            }
            
        return metrics

    def predict_stats(self, pokemon_data: Dict) -> Dict[str, float]:
        """Prédit les stats d'évolution pour un Pokémon."""
        features = np.array([[
            self.type_mapping[pokemon_data['type1']],
            self.type_mapping.get(pokemon_data['type2'], self.type_mapping[pokemon_data['type1']]),
            pokemon_data['hp'],
            pokemon_data['attack'],
            pokemon_data['defense'],
            pokemon_data['sp_attack'],
            pokemon_data['sp_defense'],
            pokemon_data['speed']
        ]])
        
        features_scaled = self.scaler_X.transform(features)
        pred_scaled = self.model.predict(features_scaled)
        predictions = self.scaler_y.inverse_transform(pred_scaled)[0]
        
        return {
            'attack': int(predictions[0]),
            'defense': int(predictions[1]),
            'sp_attack': int(predictions[2]),
            'sp_defense': int(predictions[3]),
            'speed': int(predictions[4])
        }

    def visualize_decision_tree(self, figsize: Tuple[int, int] = (20, 10)) -> None:
        """Visualise l'arbre de décision."""
        from sklearn.tree import DecisionTreeRegressor, plot_tree
        import matplotlib.pyplot as plt
        
        if not isinstance(self.model, DecisionTreeRegressor):
            raise TypeError("Cette méthode n'est disponible que pour les arbres de décision")
        
        plt.figure(figsize=figsize)
        plot_tree(
            self.model,
            feature_names=self.define_features(),
            filled=True,
            rounded=True
        )
        plt.show()

    def save_model(self, path: str) -> None:
        """Sauvegarde le modèle et les scalers.
        
        Args:
            path: Chemin de base pour la sauvegarde (sans extension)
        """
        import joblib
        import os
        
        # Création du dossier si nécessaire
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Sauvegarde des scalers et du mapping
        joblib.dump(self.scaler_X, f"{path}_scaler_X.joblib")
        joblib.dump(self.scaler_y, f"{path}_scaler_y.joblib")
        joblib.dump(self.type_mapping, f"{path}_type_mapping.joblib")
        
        # Sauvegarde du modèle scikit-learn
        joblib.dump(self.model, f"{path}_model.joblib")

    def load_model(self, path: str) -> None:
        """Charge le modèle et les scalers.
        
        Args:
            path: Chemin de base pour le chargement (sans extension)
        """
        import joblib
        
        # Chargement des scalers et du mapping
        self.scaler_X = joblib.load(f"{path}_scaler_X.joblib")
        self.scaler_y = joblib.load(f"{path}_scaler_y.joblib")
        self.type_mapping = joblib.load(f"{path}_type_mapping.joblib")
        
        # Chargement du modèle scikit-learn
        self.model = joblib.load(f"{path}_model.joblib") 