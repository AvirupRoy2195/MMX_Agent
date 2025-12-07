"""
Schema Mapper Agent - Maps user queries to appropriate tables and relationships.

This agent:
1. Understands the database schema (all tables and their columns)
2. Uses LLM to interpret user queries and identify relevant tables
3. Determines join keys and relationships between tables
4. Generates the correct data mapping for complex multi-table queries
"""

import os
import json
import yaml
import pandas as pd
from typing import Dict, List, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class SchemaMapperAgent:
    """
    Intelligent agent for mapping user queries to database tables and relationships.
    Uses Gemini LLM to understand query intent and table structures.
    """
    
    # Database schema definition
    SCHEMA = {
        'monthly_data': {
            'file': 'Secondfile.csv',
            'description': 'Monthly aggregated sales and media spend data',
            'columns': ['month', 'Date', 'Revenue_Camera', 'Revenue_CameraAccessory', 
                       'Revenue_EntertainmentLarge', 'Revenue_EntertainmentSmall', 
                       'Revenue_GameCDDVD', 'Revenue_GamingHardware', 
                       'TV', 'Digital', 'Sponsorship', 'Content.Marketing', 
                       'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other', 'NPS'],
            'primary_key': 'month',
            'row_count': 12,
            'period': '2015-2016'
        },
        'media_investment': {
            'file': 'MediaInvestment.csv',
            'description': 'Monthly media investment by channel (in millions)',
            'columns': ['Year', 'Month', 'TV', 'Digital', 'Sponsorship', 
                       'Content.Marketing', 'Online.marketing', 'Affiliates', 
                       'SEM', 'Radio', 'Other'],
            'primary_key': ['Year', 'Month'],
            'row_count': 12
        },
        'nps_scores': {
            'file': 'MonthlyNPSscore.csv',
            'description': 'Monthly Net Promoter Score (brand health metric)',
            'columns': ['Date', 'NPS'],
            'primary_key': 'Date',
            'row_count': 12
        },
        'products': {
            'file': 'ProductList.csv',
            'description': 'Product catalog with frequencies and percentages',
            'columns': ['Product', 'Frequency', 'Percent'],
            'primary_key': 'Product',
            'row_count': 75
        },
        'special_sales': {
            'file': 'SpecialSale.csv',
            'description': 'Special sale event calendar (Diwali, Eid, etc.)',
            'columns': ['Date', 'Sales Name'],
            'primary_key': 'Date',
            'row_count': 44
        },
        'transactions': {
            'file': 'Sales.csv',
            'description': 'Individual sales transactions (1M+ rows, tab-delimited)',
            'columns': ['ID', 'Date', 'ID_Order', 'ID_Item_ordered', 'GMV', 
                       'Units', 'product_analytic_vertical', 'product_analytic_sub_category',
                       'product_analytic_category', 'product_analytic_super_category',
                       'deliverybdays', 'deliverycdays', 'MRP', 'Procurement_SLA'],
            'primary_key': 'ID_Order',
            'row_count': '1M+',
            'note': 'Use nrows parameter to limit data loading'
        }
    }
    
    # Relationship definitions
    RELATIONSHIPS = [
        {
            'from': 'monthly_data',
            'to': 'media_investment',
            'on': 'month ↔ (Year, Month)',
            'description': 'Monthly data can be joined with media investment on month'
        },
        {
            'from': 'monthly_data',
            'to': 'nps_scores',
            'on': 'Date ↔ Date',
            'description': 'Monthly data already includes NPS but can be joined for details'
        },
        {
            'from': 'monthly_data',
            'to': 'special_sales',
            'on': 'Date range match',
            'description': 'Can identify which sales events affected monthly revenue'
        },
        {
            'from': 'transactions',
            'to': 'products',
            'on': 'product_analytic_vertical ↔ Product',
            'description': 'Transaction products can be mapped to product catalog'
        }
    ]
    
    def __init__(self, data_loader=None, schema_path="config/data_schema.yaml"):
        """
        Initialize the Schema Mapper with optional data loader.
        """
        self.data_loader = data_loader
        self.llm = None
        self.yaml_schema = None
        
        # Load YAML schema if available
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    self.yaml_schema = yaml.safe_load(f)
                print(f"✅ SchemaMapperAgent: Loaded schema from {schema_path}")
            except Exception as e:
                print(f"⚠️ Could not load schema YAML: {e}")
        
        # Initialize Gemini LLM
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.llm = genai.GenerativeModel('gemini-flash-latest')
                print("✅ SchemaMapperAgent: LLM enabled")
            except Exception as e:
                print(f"⚠️ SchemaMapperAgent: LLM init failed: {e}")
    
    def get_schema_summary(self) -> str:
        """Get a text summary of the database schema for LLM context."""
        summary = "DATABASE SCHEMA:\n\n"
        
        for table_name, table_info in self.SCHEMA.items():
            summary += f"TABLE: {table_name}\n"
            summary += f"  File: {table_info['file']}\n"
            summary += f"  Description: {table_info['description']}\n"
            summary += f"  Columns: {', '.join(table_info['columns'][:8])}{'...' if len(table_info['columns']) > 8 else ''}\n"
            summary += f"  Rows: {table_info['row_count']}\n\n"
        
        summary += "\nRELATIONSHIPS:\n"
        for rel in self.RELATIONSHIPS:
            summary += f"  {rel['from']} ↔ {rel['to']}: {rel['description']}\n"
        
        return summary
    
    def map_query_to_tables(self, user_query: str) -> Dict[str, Any]:
        """
        Use LLM to determine which tables are needed for a user query.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            dict with 'tables', 'joins', 'columns', 'explanation'
        """
        if not self.llm:
            return self._fallback_mapping(user_query)
        
        prompt = f"""You are a database schema expert. Analyze this user query and determine which tables and columns are needed.

{self.get_schema_summary()}

USER QUERY: "{user_query}"

Respond in JSON format:
{{
    "primary_table": "main table to query",
    "additional_tables": ["other tables if join needed"],
    "columns_needed": ["list of specific columns"],
    "join_logic": "description of how to join tables, or null if single table",
    "reasoning": "brief explanation of why these tables"
}}"""

        try:
            response = self.llm.generate_content(prompt)
            clean = response.text.strip().replace('```json', '').replace('```', '')
            result = json.loads(clean)
            
            # Add the schema info
            result['schema'] = self.SCHEMA.get(result.get('primary_table', ''), {})
            
            return result
        except Exception as e:
            print(f"Schema mapping error: {e}")
            return self._fallback_mapping(user_query)
    
    def _fallback_mapping(self, query: str) -> Dict[str, Any]:
        """Keyword-based fallback for table mapping."""
        query_lower = query.lower()
        
        result = {
            'primary_table': 'monthly_data',
            'additional_tables': [],
            'columns_needed': [],
            'join_logic': None,
            'reasoning': 'Default mapping based on keywords'
        }
        
        # Keyword matching
        if any(word in query_lower for word in ['sales', 'revenue', 'gmv']):
            result['primary_table'] = 'monthly_data'
            result['columns_needed'] = ['month', 'Total_Sales', 'Revenue_*']
        
        if any(word in query_lower for word in ['media', 'spend', 'investment', 'tv', 'digital']):
            result['primary_table'] = 'media_investment'
            result['columns_needed'] = ['Year', 'Month', 'TV', 'Digital', 'Sponsorship']
        
        if any(word in query_lower for word in ['nps', 'brand', 'health', 'promoter']):
            result['additional_tables'].append('nps_scores')
            result['columns_needed'].append('NPS')
        
        if any(word in query_lower for word in ['product', 'catalog', 'category']):
            result['primary_table'] = 'products'
            result['columns_needed'] = ['Product', 'Frequency', 'Percent']
        
        if any(word in query_lower for word in ['sale event', 'diwali', 'special', 'festival']):
            result['additional_tables'].append('special_sales')
        
        if any(word in query_lower for word in ['transaction', 'order', 'item']):
            result['primary_table'] = 'transactions'
            result['columns_needed'] = ['Date', 'GMV', 'Units', 'product_analytic_category']
        
        return result
    
    def execute_mapped_query(self, mapping: Dict[str, Any], data_loader=None) -> pd.DataFrame:
        """
        Execute a query based on the table mapping.
        
        Args:
            mapping: Result from map_query_to_tables
            data_loader: DataLoader instance
            
        Returns:
            DataFrame with the requested data
        """
        loader = data_loader or self.data_loader
        if loader is None:
            raise ValueError("No data loader available")
        
        primary = mapping.get('primary_table', 'monthly_data')
        
        # Load primary table
        if primary == 'monthly_data':
            df = loader.get_mmm_data()
        elif primary == 'media_investment':
            df = loader.load_media_investment()
        elif primary == 'nps_scores':
            df = loader.load_nps_data()
        elif primary == 'products':
            df = loader.load_product_catalog()
        elif primary == 'special_sales':
            df = loader.load_special_sales_calendar()
        elif primary == 'transactions':
            df = loader.load_sales_transactions(nrows=10000)  # Limit for performance
        else:
            df = loader.get_mmm_data()
        
        return df
    
    def suggest_joins(self, table1: str, table2: str) -> Dict[str, Any]:
        """Suggest how to join two tables."""
        for rel in self.RELATIONSHIPS:
            if (rel['from'] == table1 and rel['to'] == table2) or \
               (rel['from'] == table2 and rel['to'] == table1):
                return {
                    'can_join': True,
                    'join_key': rel['on'],
                    'description': rel['description']
                }
        
        return {
            'can_join': False,
            'suggestion': 'These tables may not have a direct relationship. Consider intermediate joins.'
        }
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed info about a specific table."""
        return self.SCHEMA.get(table_name, {'error': f'Table {table_name} not found'})
