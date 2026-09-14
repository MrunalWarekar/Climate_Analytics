from gui.base_page import BasePage
import tkinter as tk


class DashboardPage(BasePage):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            app,
            "Dashboard",
            "Consolidated overview of climate analysis results."
        )

        self.create_dashboard_ui()

    def create_dashboard_ui(self):

        card = self.create_card()

        card.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            card,
            text="Dashboard",
            font=("Arial", 20, "bold"),
            bg=self.app.card_color,
            fg=self.app.text_color
        ).pack(
            pady=(150, 10)
        )

        tk.Label(
            card,
            text="Combined analysis results will appear here.",
            font=("Arial", 11),
            bg=self.app.card_color,
            fg=self.app.secondary_text
        ).pack()