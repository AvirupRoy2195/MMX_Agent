from src.agents.orchestrator import Orchestrator

print("Initializing Orchestrator...")
orch = Orchestrator()

print("\n=== Running Basic Analysis ===")
basic_results = orch.run_analysis()
print("Basic Model R²:", basic_results['model_results']['r2'])

print("\n=== Running Advanced Analysis ===")
advanced_results = orch.run_advanced_analysis()

print("\nModel Comparison:")
for model_name, results in advanced_results['model_comparison'].items():
    print(f"  {model_name}: R² = {results['r2']:.3f}, RMSE = {results['rmse']:.0f}")

print("\nROI Decomposition (first 3 channels):")
roi_decomp = advanced_results['roi_decomposition']
for i, (channel, values) in enumerate(list(roi_decomp.items())[:3]):
    print(f"  {channel}:")
    print(f"    Immediate: {values['immediate']:.2f}")
    print(f"    Long-term: {values['longterm']:.2f}")
    print(f"    Total: {values['total']:.2f}")

print("\nBrand Analysis:")
print(f"  NPS Mean: {advanced_results['nps_stats']['mean']:.1f}")
print(f"  NPS-Sales Correlation: {advanced_results['nps_correlation']:.2f}")
if advanced_results['brand_impact']:
    print(f"  Brand Impact Coefficient: {advanced_results['brand_impact']:.2f}")

print("\n✅ Advanced MMM verification complete!")
