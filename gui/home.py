import tkinter as tk


class HomePage(tk.Frame):

    def __init__(self, parent, app):

        super().__init__(parent)

        self.app = app

        title = tk.Label(
            self,
            text="Climate Analytics System",
            font=("Arial", 26, "bold")
        )

        title.pack(
            pady=50
        )