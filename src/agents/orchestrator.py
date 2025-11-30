from src.data_loader import DataLoader
from src.agents.explorer_agent import ExplorerAgent
from src.agents.mmx_agent import MMXAgent
from src.agents.viz_agent import VizAgent
from src.agents.critique_agent import CritiqueAgent
from src.agents.brand_agent import BrandAgent
from src.models.advanced_mmm import AdvancedMMM

class Orchestrator:
    def __init__(self):
        self.loader = DataLoader()
        self.data = self.loader.get_mmm_data()
        
        # Initialize Sub-Agents
        self.explorer = ExplorerAgent(self.data)
        self.mmx = MMXAgent()
        self.viz = VizAgent()
        self.critique = CritiqueAgent()
        self.brand = BrandAgent(self.data)
        self.advanced_mmm = AdvancedMMM(decay_rate=0.5)
        
        # State
        self.model_trained = False
        self.model_results = None
        self.advanced_results = None

    def run_analysis(self):
        """Runs the full analysis pipeline."""
        if self.data is None:
            return {"error": "No data found"}
        
        # 1. Train Model
        self.model_results = self.mmx.train_model(self.data)
        self.model_trained = True
        
        # 2. Get Insights
        kpis = self.explorer.get_kpis()
        roi = self.mmx.get_roi()
        contributions = self.mmx.get_contributions(self.data)
        categories = self.loader.get_category_data(self.data) # Use loader or explorer
        correlations = self.explorer.analyze_correlations()
        
        # 3. Critique
        model_feedback = self.critique.evaluate_model(self.model_results)
        data_feedback = self.critique.evaluate_data(self.data)
        
        return {
            "kpis": kpis,
            "roi": roi,
            "contributions": contributions,
            "categories": categories,
            "correlations": correlations,
            "feedback": model_feedback + data_feedback,
            "model_results": self.model_results
        }

    def get_plots(self, analysis_results):
        """Generates plots based on analysis."""
        plots = {}
        if self.data is not None:
            plots['trend'] = self.viz.plot_sales_trend(self.data)
        
        if analysis_results.get('roi'):
            plots['roi'] = self.viz.plot_roi(analysis_results['roi'])
            
        if analysis_results.get('categories') is not None:
            plots['categories'] = self.viz.plot_categories(analysis_results['categories'])
            
        if analysis_results.get('contributions'):
            plots['contributions'] = self.viz.plot_contributions(analysis_results['contributions'])
            
        if analysis_results.get('correlations') is not None:
            plots['correlation'] = self.viz.plot_correlation(analysis_results['correlations'])
            
        return plots


    def simulate(self, inputs):
        return self.mmx.predict(inputs)
    
    def run_advanced_analysis(self):
        """Runs advanced MMM with adstock and brand equity."""
        if self.data is None:
            return {"error": "No data found"}
        
        # Get media columns
        media_cols = ['TV', 'Digital', 'Sponsorship', 'Content.Marketing', 'Online.marketing', 'Affiliates', 'SEM', 'Radio', 'Other']
        media_cols = [c for c in media_cols if c in self.data.columns]
        
        # Train advanced models
        self.advanced_results = self.advanced_mmm.train(self.data, media_cols)
        
        # Get decomposition
        roi_decomp = self.advanced_mmm.get_roi_decomposition()
        brand_impact = self.advanced_mmm.get_brand_impact()
        
        # Brand analysis
        nps_stats = self.brand.get_nps_stats()
        nps_correlation = self.brand.analyze_nps_sales_correlation()
        
        return {
            'model_comparison': self.advanced_results,
            'roi_decomposition': roi_decomp,
            'brand_impact': brand_impact,
            'nps_stats': nps_stats,
            'nps_correlation': nps_correlation
        }

