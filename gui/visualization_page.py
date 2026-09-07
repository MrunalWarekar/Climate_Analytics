from gui.base_page import BasePage
import tkinter as tk


class VisualizationPage(BasePage):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            app,
            "Visualization",
            "Explore climate data through interactive visualizations."
        )

        self.create_visualization_ui()

    def create_visualization_ui(self):

        card = self.create_card()

        card.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            card,
            text="Visualization Module",
            font=("Arial", 20, "bold"),
            bg=self.app.card_color,
            fg=self.app.text_color
        ).pack(
            pady=(150, 10)
        )

        tk.Label(
            card,
            text="Charts and graphs will be integrated here.",
            font=("Arial", 11),
            bg=self.app.card_color,
            fg=self.app.secondary_text
        ).pack()