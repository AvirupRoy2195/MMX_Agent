import pandas as pd

class BrandAgent:
    """Agent focused on Brand Equity analysis using NPS."""
    
    def __init__(self, data):
        self.data = data
    
    def get_nps_trend(self):
        """Returns NPS trend over time."""
        if self.data is None or 'NPS' not in self.data.columns:
            return None
        
        return self.data[['Date', 'NPS']].copy()
    
    def get_nps_stats(self):
        """Returns NPS statistics."""
        if self.data is None or 'NPS' not in self.data.columns:
            return {}
        
        return {
            'mean': self.data['NPS'].mean(),
            'std': self.data['NPS'].std(),
            'min': self.data['NPS'].min(),
            'max': self.data['NPS'].max()
        }
    
    def analyze_nps_sales_correlation(self):
        """Analyzes correlation between NPS and Sales."""
        if self.data is None or 'NPS' not in self.data.columns or 'Total_Sales' not in self.data.columns:
            return None
        
        correlation = self.data[['NPS', 'Total_Sales']].corr().iloc[0, 1]
        return correlation
