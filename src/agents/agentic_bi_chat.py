class AgenticBIChat:
    """
    Enhanced chat agent that can answer questions AND generate visualizations dynamically.
    Combines natural language understanding with BI capabilities.
    """
    
    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.analysis = None
        self.advanced = None
        
    def set_analysis_results(self, analysis, advanced):
        """Store analysis results for quick access."""
        self.analysis = analysis
        self.advanced = advanced
    
    def process_query(self, query):
        """
        Process user query and return both text response and optional visualization.
        
        Returns:
            dict with 'text' and optional 'chart' keys
        """
        query_lower = query.lower()
        
        # ROI Queries
        if "roi" in query_lower or "return on investment" in query_lower:
            if "decomp" in query_lower or "short" in query_lower or "long" in query_lower:
                # Advanced ROI decomposition
                roi_decomp = self.advanced.get('roi_decomposition')
                if roi_decomp:
                    text = "Here's the ROI breakdown by short-term and long-term effects:\n\n"
                    for channel, values in list(roi_decomp.items())[:5]:
                        text += f"**{channel}**:\n"
                        text += f"  - Immediate: {values['immediate']:.2f}\n"
                        text += f"  - Long-term: {values['longterm']:.2f}\n"
                        text += f"  - **Total: {values['total']:.2f}**\n\n"
                    
                    chart = self.orch.viz.plot_roi_decomposition(roi_decomp)
                    return {'text': text, 'chart': chart}
            else:
                # Basic ROI
                roi = self.analysis.get('roi', {})
                sorted_roi = dict(sorted(roi.items(), key=lambda x: x[1], reverse=True))
                text = "**Marginal ROI by Channel** (Sales per $1 spent):\n\n"
                for channel, value in list(sorted_roi.items())[:5]:
                    text += f"- **{channel}**: ${value:.2f}\n"
                
                chart = self.orch.viz.plot_roi(roi)
                return {'text': text, 'chart': chart}
        
        # Sales Queries
        elif "sales" in query_lower:
            if "category" in query_lower or "product" in query_lower:
                # Sales by category
                categories = self.analysis.get('categories')
                if categories is not None:
                    text = "**Sales by Product Category**:\n\n"
                    for _, row in categories.head(5).iterrows():
                        text += f"- {row['Category']}: ${row['Sales']:,.0f}\n"
                    
                    chart = self.orch.viz.plot_categories(categories)
                    return {'text': text, 'chart': chart}
            
            elif "trend" in query_lower or "over time" in query_lower:
                # Sales trend
                text = "Here's the sales trend over time compared to media spend."
                chart = self.orch.viz.plot_sales_trend(self.orch.data)
                return {'text': text, 'chart': chart}
            
            else:
                # Total sales
                kpis = self.analysis.get('kpis', {})
                total_sales = kpis.get('Total Sales', 0)
                text = f"**Total Sales**: ${total_sales:,.0f}\n\n"
                text += f"**Total Media Spend**: ${kpis.get('Total Spend', 0):,.0f}\n"
                text += f"**Data Points**: {kpis.get('Data Points', 0)} months"
                return {'text': text}
        
        # Contribution Queries
        elif "contribution" in query_lower or "impact" in query_lower:
            contributions = self.analysis.get('contributions')
            if contributions:
                text = "**Sales Contribution by Source**:\n\n"
                sorted_contrib = dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True))
                for source, value in list(sorted_contrib.items())[:5]:
                    text += f"- {source}: ${value:,.0f}\n"
                
                chart = self.orch.viz.plot_contributions(contributions)
                return {'text': text, 'chart': chart}
        
        # Correlation Queries
        elif "correlation" in query_lower or "relationship" in query_lower:
            corr = self.analysis.get('correlations')
            if corr is not None:
                text = "Here's the correlation matrix showing relationships between media channels and sales."
                chart = self.orch.viz.plot_correlation(corr)
                return {'text': text, 'chart': chart}
        
        # Brand/NPS Queries
        elif "brand" in query_lower or "nps" in query_lower:
            nps_stats = self.advanced.get('nps_stats', {})
            nps_corr = self.advanced.get('nps_correlation')
            
            text = "**Brand Health (NPS Analysis)**:\n\n"
            text += f"- Average NPS: {nps_stats.get('mean', 0):.1f}\n"
            text += f"- NPS Range: {nps_stats.get('min', 0):.1f} - {nps_stats.get('max', 0):.1f}\n"
            if nps_corr:
                text += f"- NPS-Sales Correlation: {nps_corr:.2f}\n"
            
            nps_trend = self.orch.brand.get_nps_trend()
            if nps_trend is not None:
                chart = self.orch.viz.plot_nps_trend(nps_trend)
                return {'text': text, 'chart': chart}
            
            return {'text': text}
        
        # Model Performance Queries
        elif "model" in query_lower or "accuracy" in query_lower or "performance" in query_lower:
            model_comp = self.advanced.get('model_comparison', {})
            
            text = "**Model Performance Comparison**:\n\n"
            text += f"1. **Immediate Only**: R² = {model_comp['immediate']['r2']:.3f}\n"
            text += f"2. **With Adstock**: R² = {model_comp['adstock']['r2']:.3f}\n"
            text += f"3. **Full Model**: R² = {model_comp['full']['r2']:.3f}\n\n"
            text += "The Full Model includes both adstock (carryover effects) and brand equity (NPS)."
            
            chart = self.orch.viz.plot_model_comparison(model_comp)
            return {'text': text, 'chart': chart}
        
        # Critique/Feedback Queries
        elif "critique" in query_lower or "feedback" in query_lower or "issue" in query_lower:
            feedback = self.analysis.get('feedback', [])
            text = "**Critique Agent Feedback**:\n\n"
            for msg in feedback:
                text += f"{msg}\n\n"
            return {'text': text}
        
        # Spend Mix Queries
        elif "spend mix" in query_lower or "budget" in query_lower or "allocation" in query_lower:
            text = "Here's how your media budget is allocated across channels."
            chart = self.orch.viz.plot_spend_mix(self.orch.data)
            return {'text': text, 'chart': chart}
        
        # Channel Efficiency Queries
        elif "efficiency" in query_lower or "best channel" in query_lower or "optimize" in query_lower:
            roi = self.analysis.get('roi', {})
            text = "**Channel Efficiency Analysis**\n\n"
            text += "This scatter plot shows each channel's total spend vs ROI. \n"
            text += "Channels in the top-right are most efficient (high ROI, high spend). \n"
            text += "Channels in the top-left have high ROI but low spend (opportunity to scale)."
            
            chart = self.orch.viz.plot_channel_efficiency(self.orch.data, roi)
            return {'text': text, 'chart': chart}
        
        # Help/Capabilities
        else:
            text = """**I'm your Agentic BI Assistant!** 🤖 Ask me about:

📊 **Sales Analysis**
- "Show me sales by category"
- "What's the sales trend?"
- "Total sales"

💰 **ROI & Performance**
- "Show me ROI"
- "ROI decomposition" (short vs long-term)
- "Which channel has best ROI?"

🎯 **Contributions**
- "Show me contributions"
- "What's the impact of each channel?"

📈 **Correlations**
- "Show correlations"
- "Relationship between channels"

💵 **Budget & Efficiency**
- "Show me spend mix"
- "Budget allocation"
- "Channel efficiency"
- "Which channel should I optimize?"

🏆 **Brand Health**
- "Show me NPS"
- "Brand analysis"

🔍 **Model Performance**
- "Model accuracy"
- "Compare models"

I'll provide both insights AND visualizations!"""
            return {'text': text}
