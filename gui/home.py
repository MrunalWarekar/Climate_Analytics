import tkinter as tk


class HomePage(tk.Frame):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            bg=app.bg_color
        )

        self.app = app

        self.create_home_ui()

    # ==========================================================
    # HOME PAGE
    # ==========================================================

    def create_home_ui(self):

        # Main container
        container = tk.Frame(
            self,
            bg=self.app.bg_color
        )

        container.pack(
            fill="both",
            expand=True,
            padx=45,
            pady=40
        )

        # ------------------------------------------------------
        # TITLE
        # ------------------------------------------------------

        tk.Label(
            container,
            text="Climate Analytics",
            font=("Arial", 28, "bold"),
            bg=self.app.bg_color,
            fg=self.app.text_color
        ).pack(
            anchor="w"
        )

        tk.Label(
            container,
            text="Climate data analysis and prediction system",
            font=("Arial", 12),
            bg=self.app.bg_color,
            fg=self.app.secondary_text
        ).pack(
            anchor="w",
            pady=(8, 35)
        )

        # ------------------------------------------------------
        # WELCOME
        # ------------------------------------------------------

        welcome = tk.Label(
            container,
            text="Welcome!",
            font=("Arial", 20, "bold"),
            bg=self.app.bg_color,
            fg=self.app.text_color
        )

        welcome.pack(
            anchor="w"
        )

        tk.Label(
            container,
            text=(
                "Explore historical climate data, analyse temperature "
                "patterns, identify trends and generate predictions."
            ),
            font=("Arial", 11),
            bg=self.app.bg_color,
            fg=self.app.secondary_text,
            justify="left"
        ).pack(
            anchor="w",
            pady=(8, 30)
        )

        # ------------------------------------------------------
        # HOW TO USE
        # ------------------------------------------------------

        tk.Label(
            container,
            text="Getting Started",
            font=("Arial", 17, "bold"),
            bg=self.app.bg_color,
            fg=self.app.text_color
        ).pack(
            anchor="w",
            pady=(5, 15)
        )

        steps = [
            "1. Upload a climate dataset from the Dataset section.",
            "2. Select the country, measurement, month and year range.",
            "3. Prepare the selected data for analysis.",
            "4. Explore statistics, trends, visualizations and predictions."
        ]

        for step in steps:

            tk.Label(
                container,
                text=step,
                font=("Arial", 11),
                bg=self.app.bg_color,
                fg=self.app.secondary_text,
                anchor="w"
            ).pack(
                anchor="w",
                pady=5
            )

        # ------------------------------------------------------
        # STATUS MESSAGE
        # ------------------------------------------------------

        tk.Label(
            container,
            text="Use the navigation menu on the left to begin.",
            font=("Arial", 11, "italic"),
            bg=self.app.bg_color,
            fg=self.app.secondary_text
        ).pack(
            anchor="w",
            pady=(35, 0)
        )