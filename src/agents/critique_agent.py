class CritiqueAgent:
    def evaluate_model(self, results):
        """Critiques the model results."""
        feedback = []
        r2 = results.get('r2', 0)
        
        if r2 < 0.5:
            feedback.append(f"⚠️ **Low Model Accuracy**: R-Squared is only {r2:.2f}. The model explains less than 50% of sales variation.")
        elif r2 > 0.95:
            feedback.append(f"✅ **High Accuracy**: Excellent fit ({r2:.2f}), but check for overfitting.")
        else:
            feedback.append(f"ℹ️ **Moderate Accuracy**: Model explains {r2:.2f} of variation.")

        # Check for negative coefficients (usually bad in MMM unless price/competitor)
        negatives = [k for k, v in results.get('coefficients', {}).items() if v < 0]
        if negatives:
            feedback.append(f"⚠️ **Negative ROI Detected**: The following channels have negative impact: {', '.join(negatives)}. This might indicate data issues, multicollinearity, or inefficient spend.")
        
        return feedback

    def evaluate_data(self, data):
        """Critiques the data quality."""
        feedback = []
        if len(data) < 24:
            feedback.append("⚠️ **Small Dataset**: Less than 24 data points. Seasonality might be hard to capture.")
        return feedback
