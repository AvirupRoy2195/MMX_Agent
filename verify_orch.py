from src.agents.orchestrator import Orchestrator

print("Initializing Orchestrator...")
orch = Orchestrator()

print("Running Analysis...")
results = orch.run_analysis()

if "error" in results:
    print("Error:", results['error'])
else:
    print("Analysis Complete!")
    print("KPIs:", results['kpis'])
    print("Feedback:", results['feedback'])
    print("ROI Keys:", list(results['roi'].keys()))
    print("Category Data Shape:", results['categories'].shape if results['categories'] is not None else "None")
