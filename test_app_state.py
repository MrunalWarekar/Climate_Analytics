from utils.app_state import AppState


state = AppState()

print("Initial state:")
print("Dataset loaded:", state.dataset_loaded)
print("Analysis ready:", state.analysis_ready)
print("Statistics ready:", state.statistics_ready)
print("Trends ready:", state.trends_ready)
print("Visualization ready:", state.visualization_ready)
print("ML ready:", state.ml_ready)


print("\nMarking analysis as ready...")

state.analysis_ready = True

print("Analysis ready:", state.analysis_ready)


print("\nResetting analysis...")

state.reset_analysis()

print("Analysis ready:", state.analysis_ready)
print("Statistics ready:", state.statistics_ready)
print("Trends ready:", state.trends_ready)
print("Visualization ready:", state.visualization_ready)
print("ML ready:", state.ml_ready)