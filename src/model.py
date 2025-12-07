"""
Marketing Mix Model - Fixed with Ridge Regression to prevent overfitting.
Problem: 12 data points with 15 features causes perfect fit but no predictive value.
Solution: Use Ridge Regression with regularization.
"""

import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score
import numpy as np

class MMXModel:
    def __init__(self, alpha=1.0):
        """
        Initialize MMX Model with Ridge Regression.
        
        Args:
            alpha: Regularization strength (higher = more regularization)
        """
        self.model = Ridge(alpha=alpha)  # Ridge instead of OLS
        self.features = []
        self.target = 'Total_Sales'
        self.is_trained = False
        self.coefficients = {}
        self.intercept = 0
        self.alpha = alpha

    def train(self, df):
        """Trains the MMM model with regularization to prevent overfitting."""
        # Identify feature columns (numeric, excluding target and dates)
        all_features = [c for c in df.columns if c not in [self.target, 'month', 'Date', 'Unnamed: 0']]
        
        # Limit features to prevent overfitting (rule of thumb: n/3 features)
        max_features = max(len(df) // 3, 4)
        
        # Select top features by correlation with target
        correlations = df[all_features].corrwith(df[self.target]).abs()
        top_features = correlations.nlargest(max_features).index.tolist()
        
        self.features = top_features
        print(f"📊 MMX Model: Using {len(self.features)} features (reduced from {len(all_features)} to prevent overfitting)")
        
        X = df[self.features]
        y = df[self.target]
        
        self.model.fit(X, y)
        self.is_trained = True
        self.intercept = self.model.intercept_
        self.coefficients = dict(zip(self.features, self.model.coef_))
        
        y_pred = self.model.predict(X)
        r2 = r2_score(y, y_pred)
        
        # Compute adjusted R² (accounts for number of features)
        n = len(y)
        p = len(self.features)
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else r2
        
        # Warning for suspicious R²
        if r2 > 0.99:
            print(f"⚠️ Warning: R² = {r2:.4f} is very high. May still indicate overfitting.")
        
        return {
            "r2": r2,
            "adjusted_r2": adj_r2,
            "coefficients": self.coefficients,
            "intercept": self.intercept,
            "features_used": self.features,
            "regularization": self.alpha
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
        return self.coefficients
    
    def get_diagnostics(self):
        """Returns model diagnostics for validation."""
        return {
            "model_type": "Ridge Regression",
            "alpha": self.alpha,
            "n_features": len(self.features),
            "features": self.features,
            "is_trained": self.is_trained
        }
