import tkinter as tk
from tkinter import ttk

from utils.data_manager import DataManager

from gui.home import HomePage
from gui.dataset_page import DatasetPage
from gui.statistics_page import StatisticsPage
from gui.trends_page import TrendsPage
from gui.visualization_page import VisualizationPage
from gui.ml_page import MLPage
from gui.dashboard_page import DashboardPage


class MainWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Climate Analytics System")
        self.root.geometry("1500x850")
        self.root.minsize(1100, 650)

        # -----------------------------------------
        # CENTRAL DATA MANAGER
        # -----------------------------------------
        self.data_manager = DataManager()

        # -----------------------------------------
        # APPLICATION STATE
        # -----------------------------------------
        self.current_page = None
        self.pages = {}

        # -----------------------------------------
        # MAIN LAYOUT
        # -----------------------------------------
        self.create_layout()

        # -----------------------------------------
        # CREATE PAGES
        # -----------------------------------------
        self.create_pages()

        # -----------------------------------------
        # SHOW HOME
        # -----------------------------------------
        self.show_page("Home")

    # ==================================================
    # MAIN LAYOUT
    # ==================================================

    def create_layout(self):

        self.sidebar_visible = True

        # Sidebar
        self.sidebar = tk.Frame(
            self.root,
            width=230
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # Main content area
        self.content_frame = tk.Frame(
            self.root
        )

        self.content_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        # Menu button
        self.menu_button = tk.Button(
            self.sidebar,
            text="☰",
            command=self.toggle_sidebar,
            font=("Arial", 16),
            relief="flat"
        )

        self.menu_button.pack(
            anchor="w",
            padx=15,
            pady=15
        )

        # Application title
        self.title_label = tk.Label(
            self.sidebar,
            text="Climate Analytics",
            font=("Arial", 18, "bold")
        )

        self.title_label.pack(
            pady=(5, 25)
        )

        # Navigation buttons
        self.nav_buttons = {}

        navigation = [
            ("Home", "Home"),
            ("Dataset", "Dataset"),
            ("Statistics", "Statistics"),
            ("Trends", "Trends"),
            ("Visualization", "Visualization"),
            ("Machine Learning", "ML"),
            ("Dashboard", "Dashboard")
        ]

        for text, page_name in navigation:

            button = tk.Button(
                self.sidebar,
                text=text,
                anchor="w",
                command=lambda name=page_name:
                self.show_page(name),
                font=("Arial", 11),
                relief="flat",
                padx=20
            )

            button.pack(
                fill="x",
                padx=10,
                pady=3,
                ipady=8
            )

            self.nav_buttons[page_name] = button

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            anchor="w",
            relief="sunken"
        )

        self.status_bar.pack(
            side="bottom",
            fill="x"
        )

    # ==================================================
    # CREATE PAGES
    # ==================================================

    def create_pages(self):

        page_classes = {
            "Home": HomePage,
            "Dataset": DatasetPage,
            "Statistics": StatisticsPage,
            "Trends": TrendsPage,
            "Visualization": VisualizationPage,
            "ML": MLPage,
            "Dashboard": DashboardPage
        }

        for name, page_class in page_classes.items():

            page = page_class(
                self.content_frame,
                self
            )

            self.pages[name] = page

    # ==================================================
    # PAGE NAVIGATION
    # ==================================================

    def show_page(self, page_name):

        if self.current_page is not None:
            self.current_page.pack_forget()

        page = self.pages[page_name]

        page.pack(
            fill="both",
            expand=True
        )

        self.current_page = page

        self.status_bar.config(
            text=f"Current page: {page_name}"
        )

    # ==================================================
    # SIDEBAR COLLAPSE
    # ==================================================

    def toggle_sidebar(self):

        if self.sidebar_visible:

            self.sidebar.pack_forget()

            self.sidebar_visible = False

        else:

            self.sidebar.pack(
                side="left",
                fill="y",
                before=self.content_frame
            )

            self.sidebar_visible = True