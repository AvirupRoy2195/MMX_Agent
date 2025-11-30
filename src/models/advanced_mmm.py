import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from src.utils.adstock import apply_adstock_to_dataframe

class AdvancedMMM:
    """
    Advanced Marketing Mix Model with:
    - Adstock transformations (carryover effects)
    - Brand equity modeling (NPS)
    - Short-term vs Long-term decomposition
    """
    
    def __init__(self, decay_rate=0.5):
        self.decay_rate = decay_rate
        self.model_immediate = LinearRegression()  # Short-term only
        self.model_adstock = LinearRegression()    # With adstock
        self.model_full = LinearRegression()       # Adstock + Brand
        
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
        """Train all three models for comparison."""
        # Prepare data
        df_transformed = self.prepare_data(df, media_cols)
        
        y = df_transformed[target]
        
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
        
        # Store results
        self.results = {
            'immediate': {
                'r2': r2_score(y, y_pred_immediate),
                'rmse': np.sqrt(mean_squared_error(y, y_pred_immediate)),
                'coefficients': dict(zip(self.features_immediate, self.model_immediate.coef_)),
                'intercept': self.model_immediate.intercept_
            },
            'adstock': {
                'r2': r2_score(y, y_pred_adstock),
                'rmse': np.sqrt(mean_squared_error(y, y_pred_adstock)),
                'coefficients': dict(zip(self.features_immediate + self.features_adstock, self.model_adstock.coef_)),
                'intercept': self.model_adstock.intercept_
            },
            'full': {
                'r2': r2_score(y, y_pred_full),
                'rmse': np.sqrt(mean_squared_error(y, y_pred_full)),
                'coefficients': dict(zip(self.features_full, self.model_full.coef_)),
                'intercept': self.model_full.intercept_
            }
        }
        
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
