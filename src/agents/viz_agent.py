"""
Visualization Agent - Enhanced with NL2SQL integration.
Supports both static charts and dynamic NL-driven visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class VizAgent:
    """
    Visualization agent with NL2SQL integration for dynamic, query-driven charts.
    """
    
    def __init__(self, nl2sql_agent=None):
        """
        Initialize VizAgent with optional NL2SQL integration.
        
        Args:
            nl2sql_agent: Optional NL2SQLAgent instance for dynamic queries
        """
        self.nl2sql = nl2sql_agent
        self.llm = None
        
        # Initialize LLM for chart type detection
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.llm = genai.GenerativeModel('gemini-flash-latest')
                print("✅ VizAgent: LLM-powered chart selection enabled")
            except Exception as e:
                print(f"⚠️ VizAgent: LLM init failed: {e}")
    
    def set_nl2sql(self, nl2sql_agent):
        """Set the NL2SQL agent for dynamic queries."""
        self.nl2sql = nl2sql_agent
    
    def _detect_chart_type(self, query: str, data_preview: str) -> dict:
        """Use LLM to detect the best chart type for the query."""
        if not self.llm:
            return {"chart_type": "bar", "x": None, "y": None, "color": None}
        
        prompt = f"""You are a data visualization expert. Based on this query and data, determine the best chart type.

Query: "{query}"

Data Preview:
{data_preview}

Choose from: bar, line, pie, scatter, heatmap, histogram, box

Respond in JSON:
{{
    "chart_type": "bar|line|pie|scatter|heatmap|histogram|box",
    "x": "column_name for x-axis or null",
    "y": "column_name for y-axis or null",
    "color": "column_name for color grouping or null",
    "title": "suggested chart title",
    "reasoning": "brief explanation"
}}"""

        try:
            response = self.llm.generate_content(prompt)
            clean = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(clean)
        except Exception as e:
            print(f"Chart detection failed: {e}")
            return {"chart_type": "bar", "x": None, "y": None, "color": None, "title": "Chart"}

    def create_dynamic_chart(self, query: str, data: pd.DataFrame = None) -> dict:
        """
        Create a chart dynamically based on natural language query.
        
        Args:
            query: Natural language visualization request
            data: Optional DataFrame. If None, uses NL2SQL to get data.
            
        Returns:
            dict with 'chart', 'data', 'explanation'
        """
        result_data = data
        sql_code = None
        
        # Step 1: If no data provided, use NL2SQL to get it
        if result_data is None and self.nl2sql:
            print(f"📊 VizAgent: Querying data for '{query[:50]}...'")
            nl2sql_result = self.nl2sql.execute_query(query)
            
            if nl2sql_result.get('error'):
                return {
                    'chart': None,
                    'data': None,
                    'explanation': f"Could not get data: {nl2sql_result['error']}"
                }
            
            result_data = nl2sql_result.get('result')
            sql_code = nl2sql_result.get('sql_equivalent')
            
            if result_data is None:
                return {
                    'chart': None,
                    'data': None,
                    'explanation': "Query returned no data"
                }
        
        # Convert to DataFrame if not already
        if not isinstance(result_data, pd.DataFrame):
            if isinstance(result_data, (int, float, str)):
                # Single value - create simple bar
                result_data = pd.DataFrame({'Value': [result_data], 'Label': ['Result']})
            elif isinstance(result_data, dict):
                result_data = pd.DataFrame(list(result_data.items()), columns=['Key', 'Value'])
            elif isinstance(result_data, pd.Series):
                result_data = result_data.reset_index()
                result_data.columns = ['Label', 'Value']
        
        # Step 2: Detect best chart type using LLM
        data_preview = result_data.head(5).to_string() if len(result_data) > 0 else "Empty"
        chart_config = self._detect_chart_type(query, data_preview)
        
        # Step 3: Create the chart
        chart_type = chart_config.get('chart_type', 'bar')
        title = chart_config.get('title', 'Query Result')
        
        try:
            fig = self._create_chart(result_data, chart_type, chart_config, title)
            
            explanation = f"**Chart Type:** {chart_type.title()}\n"
            if sql_code:
                explanation += f"**Query:** `{sql_code}`\n"
            if chart_config.get('reasoning'):
                explanation += f"**Why this chart:** {chart_config['reasoning']}"
            
            return {
                'chart': fig,
                'data': result_data,
                'explanation': explanation
            }
        except Exception as e:
            return {
                'chart': None,
                'data': result_data,
                'explanation': f"Chart creation failed: {e}"
            }

    def _create_chart(self, df: pd.DataFrame, chart_type: str, config: dict, title: str):
        """Create a Plotly chart based on type and config."""
        x_col = config.get('x') or (df.columns[0] if len(df.columns) > 0 else None)
        y_col = config.get('y') or (df.columns[1] if len(df.columns) > 1 else df.columns[0])
        color_col = config.get('color')
        
        # Validate columns exist
        if x_col and x_col not in df.columns:
            x_col = df.columns[0] if len(df.columns) > 0 else None
        if y_col and y_col not in df.columns:
            y_col = df.columns[-1] if len(df.columns) > 0 else None
        if color_col and color_col not in df.columns:
            color_col = None
        
        if chart_type == 'bar':
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == 'line':
            fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title, markers=True)
        elif chart_type == 'pie':
            values_col = y_col or (df.select_dtypes(include='number').columns[0] if len(df.select_dtypes(include='number').columns) > 0 else None)
            names_col = x_col or (df.select_dtypes(exclude='number').columns[0] if len(df.select_dtypes(exclude='number').columns) > 0 else None)
            fig = px.pie(df, values=values_col, names=names_col, title=title)
        elif chart_type == 'scatter':
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == 'heatmap':
            numeric_df = df.select_dtypes(include='number')
            if len(numeric_df.columns) > 1:
                fig = px.imshow(numeric_df.corr(), text_auto=True, title=title)
            else:
                fig = px.bar(df, x=x_col, y=y_col, title=title)
        elif chart_type == 'histogram':
            fig = px.histogram(df, x=y_col or x_col, title=title)
        elif chart_type == 'box':
            fig = px.box(df, x=x_col, y=y_col, title=title)
        else:
            fig = px.bar(df, x=x_col, y=y_col, title=title)
        
        return fig

    # ==================== STATIC CHART METHODS ====================
    # (Original methods preserved for backward compatibility)
    
    def plot_sales_trend(self, data):
        """Plots Sales vs Total Media Spend."""
        df_plot = data.copy()
        media_cols = ['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']
        existing_media = [c for c in media_cols if c in df_plot.columns]
        df_plot['Total Media Spend'] = df_plot[existing_media].sum(axis=1)
        
        fig = px.line(df_plot, x='Date', y=['Total_Sales', 'Total Media Spend'], title="Sales vs Media Spend Trend")
        return fig

    def plot_roi(self, roi_dict):
        """Plots ROI Bar Chart."""
        df = pd.DataFrame(list(roi_dict.items()), columns=['Channel', 'ROI'])
        fig = px.bar(df, x='Channel', y='ROI', color='ROI', title="Marginal ROI by Channel")
        return fig

    def plot_categories(self, cat_df):
        """Plots Category Sales Pie Chart."""
        fig = px.pie(cat_df, values='Sales', names='Category', title="Sales Distribution by Category")
        return fig

    def plot_contributions(self, contrib_dict):
        """Plots Contribution Waterfall/Bar."""
        df = pd.DataFrame(list(contrib_dict.items()), columns=['Source', 'Contribution'])
        fig = px.bar(df, x='Source', y='Contribution', title="Total Sales Contribution by Source")
        return fig

    def plot_correlation(self, corr_matrix):
        """Plots Correlation Heatmap."""
        fig = px.imshow(corr_matrix, text_auto=True, title="Spend vs Sales Correlation")
        return fig
    
    def plot_roi_decomposition(self, roi_decomp):
        """Plots Short-term vs Long-term ROI."""
        channels = list(roi_decomp.keys())
        immediate = [roi_decomp[ch]['immediate'] for ch in channels]
        longterm = [roi_decomp[ch]['longterm'] for ch in channels]
        
        fig = go.Figure(data=[
            go.Bar(name='Immediate', x=channels, y=immediate),
            go.Bar(name='Long-term (Adstock)', x=channels, y=longterm)
        ])
        fig.update_layout(barmode='stack', title="ROI Decomposition: Short-term vs Long-term")
        return fig
    
    def plot_model_comparison(self, model_results):
        """Plots comparison of model performance."""
        models = list(model_results.keys())
        r2_scores = [model_results[m]['r2'] for m in models]
        
        fig = px.bar(x=models, y=r2_scores, title="Model Comparison (R² Score)",
                     labels={'x': 'Model', 'y': 'R² Score'})
        fig.update_layout(yaxis_range=[0, 1])
        return fig
    
    def plot_nps_trend(self, nps_data):
        """Plots NPS trend over time."""
        fig = px.line(nps_data, x='Date', y='NPS', title="Brand Health: NPS Trend",
                      markers=True)
        return fig
    
    def plot_spend_mix(self, data):
        """Plots media spend distribution as a pie chart."""
        media_cols = ['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']
        existing_media = [c for c in media_cols if c in data.columns]
        
        spend_totals = data[existing_media].sum()
        spend_df = pd.DataFrame({
            'Channel': spend_totals.index,
            'Spend': spend_totals.values
        })
        
        fig = px.pie(spend_df, values='Spend', names='Channel', 
                     title="Media Spend Distribution",
                     hole=0.4)
        return fig
    
    def plot_channel_efficiency(self, data, roi_dict):
        """Plots channel efficiency (Spend vs ROI scatter)."""
        media_cols = ['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']
        existing_media = [c for c in media_cols if c in data.columns]
        
        spend_totals = data[existing_media].sum()
        
        efficiency_data = []
        for channel in existing_media:
            if channel in roi_dict:
                efficiency_data.append({
                    'Channel': channel,
                    'Total Spend': spend_totals[channel],
                    'ROI': roi_dict[channel]
                })
        
        efficiency_df = pd.DataFrame(efficiency_data)
        
        fig = px.scatter(efficiency_df, x='Total Spend', y='ROI', 
                        text='Channel', size='Total Spend',
                        title="Channel Efficiency: Spend vs ROI",
                        labels={'Total Spend': 'Total Spend ($)', 'ROI': 'Marginal ROI'})
        fig.update_traces(textposition='top center')
        return fig
