import json
from typing import List, Dict, Any
from src.utils.llm_interface import LLMInterface
from src.agents.orchestrator import Orchestrator

class PlanningAgent:
    """
    Planning Agent responsible for breaking down complex user goals into 
    a sequence of executable steps (a plan).
    """

    def __init__(self, orchestrator: Orchestrator, llm: LLMInterface = None):
        self.orch = orchestrator
        self.llm = llm if llm else LLMInterface()

    def create_plan(self, query: str, context: str = "") -> List[Dict[str, Any]]:
        """
        Generates a plan (list of steps) based on the user query.
        """
        if not self.llm.use_llm:
            # Fallback for when LLM is not available - treat as single step query
            return [{"step": "process_single_query", "query": query}]

        prompt = f"""You are an expert AI Planner for a Marketing Mix Modeling (MMM) Agent. 
Your goal is to break down a complex user request into a sequence of simple, executable steps.

Available Actions (Tools):
1. `get_sales_analysis`: specific to sales data, trends, or category performance.
2. `get_roi_analysis`: specific to ROI, channel efficiency, or short/long term effects.
3. `get_contributions`: specific to decomposition of sales drivers.
4. `get_correlations`: specific to relationship between variables.
5. `get_brand_health`: specific to NPS or brand metrics.
6. `get_model_performance`: specific to R2, accuracy, or model comparison.
7. `run_sql_query`: for detailed data questions not covered by above tools (e.g. "average sales where X", "count months", "top 5").
8. `answer_general`: for greetings, explanations, or summarizing.

User Query: "{query}"
Context: {context}

Output a JSON array of steps. Each step should have:
- `tool`: one of the available actions above.
- `description`: brief explanation of what this step does.
- `sub_query`: the specific question to ask the sub-agent for this step.

Example:
Query: "First show me the sales trend, then tell me which channel has the best ROI."
Plan:
[
    {{"tool": "get_sales_analysis", "description": "Analyze sales trend", "sub_query": "Show me the sales trend over time"}},
    {{"tool": "run_sql_query", "description": "Get max ROI channel", "sub_query": "Which channel has the highest ROI?"}}
]

Provide ONLY the JSON array.
"""
        try:
            response = self.llm.model.generate_content(prompt)
            # Clean up potential markdown formatting
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            plan = json.loads(clean_text)
            return plan
        except Exception as e:
            print(f"Planning Error: {e}")
            # Fallback
            return [{"step": "process_single_query", "query": query}]

    def execute_step(self, step: Dict[str, Any], bi_chat_agent) -> Dict[str, Any]:
        """
        Executes a single step of the plan using the AgenticBIChat's logic.
        This reuses the existing query processing logic but allows us to sequence it.
        """
        tool = step.get('tool')
        sub_query = step.get('sub_query')
        
        # We can leverage the existing process_query from AgenticBIChat
        # effectively treating it as a "tool" executor for these domains.
        return bi_chat_agent.process_query(sub_query)
