import tkinter as tk


class StatisticsPage(tk.Frame):

    def __init__(self, parent, app):

        super().__init__(parent)

        self.app = app

        tk.Label(
            self,
            text="Statistics",
            font=("Arial", 24, "bold")
        ).pack(pady=50)