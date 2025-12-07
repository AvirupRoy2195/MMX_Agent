import pandas as pd
import json
from src.utils.llm_interface import LLMInterface

class NL2SQLAgent:
    """
    Agent that converts Natural Language to Pandas operations using an LLM.
    """
    def __init__(self, data: pd.DataFrame, llm: LLMInterface = None):
        self.data = data
        self.llm = llm if llm else LLMInterface()
        self.columns = list(data.columns) if data is not None else []

    def execute_query(self, query: str) -> dict:
        """
        Translates NL query to Pandas code and executes it.
        """
        print(f"DEBUG: NL2SQLAgent executing: {query}")
        print(f"DEBUG: LLM Available: {self.llm.use_llm}")
        
        if not self.llm.use_llm:
            print("DEBUG: LLM is FALSE")

            return {
                "result": None,
                "sql_equivalent": "LLM not available",
                "error": "LLM required for this feature"
            }

        # prompt construction
        data_head = self.data.head(3).to_markdown(index=False)
        prompt = f"""You are a Python Data Analyst.
You have a pandas DataFrame named `df`.
Columns: {self.columns}
Sample data:
{data_head}

User Question: "{query}"

Write the python code to answer this question.
1. Assign the final result to a variable named `result`.
2. `result` can be a single number, string, or a DataFrame.
3. Do NOT import pandas. Assume `df` and `pd` are available.
4. Wrap your code in a JSON block with keys "code" and "explanation".

Example Response:
{{
    "code": "result = df.groupby('Channel')['Sales'].sum().sort_values(ascending=False)",
    "explanation": "Grouping by Channel and summing Sales."
}}
"""
        try:
            print("DEBUG: Sending prompt to LLM...")
            response = self.llm.model.generate_content(prompt)
            print(f"DEBUG: LLM Response len: {len(response.text)}")
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            parsed = json.loads(clean_text)
            code = parsed.get('code', '')
            explanation = parsed.get('explanation', '')
            
            # Execute code safely
            local_vars = {'df': self.data, 'pd': pd}
            exec(code, {}, local_vars)
            
            result = local_vars.get('result')
            
            return {
                "result": result,
                "sql_equivalent": code,
                "explanation": explanation
            }
            
        except Exception as e:
            return {
                "result": None,
                "sql_equivalent": "Error generating/executing query",
                "error": str(e)
            }
