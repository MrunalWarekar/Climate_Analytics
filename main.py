import tkinter as tk
from tkinter import ttk

from utils.data_manager import DataManager


class ClimateAnalyticsApp(tk.Tk):

    def __init__(self):
        super().__init__()

        # ==========================================================
        # SHARED DATA MANAGER
        # ==========================================================

        self.data_manager = DataManager()

        # ==========================================================
        # APPLICATION STATE
        # ==========================================================

        self.dataset_loaded = False
        self.analysis_ready = False
        self.statistics_ready = False
        self.trends_ready = False
        self.visualization_ready = False
        self.ml_ready = False

        # ==========================================================
        # WINDOW
        # ==========================================================

        self.title("Climate Analytics System")
        self.geometry("1500x850")
        self.minsize(1100, 650)

        # ==========================================================
        # COLORS
        # ==========================================================

        self.bg_color = "#F5F7FA"
        self.sidebar_color = "#172033"
        self.sidebar_hover = "#263449"
        self.sidebar_active = "#334967"

        self.card_color = "#FFFFFF"
        self.text_color = "#172033"
        self.secondary_text = "#64748B"
        self.border_color = "#E2E8F0"

        self.configure(bg=self.bg_color)

        # ==========================================================
        # SIDEBAR STATE
        # ==========================================================

        self.sidebar_expanded = True
        self.expanded_width = 250
        self.collapsed_width = 72

        self.current_page = "Home"

        # ==========================================================
        # STYLE
        # ==========================================================

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # ==========================================================
        # CREATE APPLICATION
        # ==========================================================

        self.create_layout()
        self.create_sidebar()
        self.create_main_area()

        self.show_home()

    # ==============================================================
    # MAIN LAYOUT
    # ==============================================================

    def create_layout(self):

        self.sidebar = tk.Frame(
            self,
            bg=self.sidebar_color,
            width=self.expanded_width
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(
            self,
            bg=self.bg_color
        )

        self.main_area.pack(
            side="right",
            fill="both",
            expand=True
        )

    # ==============================================================
    # SIDEBAR
    # ==============================================================

    def create_sidebar(self):

        # ---------------- TOP ----------------

        self.sidebar_top = tk.Frame(
            self.sidebar,
            bg=self.sidebar_color
        )

        self.sidebar_top.pack(
            fill="x",
            pady=(20, 15)
        )

        # Collapse button

        self.toggle_button = tk.Button(
            self.sidebar_top,
            text="☰",
            command=self.toggle_sidebar,
            font=("Arial", 16, "bold"),
            fg="white",
            bg=self.sidebar_color,
            activebackground=self.sidebar_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        self.toggle_button.pack(
            side="left",
            padx=15
        )

        # Application title

        self.app_title = tk.Label(
            self.sidebar_top,
            text="CLIMATE\nANALYTICS",
            font=("Arial", 15, "bold"),
            fg="white",
            bg=self.sidebar_color,
            justify="left"
        )

        self.app_title.pack(
            side="left",
            padx=5
        )

        # ---------------- NAVIGATION ----------------

        self.nav_frame = tk.Frame(
            self.sidebar,
            bg=self.sidebar_color
        )

        self.nav_frame.pack(
            fill="both",
            expand=True,
            padx=8
        )

        self.nav_items = [
            ("⌂", "Home", self.show_home),
            ("▣", "Dataset", self.show_dataset),
            ("▤", "Statistics", self.show_statistics),
            ("↗", "Trend Analysis", self.show_trends),
            ("◈", "Visualization", self.show_visualization),
            ("⚙", "Machine Learning", self.show_ml),
            ("▦", "Dashboard", self.show_dashboard),
        ]

        self.nav_buttons = {}

        for icon, name, command in self.nav_items:

            button = self.create_nav_button(
                icon,
                name,
                command
            )

            self.nav_buttons[name] = button

        # ---------------- BOTTOM ----------------

        self.bottom_frame = tk.Frame(
            self.sidebar,
            bg=self.sidebar_color
        )

        self.bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=8,
            pady=15
        )

        self.create_bottom_button(
            "⚙",
            "Settings",
            self.show_settings
        )

        self.create_bottom_button(
            "?",
            "Help & About",
            self.show_help
        )

    # ==============================================================
    # NAVIGATION BUTTON
    # ==============================================================

    def create_nav_button(self, icon, name, command):

        frame = tk.Frame(
            self.nav_frame,
            bg=self.sidebar_color
        )

        frame.pack(
            fill="x",
            pady=2
        )

        button = tk.Button(
            frame,
            text=f"{icon}   {name}",
            command=command,
            font=("Arial", 11),
            fg="white",
            bg=self.sidebar_color,
            activebackground=self.sidebar_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            anchor="w",
            padx=15,
            pady=12,
            cursor="hand2"
        )

        button.pack(
            fill="x"
        )

        # Hover effect

        button.bind(
            "<Enter>",
            lambda event: self.nav_hover(button, True)
        )

        button.bind(
            "<Leave>",
            lambda event: self.nav_hover(button, False)
        )

        # Tooltip

        self.create_tooltip(button, name)

        return button

    # ==============================================================
    # BOTTOM BUTTONS
    # ==============================================================

    def create_bottom_button(self, icon, name, command):

        button = tk.Button(
            self.bottom_frame,
            text=f"{icon}   {name}",
            command=command,
            font=("Arial", 11),
            fg="white",
            bg=self.sidebar_color,
            activebackground=self.sidebar_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            anchor="w",
            padx=15,
            pady=10,
            cursor="hand2"
        )

        button.pack(
            fill="x",
            pady=2
        )

        button.bind(
            "<Enter>",
            lambda event: self.nav_hover(button, True)
        )

        button.bind(
            "<Leave>",
            lambda event: self.nav_hover(button, False)
        )

        self.create_tooltip(button, name)

    # ==============================================================
    # SIDEBAR COLLAPSE
    # ==============================================================

    def toggle_sidebar(self):

        if self.sidebar_expanded:

            self.sidebar.config(
                width=self.collapsed_width
            )

            self.sidebar_expanded = False

            # Hide title
            self.app_title.pack_forget()

            # Change navigation buttons to icons
            for icon, name, command in self.nav_items:

                button = self.nav_buttons[name]

                button.config(
                    text=icon,
                    anchor="center",
                    padx=0
                )

            # Bottom buttons
            for widget in self.bottom_frame.winfo_children():

                widget.config(
                    text=widget.cget("text").split("   ")[0],
                    anchor="center",
                    padx=0
                )

        else:

            self.sidebar.config(
                width=self.expanded_width
            )

            self.sidebar_expanded = True

            # Show title again
            self.app_title.pack(
                side="left",
                padx=5
            )

            # Restore navigation buttons
            for icon, name, command in self.nav_items:

                button = self.nav_buttons[name]

                button.config(
                    text=f"{icon}   {name}",
                    anchor="w",
                    padx=15
                )

            # Restore bottom buttons
            bottom_names = [
                ("⚙", "Settings"),
                ("?", "Help & About")
            ]

            for widget, (icon, name) in zip(
                self.bottom_frame.winfo_children(),
                bottom_names
            ):

                widget.config(
                    text=f"{icon}   {name}",
                    anchor="w",
                    padx=15
                )

    # ==============================================================
    # HOVER
    # ==============================================================

    def nav_hover(self, button, entering):

        if button.cget("text") not in self.get_active_button_text():

            if entering:
                button.config(
                    bg=self.sidebar_hover
                )
            else:
                button.config(
                    bg=self.sidebar_active
                    if self.is_active_button(button)
                    else self.sidebar_color
                )

    # ==============================================================
    # ACTIVE PAGE
    # ==============================================================

    def set_active_page(self, page_name):

        self.current_page = page_name

        for name, button in self.nav_buttons.items():

            if name == page_name:

                button.config(
                    bg=self.sidebar_active
                )

            else:

                button.config(
                    bg=self.sidebar_color
                )

    def is_active_button(self, button):

        return button == self.nav_buttons.get(
            self.current_page
        )

    def get_active_button_text(self):

        button = self.nav_buttons.get(
            self.current_page
        )

        if button:
            return [button.cget("text")]

        return []

    # ==============================================================
    # TOOLTIP
    # ==============================================================

    def create_tooltip(self, widget, text):

        tooltip = tk.Label(
            self,
            text=text,
            bg="#111827",
            fg="white",
            font=("Arial", 9),
            padx=8,
            pady=4
        )

        tooltip.place_forget()

        def show_tooltip(event):

            if not self.sidebar_expanded:

                x = self.sidebar.winfo_width() + 8
                y = widget.winfo_rooty() - self.winfo_rooty()

                tooltip.place(
                    x=x,
                    y=y
                )

        def hide_tooltip(event):

            tooltip.place_forget()

        widget.bind(
            "<Enter>",
            show_tooltip,
            add="+"
        )

        widget.bind(
            "<Leave>",
            hide_tooltip,
            add="+"
        )

    # ==============================================================
    # MAIN AREA
    # ==============================================================

    def create_main_area(self):

        # Header

        self.header = tk.Frame(
            self.main_area,
            bg=self.bg_color,
            height=85
        )

        self.header.pack(
            fill="x",
            padx=40,
            pady=(25, 0)
        )

        self.header.pack_propagate(False)

        self.page_title = tk.Label(
            self.header,
            text="Home",
            font=("Arial", 25, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )

        self.page_title.pack(
            side="left",
            anchor="center"
        )

        self.content = tk.Frame(
            self.main_area,
            bg=self.bg_color
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=(5, 30)
        )

        # ==========================================================
        # STATUS BAR
        # ==========================================================

        self.status_bar = tk.Label(
            self.main_area,
            text="Ready",
            font=("Arial", 9),
            bg="#E2E8F0",
            fg=self.secondary_text,
            anchor="w",
            padx=15
        )

        self.status_bar.pack(
            side="bottom",
            fill="x"
        )

    # ==============================================================
    # PAGE MANAGEMENT
    # ==============================================================

    def clear_page(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def set_page_title(self, title):

        self.page_title.config(
            text=title
        )

        self.set_active_page(title)

    # ==============================================================
    # HOME PAGE
    # ==============================================================

    def show_home(self):

        self.clear_page()
        self.set_page_title("Home")

        # Welcome section

        welcome_frame = tk.Frame(
            self.content,
            bg=self.bg_color
        )

        welcome_frame.pack(
            fill="x",
            pady=(5, 20)
        )

        welcome = tk.Label(
            welcome_frame,
            text="Climate Analytics Dashboard",
            font=("Arial", 21, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )

        welcome.pack(
            anchor="w"
        )

        subtitle = tk.Label(
            welcome_frame,
            text=(
                "Analyze historical temperature data, identify climate trends "
                "and explore machine learning predictions."
            ),
            font=("Arial", 11),
            bg=self.bg_color,
            fg=self.secondary_text
        )

        subtitle.pack(
            anchor="w",
            pady=(5, 0)
        )

        # ==========================================================
        # STATISTIC CARDS
        # ==========================================================

        cards_frame = tk.Frame(
            self.content,
            bg=self.bg_color
        )

        cards_frame.pack(
            fill="x"
        )

        cards = [
            ("🌡", "Average Temperature", "-- °C"),
            ("↑", "Highest Temperature", "-- °C"),
            ("↓", "Lowest Temperature", "-- °C"),
            ("📅", "Years Analysed", "--"),
        ]

        for icon, title, value in cards:

            self.create_stat_card(
                cards_frame,
                icon,
                title,
                value
            )

        # ==========================================================
        # LOWER SECTION
        # ==========================================================

        lower_frame = tk.Frame(
            self.content,
            bg=self.bg_color
        )

        lower_frame.pack(
            fill="both",
            expand=True,
            pady=(25, 0)
        )

        # Quick actions

        quick_frame = tk.Frame(
            lower_frame,
            bg=self.card_color,
            highlightbackground=self.border_color,
            highlightthickness=1
        )

        quick_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        tk.Label(
            quick_frame,
            text="Quick Actions",
            font=("Arial", 16, "bold"),
            bg=self.card_color,
            fg=self.text_color
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 15)
        )

        actions = [
            ("Upload Dataset", self.show_dataset),
            ("View Statistics", self.show_statistics),
            ("Analyze Trends", self.show_trends),
            ("Run Machine Learning", self.show_ml),
        ]

        for text, command in actions:

            button = tk.Button(
                quick_frame,
                text=text,
                command=command,
                font=("Arial", 10),
                bg="#F1F5F9",
                fg=self.text_color,
                activebackground="#E2E8F0",
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=15,
                pady=10
            )

            button.pack(
                fill="x",
                padx=25,
                pady=4
            )

        # Recent activity

        activity_frame = tk.Frame(
            lower_frame,
            bg=self.card_color,
            highlightbackground=self.border_color,
            highlightthickness=1
        )

        activity_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(12, 0)
        )

        tk.Label(
            activity_frame,
            text="Recent Activity",
            font=("Arial", 16, "bold"),
            bg=self.card_color,
            fg=self.text_color
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 15)
        )

        activities = [
            "Application started",
            "No dataset loaded",
            "Ready for analysis"
        ]

        for activity in activities:

            tk.Label(
                activity_frame,
                text="•  " + activity,
                font=("Arial", 10),
                bg=self.card_color,
                fg=self.secondary_text
            ).pack(
                anchor="w",
                padx=25,
                pady=7
            )

    # ==============================================================
    # STAT CARD
    # ==============================================================

    def create_stat_card(
        self,
        parent,
        icon,
        title,
        value
    ):

        card = tk.Frame(
            parent,
            bg=self.card_color,
            highlightbackground=self.border_color,
            highlightthickness=1
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        tk.Label(
            card,
            text=icon,
            font=("Arial", 22),
            bg=self.card_color,
            fg=self.text_color
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        tk.Label(
            card,
            text=title,
            font=("Arial", 10),
            bg=self.card_color,
            fg=self.secondary_text
        ).pack(
            anchor="w",
            padx=20
        )

        tk.Label(
            card,
            text=value,
            font=("Arial", 18, "bold"),
            bg=self.card_color,
            fg=self.text_color
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 15)
        )

    # ==============================================================
    # PLACEHOLDER PAGES
    # ==============================================================

    def show_dataset(self):

        self.show_placeholder(
            "Dataset",
            "Upload and manage climate datasets."
        )

    def show_statistics(self):

        self.show_placeholder(
            "Statistics",
            "Statistical analysis will appear here."
        )

    def show_trends(self):

        self.show_placeholder(
            "Trend Analysis",
            "Temperature trend analysis will appear here."
        )

    def show_visualization(self):

        self.show_placeholder(
            "Visualization",
            "Climate data visualizations will appear here."
        )

    def show_ml(self):

        self.show_placeholder(
            "Machine Learning",
            "Machine learning and temperature prediction will appear here."
        )

    def show_dashboard(self):

        self.show_placeholder(
            "Dashboard",
            "Detailed climate analytics dashboard will appear here."
        )

    # ==============================================================
    # SETTINGS
    # ==============================================================

    def show_settings(self):

        self.show_placeholder(
            "Settings",
            "Application settings will appear here."
        )

    # ==============================================================
    # HELP
    # ==============================================================

    def show_help(self):

        self.show_placeholder(
            "Help & About",
            "Help, instructions and application information."
        )

    # ==============================================================
    # GENERIC PLACEHOLDER
    # ==============================================================

    def show_placeholder(self, title, description):

        self.clear_page()
        self.set_page_title(title)

        frame = tk.Frame(
            self.content,
            bg=self.card_color,
            highlightbackground=self.border_color,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            frame,
            text=title,
            font=("Arial", 24, "bold"),
            bg=self.card_color,
            fg=self.text_color
        ).pack(
            pady=(150, 10)
        )

        tk.Label(
            frame,
            text=description,
            font=("Arial", 12),
            bg=self.card_color,
            fg=self.secondary_text
        ).pack()

    def update_status(self, message):
        """Update application status message."""

        self.status_bar.config(
            text=message
        )

    def dataset_is_loaded(self):
        """Check whether a master dataset has been loaded."""
        return self.data_manager.has_dataset()


    def analysis_is_ready(self):
        """Check whether processed analytical data exists."""
        return self.data_manager.has_processed_data()


    def reset_analysis_state(self):
        """Reset analysis results after a new dataset/selection."""

        self.data_manager.clear_results()

        self.statistics_ready = False
        self.trends_ready = False
        self.visualization_ready = False
        self.ml_ready = False

    def get_home_statistics(self):

        df = self.data_manager.processed_df

        if df is None or df.empty:
            return {
                "average": "--",
                "highest": "--",
                "lowest": "--",
                "years": "--"
            }

        return {
            "average": f"{df['VALUE'].mean():.2f}",
            "highest": f"{df['VALUE'].max():.2f}",
            "lowest": f"{df['VALUE'].min():.2f}",
            "years": df["YEAR"].nunique()
        }

    def handle_error(self, message, title="Error"):
        from tkinter import messagebox
        messagebox.showerror(
            title,
            message
        )

        self.update_status(
            f"Error: {message}"
        )

    def handle_success(self, message):
        self.update_status(
            message
        )


    def go_to(self, page_name):

        navigation = {
            "Home": self.show_home,
            "Dataset": self.show_dataset,
            "Statistics": self.show_statistics,
            "Trend Analysis": self.show_trends,
            "Visualization": self.show_visualization,
            "Machine Learning": self.show_ml,
            "Dashboard": self.show_dashboard,
        }

        if page_name in navigation:
            navigation[page_name]()

    

# ==============================================================
# RUN APPLICATION
# ==============================================================

if __name__ == "__main__":

    app = ClimateAnalyticsApp()

    app.mainloop()