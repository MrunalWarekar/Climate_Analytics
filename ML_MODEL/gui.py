import os
import re
import shutil
import tkinter as tk

from tkinter import (
    ttk,
    messagebox,
    filedialog
)

from PIL import Image, ImageTk


# =========================================================
# IMPORT MONTHLY FUNCTIONS
# =========================================================

from monthly_training import (
    get_available_countries,
    get_available_months,
    run_monthly_analysis
)


# =========================================================
# IMPORT PREDICTION FUNCTIONS
# =========================================================

from prediction import (
    predict_yearly_temperature,
    predict_monthly_temperature
)


# =========================================================
# IMPORT YEARLY ANALYSIS
# =========================================================

from train_model import (
    run_yearly_analysis
)


# =========================================================
# PATH
# =========================================================

BASE_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_FILE = os.path.join(
    BASE_FOLDER,
    "DataSet.csv"
)


# =========================================================
# THEME COLORS
# =========================================================

# Reference theme:
# Olive/gold top bar
# Muted teal buttons
# Light gray page background
# White cards
# Dark navy text
# Soft gray borders

TOPBAR = "#8b7d47"

TEAL = "#579a91"
TEAL_DARK = "#46857d"
TEAL_LIGHT = "#e4f0ee"

BG = "#f3f5f5"

CARD = "#ffffff"

TEXT = "#17272d"
MUTED = "#718087"

BORDER = "#dce2e2"

INPUT_BG = "#ffffff"

RESULT_BG = "#fafbfb"

WHITE = "#ffffff"

CLEAR_BG = "#eeeeee"
CLEAR_ACTIVE = "#dddddd"


# =========================================================
# APPLICATION
# =========================================================

class ClimateApp:

    def __init__(
        self,
        root
    ):

        self.root = root

        self.root.title(
            "Climate Analytics System"
        )

        self.root.geometry(
            "1150x850"
        )

        self.root.minsize(
            900,
            650
        )

        self.root.configure(
            bg=BG
        )

        self.graph_image = None

        self.setup_styles()

        self.load_dataset_options()

        self.create_interface()


    # =====================================================
    # STYLES
    # =====================================================

    def setup_styles(self):

        style = ttk.Style()

        try:

            style.theme_use(
                "clam"
            )

        except:

            pass


        # -------------------------------------------------
        # Combobox
        # -------------------------------------------------

        style.configure(
            "TCombobox",
            padding=8,
            font=(
                "Segoe UI",
                10
            ),
            fieldbackground=INPUT_BG,
            background=INPUT_BG,
            foreground=TEXT
        )


        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", INPUT_BG)
            ],
            foreground=[
                ("readonly", TEXT)
            ]
        )


        # -------------------------------------------------
        # Entry
        # -------------------------------------------------

        style.configure(
            "TEntry",
            padding=8,
            font=(
                "Segoe UI",
                10
            ),
            fieldbackground=INPUT_BG,
            foreground=TEXT
        )


        # -------------------------------------------------
        # Scrollbar
        # -------------------------------------------------

        style.configure(
            "Vertical.TScrollbar",
            width=10,
            background="#d3dada",
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=TEXT
        )


    # =====================================================
    # LOAD DATA OPTIONS
    # =====================================================

    def load_dataset_options(self):

        try:

            self.countries = (
                get_available_countries(
                    DATASET_FILE
                )
            )

            self.months = (
                get_available_months(
                    DATASET_FILE
                )
            )

        except Exception as e:

            messagebox.showerror(
                "Dataset Error",
                str(e)
            )

            self.countries = []

            self.months = []


    # =====================================================
    # CREATE INTERFACE
    # =====================================================

    def create_interface(self):

        # =================================================
        # TOP BAR
        # =================================================

        topbar = tk.Frame(
            self.root,
            bg=TOPBAR,
            height=30
        )

        topbar.pack(
            fill="x"
        )

        topbar.pack_propagate(
            False
        )


        tk.Label(
            topbar,
            text="Climate Analytics System",
            bg=TOPBAR,
            fg=WHITE,
            font=(
                "Segoe UI",
                9
            ),
            anchor="w"
        ).pack(
            side="left",
            padx=10
        )


        # =================================================
        # SCROLLABLE MAIN AREA
        # =================================================

        outer = tk.Frame(
            self.root,
            bg=BG
        )

        outer.pack(
            fill="both",
            expand=True
        )


        # -------------------------------------------------
        # Canvas
        # -------------------------------------------------

        self.canvas = tk.Canvas(
            outer,
            bg=BG,
            highlightthickness=0
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )


        # -------------------------------------------------
        # Main scrollbar
        # -------------------------------------------------

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=self.canvas.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )


        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )


        # -------------------------------------------------
        # Main content frame
        # -------------------------------------------------

        main = tk.Frame(
            self.canvas,
            bg=BG
        )


        self.canvas_window = (
            self.canvas.create_window(
                (0, 0),
                window=main,
                anchor="nw"
            )
        )


        main.bind(
            "<Configure>",
            self.update_scroll_region
        )


        self.canvas.bind(
            "<Configure>",
            self.resize_canvas_content
        )


        self.canvas.bind_all(
            "<MouseWheel>",
            self.mouse_wheel
        )


        # =================================================
        # PAGE HEADER
        # =================================================

        page_header = tk.Frame(
            main,
            bg=BG
        )

        page_header.pack(
            fill="x",
            padx=55,
            pady=(48, 25)
        )


        title_row = tk.Frame(
            page_header,
            bg=BG
        )

        title_row.pack(
            anchor="w"
        )


        tk.Label(
            title_row,
            text="Machine Learning",
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                28,
                "bold"
            )
        ).pack(
            side="left"
        )


        # -------------------------------------------------
        # Teal vertical accent
        # -------------------------------------------------

        tk.Frame(
            title_row,
            bg=TEAL,
            width=5,
            height=35
        ).pack(
            side="left",
            padx=(10, 0)
        )


        tk.Label(
            page_header,
            text="Train, evaluate and predict temperature trends using machine learning.",
            bg=BG,
            fg=MUTED,
            font=(
                "Segoe UI",
                11
            )
        ).pack(
            anchor="w",
            pady=(7, 0)
        )


        # =================================================
        # CONFIGURATION CARD
        # =================================================

        config_card = tk.Frame(
            main,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        config_card.pack(
            fill="x",
            padx=45,
            pady=(0, 15)
        )


        tk.Label(
            config_card,
            text="Analysis Settings",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                17,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=28,
            pady=(23, 18)
        )


        # =================================================
        # ANALYSIS TYPE
        # =================================================

        tk.Label(
            config_card,
            text="Analysis Type",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=28
        )


        self.mode = ttk.Combobox(
            config_card,
            values=[
                "Yearly",
                "Monthly"
            ],
            state="readonly"
        )


        self.mode.set(
            "Yearly"
        )


        self.mode.grid(
            row=2,
            column=0,
            padx=28,
            pady=(5, 23),
            sticky="ew"
        )


        self.mode.bind(
            "<<ComboboxSelected>>",
            self.mode_changed
        )


        # =================================================
        # COUNTRY
        # =================================================

        tk.Label(
            config_card,
            text="Country",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=28
        )


        self.country = ttk.Combobox(
            config_card,
            values=self.countries,
            state="readonly"
        )


        if self.countries:

            self.country.set(
                self.countries[0]
            )


        self.country.grid(
            row=2,
            column=1,
            padx=28,
            pady=(5, 23),
            sticky="ew"
        )


        # =================================================
        # MONTH
        # =================================================

        self.month_label = tk.Label(
            config_card,
            text="Month",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        )


        self.month_label.grid(
            row=1,
            column=2,
            sticky="w",
            padx=28
        )


        self.month = ttk.Combobox(
            config_card,
            values=self.months,
            state="readonly"
        )


        if self.months:

            self.month.set(
                self.months[0]
            )


        self.month.grid(
            row=2,
            column=2,
            padx=28,
            pady=(5, 23),
            sticky="ew"
        )


        # =================================================
        # RUN ANALYSIS BUTTON
        # =================================================

        self.run_button = tk.Button(
            config_card,
            text="Run Analysis",
            command=self.run_analysis,
            bg=TEAL,
            fg=WHITE,
            activebackground=TEAL_DARK,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            padx=25,
            pady=11
        )


        self.run_button.grid(
            row=2,
            column=3,
            padx=28,
            pady=(5, 23)
        )


        config_card.grid_columnconfigure(
            0,
            weight=1
        )

        config_card.grid_columnconfigure(
            1,
            weight=1
        )

        config_card.grid_columnconfigure(
            2,
            weight=1
        )


        # =================================================
        # PREDICTION CARD
        # =================================================

        prediction_card = tk.Frame(
            main,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )


        prediction_card.pack(
            fill="x",
            padx=45,
            pady=(0, 15)
        )


        tk.Label(
            prediction_card,
            text="Future Temperature Prediction",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                17,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=28,
            pady=(23, 18)
        )


        # =================================================
        # PREDICT QUESTION
        # =================================================

        tk.Label(
            prediction_card,
            text="Predict temperature?",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        ).grid(
            row=1,
            column=0,
            padx=28,
            sticky="w"
        )


        self.predict_choice = ttk.Combobox(
            prediction_card,
            values=[
                "No",
                "Yes"
            ],
            state="readonly",
            width=12
        )


        self.predict_choice.set(
            "No"
        )


        self.predict_choice.grid(
            row=2,
            column=0,
            padx=28,
            pady=(5, 23),
            sticky="w"
        )


        self.predict_choice.bind(
            "<<ComboboxSelected>>",
            self.prediction_choice_changed
        )


        # =================================================
        # YEAR
        # =================================================

        self.year_label = tk.Label(
            prediction_card,
            text="Prediction Year",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        )


        self.year_label.grid(
            row=1,
            column=1,
            padx=28,
            sticky="w"
        )


        self.prediction_year = ttk.Entry(
            prediction_card,
            width=15
        )


        self.prediction_year.grid(
            row=2,
            column=1,
            padx=28,
            pady=(5, 23),
            sticky="w"
        )


        # =================================================
        # PREDICT BUTTON
        # =================================================

        self.predict_button = tk.Button(
            prediction_card,
            text="Predict",
            command=self.run_prediction,
            bg=TEAL,
            fg=WHITE,
            activebackground=TEAL_DARK,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            padx=25,
            pady=10
        )


        self.predict_button.grid(
            row=2,
            column=2,
            padx=28,
            pady=(5, 23)
        )


        # =================================================
        # RESULTS CARD
        # =================================================

        result_card = tk.Frame(
            main,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )


        result_card.pack(
            fill="x",
            padx=45,
            pady=(0, 30)
        )


        # =================================================
        # RESULTS TITLE
        # =================================================

        tk.Label(
            result_card,
            text="Results",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                17,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=28,
            pady=(23, 12)
        )


        # =================================================
        # RESULT TEXT + SCROLLBAR
        # =================================================

        result_text_frame = tk.Frame(
            result_card,
            bg=RESULT_BG,
            highlightbackground=BORDER,
            highlightthickness=1
        )


        result_text_frame.pack(
            fill="x",
            padx=28,
            pady=(0, 18)
        )


        self.result_text = tk.Text(
            result_text_frame,
            height=10,
            bg=RESULT_BG,
            fg=TEXT,
            relief="flat",
            font=(
                "Consolas",
                11
            ),
            padx=15,
            pady=15,
            wrap="none"
        )


        self.result_text.pack(
            side="left",
            fill="both",
            expand=True
        )


        result_scrollbar = ttk.Scrollbar(
            result_text_frame,
            orient="vertical",
            command=self.result_text.yview
        )


        result_scrollbar.pack(
            side="right",
            fill="y"
        )


        self.result_text.configure(
            yscrollcommand=result_scrollbar.set
        )


        # =================================================
        # GRAPH TITLE
        # =================================================

        tk.Label(
            result_card,
            text="Actual vs Predicted Temperature",
            bg=CARD,
            fg=TEXT,
            font=(
                "Segoe UI",
                13,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=28,
            pady=(2, 10)
        )


        # =================================================
        # GRAPH FRAME
        # =================================================

        self.graph_frame = tk.Frame(
            result_card,
            bg=RESULT_BG,
            height=400,
            highlightbackground=BORDER,
            highlightthickness=1
        )


        self.graph_frame.pack(
            fill="x",
            padx=28,
            pady=(0, 18)
        )


        self.graph_frame.pack_propagate(
            False
        )


        # =================================================
        # GRAPH LABEL
        # =================================================

        self.graph_label = tk.Label(
            self.graph_frame,
            bg=RESULT_BG,
            text="Run an analysis to display the graph.",
            fg=MUTED,
            font=(
                "Segoe UI",
                11
            )
        )


        self.graph_label.pack(
            fill="both",
            expand=True
        )


        # =================================================
        # BUTTONS
        # =================================================

        buttons = tk.Frame(
            result_card,
            bg=CARD
        )


        buttons.pack(
            fill="x",
            padx=28,
            pady=(0, 23)
        )


        # -------------------------------------------------
        # Download
        # -------------------------------------------------

        tk.Button(
            buttons,
            text="Download All Graphs",
            command=self.download_graphs,
            bg=TEAL,
            fg=WHITE,
            activebackground=TEAL_DARK,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            padx=18,
            pady=9
        ).pack(
            side="left",
            padx=(0, 10)
        )


        # -------------------------------------------------
        # Clear
        # -------------------------------------------------

        tk.Button(
            buttons,
            text="Clear Results",
            command=self.clear_results,
            bg=CLEAR_BG,
            fg=TEXT,
            activebackground=CLEAR_ACTIVE,
            activeforeground=TEXT,
            relief="flat",
            cursor="hand2",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            padx=18,
            pady=9
        ).pack(
            side="left"
        )


        # =================================================
        # INITIAL STATE
        # =================================================

        self.update_month_visibility()

        self.update_prediction_visibility()


    # =====================================================
    # SCROLL REGION
    # =====================================================

    def update_scroll_region(
        self,
        event=None
    ):

        self.canvas.configure(
            scrollregion=self.canvas.bbox(
                "all"
            )
        )


    # =====================================================
    # RESIZE CANVAS CONTENT
    # =====================================================

    def resize_canvas_content(
        self,
        event
    ):

        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )


    # =====================================================
    # MOUSE WHEEL
    # =====================================================

    def mouse_wheel(
        self,
        event
    ):

        try:

            self.canvas.yview_scroll(
                int(
                    -1 *
                    (event.delta / 120)
                ),
                "units"
            )

        except:

            pass


    # =====================================================
    # MODE CHANGED
    # =====================================================

    def mode_changed(
        self,
        event=None
    ):

        self.update_month_visibility()


    # =====================================================
    # MONTH VISIBILITY
    # =====================================================

    def update_month_visibility(self):

        if self.mode.get() == "Monthly":

            self.month_label.grid()

            self.month.grid()

        else:

            self.month_label.grid_remove()

            self.month.grid_remove()


    # =====================================================
    # PREDICTION CHANGED
    # =====================================================

    def prediction_choice_changed(
        self,
        event=None
    ):

        self.update_prediction_visibility()


    # =====================================================
    # PREDICTION VISIBILITY
    # =====================================================

    def update_prediction_visibility(self):

        if self.predict_choice.get() == "Yes":

            self.year_label.grid()

            self.prediction_year.grid()

            self.predict_button.grid()

        else:

            self.year_label.grid_remove()

            self.prediction_year.grid_remove()

            self.predict_button.grid_remove()


    # =====================================================
    # RUN ANALYSIS
    # =====================================================

    def run_analysis(self):

        country = self.country.get()

        mode = self.mode.get()


        if not country:

            messagebox.showwarning(
                "Missing Country",
                "Please select a country."
            )

            return


        try:

            self.result_text.delete(
                "1.0",
                tk.END
            )


            self.graph_label.configure(
                image="",
                text="Running analysis..."
            )


            self.graph_image = None


            self.root.update_idletasks()


            # ---------------------------------------------
            # YEARLY
            # ---------------------------------------------

            if mode == "Yearly":

                result = run_yearly_analysis(
                    country,
                    DATASET_FILE
                )


            # ---------------------------------------------
            # MONTHLY
            # ---------------------------------------------

            else:

                selected_month = (
                    self.month.get()
                )


                if not selected_month:

                    messagebox.showwarning(
                        "Missing Month",
                        "Please select a month."
                    )

                    return


                result = run_monthly_analysis(
                    country,
                    DATASET_FILE,
                    selected_month
                )


            # ---------------------------------------------
            # Display result
            # ---------------------------------------------

            self.display_result(
                result,
                mode
            )


            # ---------------------------------------------
            # Display graph
            # ---------------------------------------------

            self.display_graph(
                result.get(
                    "graph"
                )
            )


            # ---------------------------------------------
            # Scroll to results
            # ---------------------------------------------

            self.root.after(
                100,
                self.scroll_to_results
            )


        except Exception as e:

            self.graph_label.configure(
                image="",
                text="Graph could not be displayed."
            )


            messagebox.showerror(
                "Analysis Error",
                str(e)
            )


    # =====================================================
    # SCROLL TO RESULTS
    # =====================================================

    def scroll_to_results(self):

        self.canvas.yview_moveto(
            1.0
        )


    # =====================================================
    # DISPLAY RESULT
    # =====================================================

    def display_result(
        self,
        result,
        mode
    ):

        self.result_text.delete(
            "1.0",
            tk.END
        )


        self.result_text.insert(
            tk.END,
            f"Country    : "
            f"{result.get('country', '-')}\n"
        )


        self.result_text.insert(
            tk.END,
            f"Model Used : "
            f"{result.get('model', '-')}\n"
        )


        if mode == "Monthly":

            self.result_text.insert(
                tk.END,
                f"Month      : "
                f"{result.get('month', '-')}\n"
            )


        self.result_text.insert(
            tk.END,
            "\n"
        )


        self.result_text.insert(
            tk.END,
            f"R²         : "
            f"{result.get('r2', 0):.4f}\n"
        )


        self.result_text.insert(
            tk.END,
            f"MAE        : "
            f"{result.get('mae', 0):.4f}\n"
        )


        self.result_text.insert(
            tk.END,
            f"MSE        : "
            f"{result.get('mse', 0):.4f}\n"
        )


        self.result_text.insert(
            tk.END,
            f"RMSE       : "
            f"{result.get('rmse', 0):.4f}\n"
        )


        self.result_text.insert(
            tk.END,
            "\n"
        )


        self.result_text.insert(
            tk.END,
            "✓ Analysis completed successfully.\n"
        )


        self.result_text.insert(
            tk.END,
            "✓ Graphs are ready.\n"
        )


    # =====================================================
    # DISPLAY GRAPH
    # =====================================================

    def display_graph(
        self,
        graph_path
    ):

        if not graph_path:

            self.graph_label.configure(
                image="",
                text="No graph was generated."
            )

            return


        if not os.path.exists(
            graph_path
        ):

            self.graph_label.configure(
                image="",
                text="Graph file was not found."
            )

            return


        try:

            image = Image.open(
                graph_path
            )


            self.root.update_idletasks()


            available_width = max(
                self.graph_frame.winfo_width() - 20,
                500
            )


            available_height = max(
                self.graph_frame.winfo_height() - 20,
                350
            )


            image.thumbnail(
                (
                    available_width,
                    available_height
                ),
                Image.Resampling.LANCZOS
            )


            self.graph_image = (
                ImageTk.PhotoImage(
                    image
                )
            )


            self.graph_label.configure(
                image=self.graph_image,
                text=""
            )


        except Exception as e:

            self.graph_label.configure(
                image="",
                text="Graph display error."
            )

            print(
                "Graph display error:",
                e
            )


    # =====================================================
    # RUN PREDICTION
    # =====================================================

    def run_prediction(self):

        country = self.country.get()

        mode = self.mode.get()

        year_text = (
            self.prediction_year
            .get()
            .strip()
        )


        if not country:

            messagebox.showwarning(
                "Missing Country",
                "Please select a country."
            )

            return


        if not year_text:

            messagebox.showwarning(
                "Missing Year",
                "Please enter a prediction year."
            )

            return


        try:

            year = int(
                year_text
            )

        except:

            messagebox.showwarning(
                "Invalid Year",
                "Please enter a valid year."
            )

            return


        try:

            # =============================================
            # YEARLY
            # =============================================

            if mode == "Yearly":

                result = (
                    predict_yearly_temperature(
                        country,
                        year,
                        DATASET_FILE
                    )
                )


                prediction = result[
                    "prediction"
                ]


                text = (
                    "\nFuture Temperature Prediction\n"
                    "--------------------------------\n\n"
                    f"Country : {country}\n"
                    f"Year    : {year}\n"
                    f"Type    : Yearly\n\n"
                    f"Predicted Temperature Change : "
                    f"{prediction:.4f}\n"
                )


            # =============================================
            # MONTHLY
            # =============================================

            else:

                month = self.month.get()


                if not month:

                    messagebox.showwarning(
                        "Missing Month",
                        "Please select a month."
                    )

                    return


                result = (
                    predict_monthly_temperature(
                        country,
                        year,
                        month,
                        DATASET_FILE
                    )
                )


                prediction = result[
                    "prediction"
                ]


                text = (
                    "\nFuture Temperature Prediction\n"
                    "--------------------------------\n\n"
                    f"Country : {country}\n"
                    f"Year    : {year}\n"
                    f"Month   : {month}\n"
                    f"Type    : Monthly\n\n"
                    f"Predicted Temperature Change : "
                    f"{prediction:.4f}\n"
                )


            # =============================================
            # DISPLAY PREDICTION
            # =============================================

            self.result_text.insert(
                tk.END,
                text
            )


            self.result_text.insert(
                tk.END,
                "\n✓ Prediction completed successfully.\n"
            )


            self.result_text.see(
                tk.END
            )


            self.root.after(
                100,
                self.scroll_to_results
            )


        except Exception as e:

            messagebox.showerror(
                "Prediction Error",
                str(e)
            )


    # =====================================================
    # DOWNLOAD GRAPHS
    # =====================================================

    def download_graphs(self):

        country = self.country.get()


        if not country:

            messagebox.showwarning(
                "Missing Country",
                "Please select a country first."
            )

            return


        source_folders = []


        # -------------------------------------------------
        # Yearly
        # -------------------------------------------------

        yearly_folder = os.path.join(
            BASE_FOLDER,
            "results",
            "yearly",
            self.safe_name(
                country
            )
        )


        if os.path.exists(
            yearly_folder
        ):

            source_folders.append(
                yearly_folder
            )


        # -------------------------------------------------
        # Monthly
        # -------------------------------------------------

        monthly_folder = os.path.join(
            BASE_FOLDER,
            "results",
            "monthly",
            self.safe_name(
                country
            )
        )


        if os.path.exists(
            monthly_folder
        ):

            source_folders.append(
                monthly_folder
            )


        # -------------------------------------------------
        # Find images
        # -------------------------------------------------

        files = []


        for folder in source_folders:

            for filename in os.listdir(
                folder
            ):

                if filename.lower().endswith(
                    (
                        ".png",
                        ".jpg",
                        ".jpeg"
                    )
                ):

                    files.append(
                        os.path.join(
                            folder,
                            filename
                        )
                    )


        if not files:

            messagebox.showinfo(
                "No Graphs",
                "No generated graphs were found for this country."
            )

            return


        # -------------------------------------------------
        # Destination
        # -------------------------------------------------

        destination = filedialog.askdirectory(
            title="Select folder to save graphs"
        )


        if not destination:

            return


        # -------------------------------------------------
        # Copy
        # -------------------------------------------------

        copied = 0


        for source in files:

            filename = os.path.basename(
                source
            )


            target = os.path.join(
                destination,
                filename
            )


            shutil.copy2(
                source,
                target
            )


            copied += 1


        messagebox.showinfo(
            "Download Complete",
            f"{copied} graph(s) saved successfully."
        )


    # =====================================================
    # SAFE NAME
    # =====================================================

    def safe_name(
        self,
        text
    ):

        return re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            str(text).strip()
        ).strip("_").lower()


    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    def clear_results(self):

        self.result_text.delete(
            "1.0",
            tk.END
        )


        self.graph_label.configure(
            image="",
            text="Run an analysis to display the graph."
        )


        self.graph_image = None


        self.canvas.yview_moveto(
            0
        )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ClimateApp(
        root
    )

    root.mainloop()