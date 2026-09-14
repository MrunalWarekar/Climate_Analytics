class AppState:

    def __init__(self):

        self.dataset_loaded = False
        self.analysis_ready = False

        self.statistics_ready = False
        self.trends_ready = False
        self.visualization_ready = False
        self.ml_ready = False

    def reset_analysis(self):

        self.analysis_ready = False
        self.statistics_ready = False
        self.trends_ready = False
        self.visualization_ready = False
        self.ml_ready = False

    def mark_result_ready(self, analysis_type):

        if analysis_type == "statistics":
            self.statistics_ready = True

        elif analysis_type == "trends":
            self.trends_ready = True

        elif analysis_type == "visualization":
            self.visualization_ready = True

        elif analysis_type == "ml":
            self.ml_ready = True