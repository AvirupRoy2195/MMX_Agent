"""
Advanced Marketing Mix Model - Fixed with Ridge Regression.
Problem: Too many features for 12 data points causes perfect fit.
Solution: Use Ridge Regression with regularization.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
from src.utils.adstock import apply_adstock_to_dataframe


class AdvancedMMM:
    """
    Advanced Marketing Mix Model with:
    - Adstock transformations (carryover effects)
    - Brand equity modeling (NPS)
    - Short-term vs Long-term decomposition
    - Ridge regularization to prevent overfitting
    """
    
    def __init__(self, decay_rate=0.5, alpha=10.0):
        """
        Args:
            decay_rate: Adstock decay rate (0-1)
            alpha: Ridge regularization strength (higher = more regularization)
        """
        self.decay_rate = decay_rate
        self.alpha = alpha
        
        # Use Ridge instead of OLS to prevent overfitting
        self.model_immediate = Ridge(alpha=alpha)
        self.model_adstock = Ridge(alpha=alpha)
        self.model_full = Ridge(alpha=alpha * 2)  # More regularization for more features
        
        self.features_immediate = []
        self.features_adstock = []
        self.features_full = []
        
        self.results = {}
        
    def prepare_data(self, df, media_cols, include_nps=True):
        """Prepare data with adstock transformations."""
        # Apply adstock
        df_transformed = apply_adstock_to_dataframe(df, media_cols, self.decay_rate)
        
        # Identify features
        self.features_immediate = media_cols
        self.features_adstock = [f"{col}_adstock" for col in media_cols if f"{col}_adstock" in df_transformed.columns]
        
        if include_nps and 'NPS' in df_transformed.columns:
            self.features_full = self.features_immediate + self.features_adstock + ['NPS']
        else:
            self.features_full = self.features_immediate + self.features_adstock
        
        return df_transformed
    
    def train(self, df, media_cols, target='Total_Sales'):
        """Train all three models for comparison with regularization."""
        # Prepare data
        df_transformed = self.prepare_data(df, media_cols)
        
        y = df_transformed[target]
        n_samples = len(y)
        
        print(f"📊 AdvancedMMM: Training with {n_samples} samples, alpha={self.alpha}")
        
        # Model 1: Immediate effects only
        X_immediate = df_transformed[self.features_immediate]
        self.model_immediate.fit(X_immediate, y)
        y_pred_immediate = self.model_immediate.predict(X_immediate)
        
        # Model 2: Adstock effects
        X_adstock = df_transformed[self.features_immediate + self.features_adstock]
        self.model_adstock.fit(X_adstock, y)
        y_pred_adstock = self.model_adstock.predict(X_adstock)
        
        # Model 3: Full model (Adstock + Brand)
        X_full = df_transformed[self.features_full]
        self.model_full.fit(X_full, y)
        y_pred_full = self.model_full.predict(X_full)
        
        # Compute adjusted R² for each model
        def adjusted_r2(y_true, y_pred, n_features):
            r2 = r2_score(y_true, y_pred)
            n = len(y_true)
            if n > n_features + 1:
                return 1 - (1 - r2) * (n - 1) / (n - n_features - 1)
            return r2
        
        # Store results
        self.results = {
            'immediate': {
                'r2': r2_score(y, y_pred_immediate),
                'adj_r2': adjusted_r2(y, y_pred_immediate, len(self.features_immediate)),
                'rmse': np.sqrt(mean_squared_error(y, y_pred_immediate)),
                'coefficients': dict(zip(self.features_immediate, self.model_immediate.coef_)),
                'intercept': self.model_immediate.intercept_,
                'n_features': len(self.features_immediate)
            },
            'adstock': {
                'r2': r2_score(y, y_pred_adstock),
                'adj_r2': adjusted_r2(y, y_pred_adstock, len(self.features_immediate + self.features_adstock)),
                'rmse': np.sqrt(mean_squared_error(y, y_pred_adstock)),
                'coefficients': dict(zip(self.features_immediate + self.features_adstock, self.model_adstock.coef_)),
                'intercept': self.model_adstock.intercept_,
                'n_features': len(self.features_immediate + self.features_adstock)
            },
            'full': {
                'r2': r2_score(y, y_pred_full),
                'adj_r2': adjusted_r2(y, y_pred_full, len(self.features_full)),
                'rmse': np.sqrt(mean_squared_error(y, y_pred_full)),
                'coefficients': dict(zip(self.features_full, self.model_full.coef_)),
                'intercept': self.model_full.intercept_,
                'n_features': len(self.features_full)
            }
        }
        
        # Print diagnostics
        for model_name, model_results in self.results.items():
            r2 = model_results['r2']
            adj_r2 = model_results['adj_r2']
            n_feat = model_results['n_features']
            print(f"  {model_name}: R²={r2:.4f}, Adj.R²={adj_r2:.4f}, features={n_feat}")
            if r2 > 0.99:
                print(f"    ⚠️ High R² may still indicate overfitting")
        
        return self.results
    
    def get_roi_decomposition(self):
        """Decompose ROI into short-term and long-term components."""
        if not self.results:
            return None
        
        roi_decomp = {}
        adstock_coefs = self.results['adstock']['coefficients']
        
        for col in self.features_immediate:
            immediate_roi = adstock_coefs.get(col, 0)
            longterm_roi = adstock_coefs.get(f"{col}_adstock", 0)
            
            roi_decomp[col] = {
                'immediate': immediate_roi,
                'longterm': longterm_roi,
                'total': immediate_roi + longterm_roi
            }
        
        return roi_decomp
    
    def get_brand_impact(self):
        """Get the impact of brand equity (NPS) on sales."""
        if 'NPS' in self.results['full']['coefficients']:
            return self.results['full']['coefficients']['NPS']
        return None
    
    def get_diagnostics(self):
        """Return model diagnostics for validation."""
        return {
            "model_type": "Ridge Regression",
            "regularization_alpha": self.alpha,
            "decay_rate": self.decay_rate,
            "n_samples": 12,  # Hardcoded for now
            "features_immediate": len(self.features_immediate),
            "features_adstock": len(self.features_adstock),
            "features_full": len(self.features_full),
            "warning": "High R² values may indicate overfitting with small dataset"
        }
