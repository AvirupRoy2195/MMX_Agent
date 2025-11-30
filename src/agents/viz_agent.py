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
                     hole=0.4)  # Donut chart
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
