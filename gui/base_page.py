import tkinter as tk


class BasePage(tk.Frame):

    def __init__(self, parent, app, title, subtitle=""):
        super().__init__(
            parent,
            bg=app.bg_color
        )

        self.app = app
        self.title_text = title

        self.create_header(title, subtitle)
        self.create_body()

    # ==========================================================
    # PAGE HEADER
    # ==========================================================

    def create_header(self, title, subtitle):

        header = tk.Frame(
            self,
            bg=self.app.bg_color
        )

        header.pack(
            fill="x",
            pady=(5, 20)
        )

        tk.Label(
            header,
            text=title,
            font=("Arial", 21, "bold"),
            bg=self.app.bg_color,
            fg=self.app.text_color
        ).pack(
            anchor="w"
        )

        if subtitle:

            tk.Label(
                header,
                text=subtitle,
                font=("Arial", 10),
                bg=self.app.bg_color,
                fg=self.app.secondary_text
            ).pack(
                anchor="w",
                pady=(5, 0)
            )

    # ==========================================================
    # BODY
    # ==========================================================

    def create_body(self):

        self.body = tk.Frame(
            self,
            bg=self.app.bg_color
        )

        self.body.pack(
            fill="both",
            expand=True
        )

    # ==========================================================
    # CARD
    # ==========================================================

    def create_card(self, parent=None):

        if parent is None:
            parent = self.body

        card = tk.Frame(
            parent,
            bg=self.app.card_color,
            highlightbackground=self.app.border_color,
            highlightthickness=1
        )

        return card

    # ==========================================================
    # STATUS
    # ==========================================================

    def set_status(self, message):

        self.app.update_status(message)