from src.data_loader import DataLoader
from src.model import MMXModel
import pandas as pd

class MMXAgent:
    def __init__(self):
        self.loader = DataLoader()
        self.model = MMXModel()
        self.data = None
        self.training_results = None

    def load_and_train(self):
        """Loads data and trains the model."""
        self.data = self.loader.get_mmm_data()
        if self.data is not None:
            self.training_results = self.model.train(self.data)
            return True
        return False

    def get_summary(self):
        """Returns a summary of the dataset."""
        if self.data is None:
            return "Data not loaded."
        
        summary = {
            "Total Sales": self.data['Total_Sales'].sum(),
            "Total Spend": self.data[self.model.features].sum().sum(),
            "Data Points": len(self.data)
        }
        return summary

    def get_roi_insights(self):
        """Returns ROI insights."""
        if not self.training_results:
            return "Model not trained."
        
        coefs = self.training_results['coefficients']
        # Sort by impact
        sorted_coefs = dict(sorted(coefs.items(), key=lambda item: item[1], reverse=True))
        return sorted_coefs

    def simulate_scenario(self, inputs):
        """Simulates a scenario with new spend values."""
        return self.model.predict(inputs)
    
    def chat(self, query):
        """Simple rule-based chat interface."""
        query = query.lower()
        if "roi" in query or "return" in query:
            rois = self.get_roi_insights()
            if isinstance(rois, str): return rois
            response = "Estimated Return on Investment (Marginal Sales per unit Spend):\n"
            for channel, val in rois.items():
                response += f"- **{channel}**: {val:.2f}\n"
            return response
        
        elif "sales" in query and "total" in query:
            summary = self.get_summary()
            return f"Total Sales in dataset: {summary['Total Sales']:,.2f}"
        
        elif "model" in query or "accuracy" in query:
            if self.training_results:
                return f"Model R-Squared: {self.training_results['r2']:.2f}"
            return "Model not trained."
            
        else:
            return "I can help you with: \n- ROI analysis ('Show me ROI')\n- Total Sales ('Total sales')\n- Model Accuracy ('Model accuracy')"
