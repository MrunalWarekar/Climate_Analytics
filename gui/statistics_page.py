from gui.base_page import BasePage


class StatisticsPage(BasePage):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            app,
            "Statistics",
            "Statistical analysis of the selected climate data."
        )

        self.create_statistics_ui()

    def create_statistics_ui(self):

        card = self.create_card()
        card.pack(
            fill="both",
            expand=True
        )