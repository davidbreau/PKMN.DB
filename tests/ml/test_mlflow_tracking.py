import pytest
import mlflow
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import RegressorChain

@pytest.fixture
def sample_model():
    return RegressorChain(GradientBoostingRegressor(random_state=42))

@pytest.fixture
def sample_data():
    X = np.random.rand(10, 6) * 100
    y = np.random.rand(10, 5) * 150
    return X, y

def test_mlflow_logging(sample_model, sample_data):
    """Test that MLflow correctly logs metrics and model"""
    X, y = sample_data
    
    with mlflow.start_run() as run:
        # Entraînement
        sample_model.fit(X, y)
        
        # Log de métriques basiques
        mlflow.log_metric("test_metric", 0.95)
        
        # Log du modèle
        mlflow.sklearn.log_model(sample_model, "model")
        
        # Vérifier que le run existe
        assert mlflow.active_run() is not None
        
        # Récupérer les métriques loggées
        run_id = run.info.run_id
        metrics = mlflow.get_run(run_id).data.metrics
        
        # Vérifier que la métrique est bien loggée
        assert "test_metric" in metrics
        assert metrics["test_metric"] == 0.95

def test_model_signature():
    """Test that the model signature is correct"""
    X = np.random.rand(10, 6)
    y = np.random.rand(10, 5)
    
    model = RegressorChain(GradientBoostingRegressor())
    model.fit(X, y)
    
    with mlflow.start_run():
        # Log du modèle avec signature
        signature = mlflow.models.infer_signature(X, y)
        mlflow.sklearn.log_model(model, "model", signature=signature)
        
        # Vérifier la signature
        assert signature.inputs.shape[1] == 6  # 6 features d'entrée
        assert signature.outputs.shape[1] == 5  # 5 targets de sortie 