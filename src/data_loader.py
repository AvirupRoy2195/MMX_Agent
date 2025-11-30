import pandas as pd
import os

class DataLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.monthly_data_path = os.path.join(data_dir, "Secondfile.csv")
        self.daily_data_path = os.path.join(data_dir, "firstfile.csv")

    def load_monthly_data(self):
        """Loads the monthly aggregated data (Secondfile.csv)."""
        try:
            df = pd.read_csv(self.monthly_data_path)
            # Basic cleaning
            # Rename columns for consistency if needed
            return df
        except FileNotFoundError:
            print(f"Error: {self.monthly_data_path} not found.")
            return None

    def load_daily_data(self):
        """Loads the granular daily sales data (firstfile.csv)."""
        try:
            df = pd.read_csv(self.daily_data_path)
            return df
        except FileNotFoundError:
            print(f"Error: {self.daily_data_path} not found.")
            return None

    def get_mmm_data(self):
        """Prepares data specifically for MMM (Sales vs Media Spend)."""
        df = self.load_monthly_data()
        if df is None:
            return None
        
        # Identify relevant columns based on inspection
        # Media columns: TV, Digital, Sponsorship, Content Marketing, Online marketing, Affiliates, SEM, Radio, Other
        # Sales columns: GMV or Revenue (we'll use 'gmv_new' or aggregated revenue if available)
        
        # Based on Secondfile.csv columns:
        # Media columns use dots instead of spaces in some cases
        # Actual columns: TV, Digital, Sponsorship, Content.Marketing, Online.marketing, Affiliates, SEM, Radio, Other
        # Let's check Secondfile columns again in the code or assume standard names.
        
        # Actually, let's look at the columns from previous step:
        # ['Unnamed: 0', 'month', 'Revenue_Camera', ..., 'TV', 'Digital', ..., 'Date', 'NPS']
        
        # We need a total sales metric. Let's sum all Revenue columns or look for a Total Revenue.
        # For now, let's sum all columns starting with 'Revenue_'
        
        revenue_cols = [c for c in df.columns if c.startswith('Revenue_')]
        df['Total_Sales'] = df[revenue_cols].sum(axis=1)
        
        media_cols = ['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']
        
        # Filter for only relevant columns (including NPS if available)
        cols_to_keep = ['month', 'Date', 'Total_Sales'] + [c for c in media_cols if c in df.columns] + revenue_cols
        if 'NPS' in df.columns:
            cols_to_keep.append('NPS')
        
        final_df = df[cols_to_keep]
        
        # Fill NaNs with 0 for media spend
        final_df = final_df.fillna(0)
        
        return final_df

    def get_category_data(self, df):
        """Extracts sales by category."""
        revenue_cols = [c for c in df.columns if c.startswith('Revenue_')]
        # Melt or just return the sum
        cat_sales = df[revenue_cols].sum().reset_index()
        cat_sales.columns = ['Category', 'Sales']
        cat_sales['Category'] = cat_sales['Category'].str.replace('Revenue_', '')
        return cat_sales

