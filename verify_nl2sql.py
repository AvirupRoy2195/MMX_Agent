import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.orchestrator import Orchestrator
from src.agents.agentic_bi_chat import AgenticBIChat

print("Initializing Orchestrator...")
orch = Orchestrator()
# Run basic analysis to populate data
orch.run_analysis()

print("\nInitializing Chat Agent with NL2SQL...")
chat_agent = AgenticBIChat(orch)
chat_agent.set_analysis_results(orch.model_results, orch.advanced_results if hasattr(orch, 'advanced_results') else None)

# Test Cases
queries = [
    "What is the average sales?",
    "Show me the top 3 months by sales",
    "Count the number of months where Sales were above 100000"
]

print("\n=== Testing NL2SQL Queries ===")

for q in queries:
    print(f"\nQuery: {q}")
    response = chat_agent.process_query(q)
    print("-" * 50)
    print(response['text'][:500] + "..." if len(response['text']) > 500 else response['text'])
    print("-" * 50)

print("\n✅ Verification Complete")
