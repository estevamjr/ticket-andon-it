import joblib
import os
import numpy as np

class AndonPredictor:
    def __init__(self):
        base_path = os.path.dirname(__file__)
        model_path = os.path.join(base_path, 'svm_andon_model.pkl')
        
        try:
            self.model = joblib.load(model_path)
            print("✨ AI Model 'svm_andon_model.pkl' loaded successfully!")
        except Exception as e:
            print(f"⚠️ Error loading AI Model: {e}")
            self.model = None

    def predict(self, cpu, ram, threats, untrusted):
        if self.model is None:
            return None
        
        features = np.array([[cpu, ram, threats, untrusted]])
        prediction = self.model.predict(features)
        
        return int(prediction[0])