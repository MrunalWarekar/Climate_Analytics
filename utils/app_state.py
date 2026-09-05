class AppState:

    def __init__(self):

        # Dataset state
        self.dataset_loaded = False
        self.analysis_ready = False

        # Analysis state
        self.statistics_ready = False
        self.trends_ready = False
        self.visualization_ready = False
        self.ml_ready = False

    def reset_analysis(self):
        """Reset analysis-related states."""

        self.analysis_ready = False
        self.statistics_ready = False
        self.trends_ready = False
        self.visualization_ready = False
        self.ml_ready = False

    def reset_all(self):
        """Reset the complete application state."""

        self.dataset_loaded = False
        self.reset_analysis()