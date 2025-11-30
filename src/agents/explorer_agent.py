import pandas as pd

class ExplorerAgent:
    def __init__(self, data):
        self.data = data

    def get_kpis(self):
        """Returns high-level KPIs."""
        if self.data is None: return {}
        return {
            "Total Sales": self.data['Total_Sales'].sum(),
            "Total Spend": self.data[['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']].sum().sum(),
            "Data Points": len(self.data)
        }

    def analyze_categories(self):
        """Returns sales by category."""
        if self.data is None: return None
        revenue_cols = [c for c in self.data.columns if c.startswith('Revenue_')]
        cat_sales = self.data[revenue_cols].sum().reset_index()
        cat_sales.columns = ['Category', 'Sales']
        cat_sales['Category'] = cat_sales['Category'].str.replace('Revenue_', '')
        return cat_sales

    def analyze_correlations(self):
        """Returns correlation matrix between Spend and Sales."""
        if self.data is None: return None
        media_cols = ['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']
        cols = media_cols + ['Total_Sales']
        # Filter cols that exist
        cols = [c for c in cols if c in self.data.columns]
        return self.data[cols].corr()
