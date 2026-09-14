from gui.base_page import BasePage
import tkinter as tk


class MLPage(BasePage):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            app,
            "Machine Learning",
            "Train models and generate temperature predictions."
        )

        self.create_ml_ui()

    def create_ml_ui(self):

        card = self.create_card()

        card.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            card,
            text="Machine Learning Module",
            font=("Arial", 20, "bold"),
            bg=self.app.card_color,
            fg=self.app.text_color
        ).pack(
            pady=(150, 10)
        )

        tk.Label(
            card,
            text="ML model training and prediction will be integrated here.",
            font=("Arial", 11),
            bg=self.app.card_color,
            fg=self.app.secondary_text
        ).pack()