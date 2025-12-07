"""
Verification script for LLM Council Agent.
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.council_agent import CouncilAgent

print("Initializing Council Agent...")
try:
    council = CouncilAgent()
    
    # Test query
    query = "Which marketing channel should I prioritize for maximum ROI?"
    
    print(f"\nQuery: {query}\n")
    result = council.ask(query)
    
    print("\n=== FINAL RESPONSE ===")
    print(result['final_response'][:500] + "..." if len(result['final_response']) > 500 else result['final_response'])
    
    print("\n✅ Council verification complete!")
    
except Exception as e:
    print(f"❌ Council verification failed: {e}")
