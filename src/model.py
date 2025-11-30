import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np

class MMXModel:
    def __init__(self):
        self.model = LinearRegression()
        self.features = []
        self.target = 'Total_Sales'
        self.is_trained = False
        self.coefficients = {}
        self.intercept = 0

    def train(self, df):
        """Trains the MMM model."""
        # Identify feature columns (numeric, excluding target and dates)
        self.features = [c for c in df.columns if c not in [self.target, 'month', 'Date', 'Unnamed: 0']]
        
        X = df[self.features]
        y = df[self.target]
        
        self.model.fit(X, y)
        self.is_trained = True
        self.intercept = self.model.intercept_
        self.coefficients = dict(zip(self.features, self.model.coef_))
        
        y_pred = self.model.predict(X)
        r2 = r2_score(y, y_pred)
        
        return {
            "r2": r2,
            "coefficients": self.coefficients,
            "intercept": self.intercept
        }

    def predict(self, inputs):
        """Predicts sales based on media spend inputs (dict)."""
        if not self.is_trained:
            return None
        
        input_values = []
        for feature in self.features:
            input_values.append(inputs.get(feature, 0.0))
            
        return self.model.predict([input_values])[0]

    def get_roi(self):
        """Calculates ROI based on coefficients (Marginal ROI)."""
        # In a linear model Sales = a*Spend + b, 'a' is the return per unit spend.
        # This is a simplification.
        return self.coefficients
