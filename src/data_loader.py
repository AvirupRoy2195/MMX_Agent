"""
Data Loader - Enhanced to properly handle the multi-file DT Mart database.

Files:
- Sales.csv: 1M+ transaction records (tab-delimited)
- MediaInvestment.csv: Monthly media spend by channel
- MonthlyNPSscore.csv: Monthly NPS scores
- ProductList.csv: Product catalog with frequencies
- SpecialSale.csv: Special sale event dates
- Secondfile.csv: Pre-aggregated monthly data (currently used)
- firstfile.csv: Granular data
"""

import pandas as pd
import os
from datetime import datetime


class DataLoader:
    """
    Enhanced data loader for the DT Mart Marketing Mix database.
    Supports multiple data sources with proper merging.
    """
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.data_files = {
            'monthly': os.path.join(data_dir, "Secondfile.csv"),
            'daily': os.path.join(data_dir, "firstfile.csv"),
            'sales': os.path.join(data_dir, "Sales.csv"),
            'media': os.path.join(data_dir, "MediaInvestment.csv"),
            'nps': os.path.join(data_dir, "MonthlyNPSscore.csv"),
            'products': os.path.join(data_dir, "ProductList.csv"),
            'special_sales': os.path.join(data_dir, "SpecialSale.csv"),
        }
        
        # Cache for loaded data
        self._cache = {}
        
    def _load_file(self, key, sep=',', **kwargs):
        """Load a file with caching."""
        if key not in self._cache:
            try:
                self._cache[key] = pd.read_csv(self.data_files[key], sep=sep, **kwargs)
                print(f"✅ Loaded {key}: {len(self._cache[key])} rows")
            except FileNotFoundError:
                print(f"⚠️ {self.data_files[key]} not found")
                self._cache[key] = None
        return self._cache[key]

    def load_monthly_data(self):
        """Loads the monthly aggregated data (Secondfile.csv)."""
        return self._load_file('monthly')

    def load_daily_data(self):
        """Loads the granular daily data (firstfile.csv)."""
        return self._load_file('daily')
    
    def load_sales_transactions(self, nrows=None):
        """
        Load detailed sales transactions (Sales.csv - tab delimited).
        Warning: 1M+ rows, use nrows to limit.
        """
        return self._load_file('sales', sep='\t', nrows=nrows)
    
    def load_media_investment(self):
        """Load monthly media investment by channel."""
        df = self._load_file('media')
        if df is not None:
            # Convert to millions for easier reading
            spend_cols = ['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 
                         'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']
            for col in spend_cols:
                if col in df.columns:
                    df[f'{col}_millions'] = df[col]
        return df
    
    def load_nps_data(self):
        """Load monthly NPS scores."""
        return self._load_file('nps')
    
    def load_product_catalog(self):
        """Load product list with frequencies."""
        return self._load_file('products')
    
    def load_special_sales_calendar(self):
        """Load special sale event dates."""
        return self._load_file('special_sales')

    def get_mmm_data(self):
        """
        Prepares data specifically for MMM (Sales vs Media Spend).
        Uses pre-aggregated Secondfile.csv with NPS and Media merged.
        """
        df = self.load_monthly_data()
        if df is None:
            return None
        
        # Sum all Revenue columns to get Total Sales
        revenue_cols = [c for c in df.columns if c.startswith('Revenue_')]
        df['Total_Sales'] = df[revenue_cols].sum(axis=1)
        
        media_cols = ['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 
                     'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']
        
        # Build final dataframe
        cols_to_keep = ['month', 'Date', 'Total_Sales'] + \
                      [c for c in media_cols if c in df.columns] + \
                      revenue_cols
        
        if 'NPS' in df.columns:
            cols_to_keep.append('NPS')
        
        final_df = df[cols_to_keep].copy()
        final_df = final_df.fillna(0)
        
        return final_df

    def get_category_data(self, df=None):
        """Extracts sales by product category."""
        if df is None:
            df = self.load_monthly_data()
        if df is None:
            return None
            
        revenue_cols = [c for c in df.columns if c.startswith('Revenue_')]
        cat_sales = df[revenue_cols].sum().reset_index()
        cat_sales.columns = ['Category', 'Sales']
        cat_sales['Category'] = cat_sales['Category'].str.replace('Revenue_', '')
        return cat_sales
    
    def get_full_database_summary(self):
        """Get a summary of all available data files."""
        summary = {}
        
        # Monthly data
        monthly = self.load_monthly_data()
        if monthly is not None:
            summary['monthly'] = {
                'rows': len(monthly),
                'columns': len(monthly.columns),
                'date_range': f"{monthly['month'].iloc[0]} to {monthly['month'].iloc[-1]}" if 'month' in monthly.columns else 'N/A'
            }
        
        # Media investment
        media = self.load_media_investment()
        if media is not None:
            summary['media'] = {
                'rows': len(media),
                'channels': [c for c in media.columns if c not in ['Year', 'Month']]
            }
        
        # NPS
        nps = self.load_nps_data()
        if nps is not None:
            summary['nps'] = {
                'rows': len(nps),
                'avg_nps': nps['NPS'].mean() if 'NPS' in nps.columns else 'N/A'
            }
        
        # Products
        products = self.load_product_catalog()
        if products is not None:
            summary['products'] = {
                'count': len(products) - 1,  # Exclude Total row
            }
        
        # Special sales
        special = self.load_special_sales_calendar()
        if special is not None:
            summary['special_sales'] = {
                'events': len(special),
                'unique_names': special['Sales Name'].nunique() if 'Sales Name' in special.columns else 0
            }
        
        return summary
    
    def get_all_tables(self):
        """Get dictionary of all available tables for NL2SQL."""
        return {
            'monthly_data': self.load_monthly_data(),
            'media_investment': self.load_media_investment(),
            'nps_scores': self.load_nps_data(),
            'products': self.load_product_catalog(),
            'special_sales': self.load_special_sales_calendar(),
        }
