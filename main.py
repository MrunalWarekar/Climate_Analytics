import tkinter as tk
from pathlib import Path
from tkinter import ttk

from utils.data_manager import DataManager
from utils.app_state import AppState

from gui.statistics_page import StatisticsPage
from gui.trends_page import TrendsPage
from gui.visualization_page import VisualizationPage
from gui.ml_page import MLPage
from gui.dashboard_page import DashboardPage


class ClimateAnalyticsApp(tk.Tk):

    def __init__(self):
        super().__init__()

        # ==========================================================
        # SHARED DATA
        # ==========================================================

        self.data_manager = DataManager()
        self.app_state = AppState()

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

        self.sidebar_top = tk.Frame(
            self.sidebar,
            bg=self.sidebar_color
        )

        self.sidebar_top.pack(
            fill="x",
            pady=(20, 15)
        )

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

        button.bind(
            "<Enter>",
            lambda event: self.nav_hover(button, True)
        )

        button.bind(
            "<Leave>",
            lambda event: self.nav_hover(button, False)
        )

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

            self.app_title.pack_forget()

            for icon, name, command in self.nav_items:

                button = self.nav_buttons[name]

                button.config(
                    text=icon,
                    anchor="center",
                    padx=0
                )

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

            self.app_title.pack(
                side="left",
                padx=5
            )

            for icon, name, command in self.nav_items:

                button = self.nav_buttons[name]

                button.config(
                    text=f"{icon}   {name}",
                    anchor="w",
                    padx=15
                )

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

            return [
                button.cget("text")
            ]

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

        welcome_frame = tk.Frame(
            self.content,
            bg=self.bg_color
        )

        welcome_frame.pack(
            fill="x",
            pady=(25, 20)
        )

        tk.Label(
            welcome_frame,
            text="Climate Analytics System",
            font=("Arial", 28, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(
            anchor="w"
        )

        tk.Label(
            welcome_frame,
            text=(
                "Explore climate data through statistical analysis, "
                "trend analysis, visualizations and machine learning."
            ),
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.secondary_text
        ).pack(
            anchor="w",
            pady=(8, 0)
        )

        card = tk.Frame(
            self.content,
            bg=self.card_color,
            highlightbackground=self.border_color,
            highlightthickness=1
        )

        card.pack(
            fill="both",
            expand=True,
            pady=(20, 0)
        )

        tk.Label(
            card,
            text="Getting Started",
            font=("Arial", 19, "bold"),
            bg=self.card_color,
            fg=self.text_color
        ).pack(
            anchor="w",
            padx=30,
            pady=(30, 20)
        )

        steps = [
            ("1", "Dataset", "Upload and configure the climate dataset."),
            ("2", "Statistics", "Perform statistical analysis on the selected data."),
            ("3", "Trend Analysis", "Study historical climate trends and patterns."),
            ("4", "Visualization", "Explore the data through graphical visualizations."),
            ("5", "Machine Learning", "Generate predictions using trained models."),
        ]

        for number, title, description in steps:

            row = tk.Frame(
                card,
                bg=self.card_color
            )

            row.pack(
                fill="x",
                padx=30,
                pady=8
            )

            tk.Label(
                row,
                text=number,
                font=("Arial", 12, "bold"),
                bg=self.sidebar_active,
                fg="white",
                width=3,
                height=1
            ).pack(
                side="left",
                padx=(0, 15)
            )

            text_frame = tk.Frame(
                row,
                bg=self.card_color
            )

            text_frame.pack(
                side="left",
                fill="x",
                expand=True
            )

            tk.Label(
                text_frame,
                text=title,
                font=("Arial", 12, "bold"),
                bg=self.card_color,
                fg=self.text_color
            ).pack(
                anchor="w"
            )

            tk.Label(
                text_frame,
                text=description,
                font=("Arial", 10),
                bg=self.card_color,
                fg=self.secondary_text
            ).pack(
                anchor="w",
                pady=(2, 0)
            )

        tk.Button(
            card,
            text="Go to Dataset",
            command=self.show_dataset,
            font=("Arial", 11, "bold"),
            bg=self.sidebar_active,
            fg="white",
            activebackground=self.sidebar_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(
            anchor="w",
            padx=30,
            pady=(25, 30)
        )

    # ==============================================================
    # DATASET
    # ==============================================================

    def show_dataset(self):

        self.show_placeholder(
            "Dataset",
            "Upload and configure the climate dataset for analysis."
        )

    # ==============================================================
    # STATISTICS
    # ==============================================================

    def show_statistics(self):

        self.clear_page()
        self.set_page_title("Statistics")

        page = StatisticsPage(
            self.content,
            self
        )

        page.pack(
            fill="both",
            expand=True
        )

    # ==============================================================
    # TREND ANALYSIS
    # ==============================================================

    def show_trends(self):

        self.clear_page()
        self.set_page_title("Trend Analysis")

        page = TrendsPage(
            self.content,
            self
        )

        page.pack(
            fill="both",
            expand=True
        )

    # ==============================================================
    # VISUALIZATION
    # ==============================================================

    def show_visualization(self):

        self.clear_page()
        self.set_page_title("Visualization")

        if not self.data_manager.has_dataset():
            dataset_path = Path(__file__).with_name(
                "Environment_Temperature_change_E_All_Data_NOFLAG.csv"
            )
            self.data_manager.load_dataset(str(dataset_path))

        if not self.data_manager.has_processed_data():
            area = self.data_manager.selected_country or "India"
            element = self.data_manager.selected_element or "Temperature change"
            self.data_manager.create_analytical_dataset(
                area=area,
                element=element
            )

        # IMPORTANT:
        # VisualizationPage expects a DataManager object,
        # not the ClimateAnalyticsApp object.

        page = VisualizationPage(
            self.content,
            self.data_manager
        )

        page.pack(
            fill="both",
            expand=True
        )

    # ==============================================================
    # MACHINE LEARNING
    # ==============================================================

    def show_ml(self):

        self.clear_page()
        self.set_page_title("Machine Learning")

        page = MLPage(
            self.content,
            self
        )

        page.pack(
            fill="both",
            expand=True
        )

    # ==============================================================
    # DASHBOARD
    # ==============================================================

    def show_dashboard(self):

        self.clear_page()
        self.set_page_title("Dashboard")

        page = DashboardPage(
            self.content,
            self
        )

        page.pack(
            fill="both",
            expand=True
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

    # ==============================================================
    # STATUS
    # ==============================================================

    def update_status(self, message):

        self.status_bar.config(
            text=message
        )

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

    # ==============================================================
    # DATASET STATE
    # ==============================================================

    def dataset_is_loaded(self):

        return self.data_manager.has_dataset()

    def analysis_is_ready(self):

        return self.data_manager.has_processed_data()

    def reset_analysis_state(self):

        self.data_manager.clear_results()
        self.app_state.reset_analysis()

    # ==============================================================
    # NAVIGATION
    # ==============================================================

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
    # ANALYSIS STATE
    # ==============================================================

    def mark_analysis_ready(self):

        self.app_state.analysis_ready = True

        self.update_status(
            "Analysis data is ready."
        )

    def mark_result_ready(self, analysis_type):

        if analysis_type == "statistics":

            self.app_state.statistics_ready = True

        elif analysis_type == "trends":

            self.app_state.trends_ready = True

        elif analysis_type == "visualization":

            self.app_state.visualization_ready = True

        elif analysis_type == "ml":

            self.app_state.ml_ready = True


# ==============================================================
# RUN APPLICATION
# ==============================================================

if __name__ == "__main__":

    app = ClimateAnalyticsApp()

    app.mainloop()