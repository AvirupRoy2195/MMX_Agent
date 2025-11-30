from src.model import MMXModel
import pandas as pd

class MMXAgent:
    def __init__(self):
        self.model = MMXModel()
        self.training_results = None

    def train_model(self, data):
        """Trains the model."""
        self.training_results = self.model.train(data)
        return self.training_results

    def get_roi(self):
        """Returns ROI coefficients."""
        if not self.training_results: return {}
        return self.training_results['coefficients']

    def get_contributions(self, data):
        """Calculates sales contribution by channel."""
        if not self.training_results: return None
        
        contributions = {}
        for feature, coef in self.training_results['coefficients'].items():
            if feature in data.columns:
                contributions[feature] = (data[feature] * coef).sum()
        
        # Base sales (Intercept * rows)
        contributions['Base Sales'] = self.training_results['intercept'] * len(data)
        return contributions

    def predict(self, inputs):
        return self.model.predict(inputs)
