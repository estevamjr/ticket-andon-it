import pytest
from sklearn.metrics import accuracy_score
import warnings
from app.ml_logic.predictor import AndonPredictor

@pytest.fixture
def predictor():
    return AndonPredictor()

def test_model_loading(predictor):
    """Verify that the AI model is loaded successfully."""
    assert predictor.model is not None, "O modelo .pkl não foi carregado corretamente!"

def test_model_performance_threshold(predictor):
    """
    Requirement 5 of the MVP: Ensure the model meets established performance requirements. 
    The defined threshold is 80% (0.80) accuracy.
    """
    # 1. Data set simulated for performance validation
    # Order of featires: CPU Usage (%), RAM Available (GB), Active Threats, Untrusted Processes
    X_validation = [
        (98.5, 0.2, 5, 8),  # Expected: 2 (Critical)
        (12.0, 14.5, 0, 0), # Expected: 0 (Normal)
        (85.0, 1.5, 0, 1),  # Expected: 1 (Alert)
        (37.6, 6.5,  0, 0), # Expected: 0 (Normal)
        (54.6, 1.6,  3, 9)  # Expected: 2 (Critical)
    ]
    
    # Trusted Labels (Ground Truth)
    y_true = [2, 0, 1, 0, 2]
    
    # 2. Warnings ignored due to sklearn's feature name warnings when predicting with raw arrays
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # 3. Generate predictions using the model
        y_pred = [predictor.predict(cpu=x[0], ram=x[1], threats=x[2], untrusted=x[3]) for x in X_validation]

    # 4. Calculate accuracy of the model
    acc = accuracy_score(y_true, y_pred)
    
    # 5. Threshold (Aceptable performance level) defined at 80%
    THRESHOLD = 0.80
    assert acc >= THRESHOLD, f"CI/CD Failure:  Model accuracy ({acc*100}%) is below the acceptable threshold of {THRESHOLD*100}%"