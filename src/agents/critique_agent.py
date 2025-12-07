"""
Critique Agent - Evaluates model results and data quality.
Uses Gemini API for LLM-powered intelligent critiques.
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class CritiqueAgent:
    """
    Agent that critiques model results and data quality.
    Uses Gemini for intelligent, context-aware feedback.
    """
    
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.model = genai.GenerativeModel('gemini-flash-latest')
                print("✅ CritiqueAgent initialized with Gemini")
            except Exception as e:
                print(f"⚠️ CritiqueAgent: Gemini init failed: {e}")
    
    def evaluate_model(self, results):
        """Critiques the model results using LLM if available."""
        feedback = []
        r2 = results.get('r2', 0)
        coefficients = results.get('coefficients', {})
        
        # Rule-based checks (always run)
        if r2 < 0.5:
            feedback.append(f"⚠️ **Low Model Accuracy**: R² is only {r2:.2f}. The model explains less than 50% of sales variation.")
        elif r2 > 0.95:
            feedback.append(f"✅ **High Accuracy**: Excellent fit ({r2:.2f}), but check for overfitting.")
        else:
            feedback.append(f"ℹ️ **Moderate Accuracy**: Model explains {r2:.2%} of variation.")

        # Check for negative coefficients
        negatives = [k for k, v in coefficients.items() if v < 0]
        if negatives:
            feedback.append(f"⚠️ **Negative ROI Detected**: {', '.join(negatives)} have negative impact.")
        
        # LLM-powered deep critique (if available)
        if self.model and coefficients:
            try:
                prompt = f"""You are a Marketing Mix Modeling expert. Analyze these model results and provide 2-3 bullet points of critique:

R-Squared: {r2:.4f}
Coefficients: {coefficients}

Focus on:
1. Overall model quality
2. Any surprising or concerning coefficient values
3. Recommendations for improvement

Be concise. Use markdown bullet points."""
                
                response = self.model.generate_content(prompt)
                feedback.append("\n**🤖 AI Analysis:**\n" + response.text)
            except Exception as e:
                feedback.append(f"(LLM critique unavailable: {e})")
        
        return feedback

    def evaluate_data(self, data):
        """Critiques the data quality."""
        feedback = []
        
        if len(data) < 24:
            feedback.append("⚠️ **Small Dataset**: Less than 24 data points. Seasonality might be hard to capture.")
        
        if len(data) < 52:
            feedback.append("ℹ️ **Tip**: For robust MMM, aim for 52+ weekly observations (1 year).")
        
        # Check for missing values
        missing = data.isnull().sum().sum()
        if missing > 0:
            feedback.append(f"⚠️ **Missing Data**: {missing} missing values detected.")
        
        return feedback
    
    def generate_recommendations(self, analysis_results):
        """Generate strategic recommendations using Gemini."""
        if not self.model:
            return ["LLM not available for recommendations. Set GEMINI_API_KEY."]
        
        try:
            roi = analysis_results.get('roi', {})
            contributions = analysis_results.get('contributions', {})
            
            prompt = f"""You are a Marketing strategist. Based on this analysis, provide 3 actionable recommendations:

Channel ROI: {roi}
Channel Contributions: {contributions}

Format as numbered list. Be specific and actionable."""

            response = self.model.generate_content(prompt)
            return [response.text]
        except Exception as e:
            return [f"Recommendation generation failed: {e}"]
