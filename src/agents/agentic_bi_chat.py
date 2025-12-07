import pandas as pd

class AgenticBIChat:
    """
    Enhanced chat agent with:
    - Natural language understanding (LLM-powered)
    - Conversational memory
    - Dynamic visualizations
    - NL to SQL
    """
    
    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.analysis = None
        self.advanced = None
        self.nl_to_sql = None
        self.memory = None
        self.llm = None
        
        # Initialize NL to SQL if data is available
        # Initialize NL to SQL if data is available
        if self.orch.data is not None:
            from src.agents.nl2sql_agent import NL2SQLAgent
            self.nl_to_sql = NL2SQLAgent(self.orch.data, self.llm)
        
        # Initialize memory
        from src.utils.memory import ConversationMemory
        self.memory = ConversationMemory(max_history=10)
        
        # Initialize LLM (optional - works without API key)
        from src.utils.llm_interface import LLMInterface
        self.llm = LLMInterface()

        # Initialize Planning Agent
        from src.agents.planning_agent import PlanningAgent
        self.planner = PlanningAgent(self.orch, self.llm)
        
        # Initialize Council Agent (optional - for complex queries)
        self.council = None
        self.use_council = False
        try:
            from src.agents.council_agent import CouncilAgent
            self.council = CouncilAgent()
            print("✅ LLM Council available")
        except Exception as e:
            print(f"⚠️ LLM Council not available: {e}")
        
        # Link VizAgent with NL2SQL for dynamic visualizations
        if hasattr(self.orch, 'viz') and self.nl_to_sql:
            self.orch.viz.set_nl2sql(self.nl_to_sql)
            print("✅ VizAgent linked with NL2SQL for dynamic charts")
        
    def set_analysis_results(self, analysis, advanced):
        """Store analysis results for quick access."""
        self.analysis = analysis
        self.advanced = advanced
    
    def process_query(self, query):
        """
        Process user query with memory and LLM understanding.
        
        Returns:
            dict with 'text' and optional 'chart' keys
        """
        # Resolve references using memory ("it", "that", "also", etc.)
        if self.memory:
            query = self.memory.resolve_reference(query)
            context = self.memory.get_context_summary()
        else:
            context = ""
        
        # Use LLM to parse intent if available
        if self.llm and self.llm.use_llm:
            intent_data = self.llm.parse_intent(query, context)
            query_type = intent_data.get('query_type', 'help')
            entities = intent_data.get('entities', {})
            
            # Update memory with entities
            if self.memory:
                self.memory.update_context(
                    query_type=query_type,
                    channels=entities.get('channels', []),
                    metrics=entities.get('metrics', [])
                )
        else:
            # Fallback to keyword matching
            query_type = self._detect_query_type(query)

        # CHECK FOR MULTI-STEP PLAN
        # Use planner if query seems complex (contains "and", "then", or explicit multi-part request)
        if self.llm.use_llm and (" and " in query.lower() or " then " in query.lower() or "," in query):
            plan = self.planner.create_plan(query, context)
            
            # If valid plan with multiple steps is created
            if isinstance(plan, list) and len(plan) > 1:
                combined_text = "**I've broken this down into steps:**\n\n"
                final_chart = None
                
                for i, step in enumerate(plan):
                    step_result = self.planner.execute_step(step, self)
                    combined_text += f"**Step {i+1}: {step.get('description', '')}**\n"
                    combined_text += f"{step_result['text']}\n\n"
                    if step_result.get('chart'):
                        final_chart = step_result['chart'] # Keep the last chart for now
                
                return {'text': combined_text, 'chart': final_chart}
        
        query_lower = query.lower()
        
        # Check if this is a visualization query with dynamic data request
        viz_keywords = ['chart', 'plot', 'visualize', 'graph', 'show me a', 'draw', 'display']
        is_viz_query = any(keyword in query_lower for keyword in viz_keywords)
        
        if is_viz_query and hasattr(self.orch, 'viz') and hasattr(self.orch.viz, 'create_dynamic_chart'):
            viz_result = self.orch.viz.create_dynamic_chart(query)
            
            if viz_result.get('chart'):
                return {
                    'text': f"📊 **Dynamic Chart Generated**\n\n{viz_result.get('explanation', '')}",
                    'chart': viz_result['chart']
                }
        
        # Check if this is a SQL-style query (aggregations, filters, etc.)
        sql_keywords = ['average', 'mean', 'sum', 'total', 'count', 'max', 'min', 'top', 'group by', 'where']
        is_sql_query = any(keyword in query_lower for keyword in sql_keywords)
        
        if is_sql_query and self.nl_to_sql:
            result = self.nl_to_sql.execute_query(query_lower)
            
            if result.get('result') is not None and not result.get('error'):
                text = f"**Query Result**\n\n"
                text += f"Executed Code: `{result['sql_equivalent']}`\n"
                text += f"Explanation: {result.get('explanation', '')}\n\n"
                
                if isinstance(result['result'], pd.DataFrame):
                    text += "**Data:**\n\n"
                    text += result['result'].to_markdown(index=False)
                else:
                    text += f"**Result:** {result['result']}"
                
                return {'text': text}
        
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
        
        # Fallback: Use NL2SQL for any unrecognized query
        else:
            # Try NL2SQL for flexible query support
            if self.nl_to_sql and self.llm and self.llm.use_llm:
                print(f"DEBUG: Fallback to NL2SQL for: {query}")
                result = self.nl_to_sql.execute_query(query)
                
                if result.get('result') is not None and not result.get('error'):
                    text = f"**Query Result**\n\n"
                    text += f"Executed Code: `{result['sql_equivalent']}`\n"
                    text += f"Explanation: {result.get('explanation', '')}\n\n"
                    
                    if isinstance(result['result'], pd.DataFrame):
                        text += "**Data:**\n\n"
                        text += result['result'].to_markdown(index=False)
                    else:
                        text += f"**Result:** {result['result']}"
                    
                    return {'text': text}
                elif result.get('error'):
                    text = f"I tried to answer your query but encountered an issue:\n\n"
                    text += f"Error: {result.get('error')}\n\n"
                    text += "Try rephrasing your question or ask for 'help' to see examples."
                    return {'text': text}
            
            # Final fallback: Show help
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

🗃️ **SQL-Style Queries** (NEW!)
- "Average sales by month"
- "Total spend on TV"
- "Top 5 months by sales"
- "Count of data points"
- "Show me Digital spend"


I'll provide both insights AND visualizations!"""
            return {'text': text}
    
    def _detect_query_type(self, query):
        """Fallback query type detection using keywords."""
        query_lower = query.lower()
        
        if "roi" in query_lower:
            return "roi"
        elif "sales" in query_lower:
            return "sales"
        elif "correlation" in query_lower:
            return "correlation"
        elif "contribution" in query_lower:
            return "contribution"
        elif "brand" in query_lower or "nps" in query_lower:
            return "brand"
        elif "model" in query_lower:
            return "model"
        elif "spend mix" in query_lower or "budget" in query_lower:
            return "budget"
        elif "efficiency" in query_lower:
            return "efficiency"
        else:
            return "help"
