import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class VizAgent:
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
