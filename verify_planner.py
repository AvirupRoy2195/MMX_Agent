import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.orchestrator import Orchestrator
from src.agents.agentic_bi_chat import AgenticBIChat
from src.agents.planning_agent import PlanningAgent

print("Initializing Orchestrator...")
orch = Orchestrator()
# Run basic analysis to populate data
orch.run_analysis()
orch.run_advanced_analysis()

print("\nInitializing Chat Agent with Planner...")
chat_agent = AgenticBIChat(orch)
chat_agent.set_analysis_results(orch.model_results, orch.advanced_results)

# Test Cases
queries = [
    "Show me the sales trend", # Simple query (should skip planner or single step)
    "First show me the sales trend, then tell me which channel has the best ROI." # Complex query
]

print("\n=== Testing Queries ===")

for q in queries:
    print(f"\nQuery: {q}")
    response = chat_agent.process_query(q)
    print("-" * 50)
    print(response['text'][:500] + "..." if len(response['text']) > 500 else response['text'])
    if response.get('chart'):
        print("[Chart generated]")
    print("-" * 50)

print("\n✅ Verification Complete")
