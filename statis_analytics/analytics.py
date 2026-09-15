import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import os


class WeatherApp:

    def __init__(self, root):

        self.root = root
        self.root.title("India Weather Analysis Tool")
        self.root.geometry("1000x700")
        self.root.config(bg="#f0f4f8")

        self.df = None
        self.current_filename = ""

        self.selected_data = None
        self.statistics = None

        self.home_frame = None
        self.analysis_frame = None

        self.create_menu()
        self.show_home_page()


    # =========================================================
    # MENU
    # =========================================================

    def create_menu(self):
        menu_font = ("Arial", 30, "bold")
        self.root.option_add("*Menu.font", menu_font)

        
        menubar = tk.Menu(self.root)

        menubar.add_command(
            label="Home",
            command=self.show_home_page
            
        )

        menubar.add_command(
            label="Analysis",
            command=self.switch_to_analysis_page
        )

        menubar.add_separator()

        menubar.add_command(
            label="Exit",
            command=self.root.quit
        )

        self.root.config(menu=menubar)


    # =========================================================
    # CLEAR SCREEN
    # =========================================================

    def clear_screen(self):

        if self.home_frame and self.home_frame.winfo_exists():
            self.home_frame.destroy()
            self.home_frame = None

        if self.analysis_frame and self.analysis_frame.winfo_exists():
            self.analysis_frame.destroy()
            self.analysis_frame = None


    # =========================================================
    # HOME PAGE
    # =========================================================

    def show_home_page(self):

        self.clear_screen()

        self.home_frame = tk.Frame(
            self.root,
            bg="#f0f4f8"
        )

        self.home_frame.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            self.home_frame,
            text="Weather Analytics Dashboard",
            font=("Arial", 30, "bold"),
            bg="#f0f4f8",
            fg="#2b6cb0"
        ).pack(pady=(100, 25))


        tk.Label(
            self.home_frame,
            text="Statistical Analysis of Temperature Data",
            font=("Arial", 20),
            bg="#f0f4f8",
            fg="#4a5568"
        ).pack(pady=10)


        self.btn_upload = tk.Button(
            self.home_frame,
            text="Select & Upload Weather CSV File",
            font=("Arial", 20, "bold"),
            bg="#2b6cb0",
            fg="white",
            padx=20,
            pady=10,
            command=self.upload_file,
            cursor="hand2"
        )

        self.btn_upload.pack(pady=25)


        self.lbl_status = tk.Label(
            self.home_frame,
            font=("Arial", 15),
            bg="#f0f4f8",
            justify="center"
        )

        self.lbl_status.pack(pady=20)


        if self.df is not None:

            self.lbl_status.config(
                text=
                f"File Active: {self.current_filename}\n\n"
                f"Rows: {self.df.shape[0]}\n"
                f"Columns: {self.df.shape[1]}\n\n"
                "Click Analysis from the top menu.",
                fg="#38a169",
                font=("Arial", 11, "bold")
            )

        else:

            self.lbl_status.config(
                text="No dataset loaded.",
                fg="#718096"
            )


    # =========================================================
    # UPLOAD FILE
    # =========================================================

    def upload_file(self):

        file_path = filedialog.askopenfilename(
            title="Select Weather CSV File",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        try:

            # Read the FAO dataset
            temp_df = pd.read_csv(
                file_path,
                encoding="latin1"
            )


            # Check required columns
            required_columns = [
                "Area",
                "Months",
                "Element"
            ]

            for column in required_columns:

                if column not in temp_df.columns:

                    messagebox.showerror(
                        "Invalid Dataset",
                        f"Required column '{column}' is missing."
                    )

                    return


            # Convert year columns to numeric
            year_columns = [
                col for col in temp_df.columns
                if col.startswith("Y")
            ]

            for col in year_columns:

                temp_df[col] = pd.to_numeric(
                    temp_df[col],
                    errors="coerce"
                )


            self.df = temp_df

            self.current_filename = os.path.basename(
                file_path
            )


            self.lbl_status.config(
                text=
                f"File uploaded successfully!\n\n"
                f"File: {self.current_filename}\n"
                f"Rows: {self.df.shape[0]}\n"
                f"Columns: {self.df.shape[1]}\n\n"
                "Click Analysis from the top menu.",
                fg="#38a169",
                font=("Arial", 11, "bold")
            )


            print("\n================================")
            print("DATASET LOADED SUCCESSFULLY")
            print("================================")
            print("File:", self.current_filename)
            print("Rows:", self.df.shape[0])
            print("Columns:", self.df.shape[1])
            print("Years:", len(year_columns))


        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Unable to read the CSV file.\n\n{e}"
            )


    # =========================================================
    # ANALYSIS PAGE
    # =========================================================

    def switch_to_analysis_page(self):

        if self.df is None:

            self.show_home_page()

            messagebox.showwarning(
                "No Dataset",
                "Please upload a CSV file first."
            )

            return

        self.clear_screen()

        self.show_analysis_page()


    def show_analysis_page(self):

        self.analysis_frame = tk.Frame(
            self.root,
            bg="#f0f4f8"
        )

        self.analysis_frame.pack(
            fill="both",
            expand=True
        )


        # =====================================================
        # TITLE
        # =====================================================

        tk.Label(
            self.analysis_frame,
            text="Statistical Analysis",
            font=("Arial", 20, "bold"),
            bg="#f0f4f8",
            fg="#2b6cb0"
        ).pack(pady=15)


        # =====================================================
        # SELECTION FRAME
        # =====================================================

        selection_frame = tk.Frame(
            self.analysis_frame,
            bg="#f0f4f8"
        )

        selection_frame.pack(
            pady=10
        )


        # -----------------------------------------------------
        # AREA
        # -----------------------------------------------------

        tk.Label(
            selection_frame,
            text="Area:",
            font=("Arial", 11, "bold"),
            bg="#f0f4f8"
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5
        )


        areas = sorted(
            self.df["Area"].dropna().unique().tolist()
        )


        self.area_dropdown = ttk.Combobox(
            selection_frame,
            values=areas,
            state="readonly",
            width=22
        )

        self.area_dropdown.grid(
            row=0,
            column=1,
            padx=5
        )


        if areas:
            self.area_dropdown.current(0)


        # -----------------------------------------------------
        # ELEMENT
        # -----------------------------------------------------

        tk.Label(
            selection_frame,
            text="Element:",
            font=("Arial", 11, "bold"),
            bg="#f0f4f8"
        ).grid(
            row=0,
            column=2,
            padx=5
        )


        elements = sorted(
            self.df["Element"].dropna().unique().tolist()
        )


        self.element_dropdown = ttk.Combobox(
            selection_frame,
            values=elements,
            state="readonly",
            width=22
        )

        self.element_dropdown.grid(
            row=0,
            column=3,
            padx=5
        )


        if elements:
            self.element_dropdown.current(0)


        # -----------------------------------------------------
        # PERIOD
        # -----------------------------------------------------

        tk.Label(
            selection_frame,
            text="Period:",
            font=("Arial", 11, "bold"),
            bg="#f0f4f8"
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=10
        )


        periods = [
            "Annual",
            "Jan-Feb",
            "Mar-May",
            "Jun-Sep",
            "Oct-Dec"
        ]


        self.period_dropdown = ttk.Combobox(
            selection_frame,
            values=periods,
            state="readonly",
            width=22
        )

        self.period_dropdown.grid(
            row=1,
            column=1,
            padx=5
        )

        self.period_dropdown.current(0)


        # -----------------------------------------------------
        # CALCULATE BUTTON
        # -----------------------------------------------------

        tk.Button(
            selection_frame,
            text="Calculate Statistics",
            font=("Arial", 10, "bold"),
            bg="#2b6cb0",
            fg="white",
            padx=15,
            pady=6,
            command=self.calculate_statistics
        ).grid(
            row=1,
            column=3,
            padx=10
        )


        # =====================================================
        # STATISTICS TABLE
        # =====================================================

        table_frame = tk.LabelFrame(
            self.analysis_frame,
            text=" Statistical Results ",
            font=("Arial", 12, "bold"),
            bg="white"
        )

        table_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )


        columns = (
            "Statistic",
            "Value"
        )


        self.stats_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=9
        )


        self.stats_table.heading(
            "Statistic",
            text="Statistic"
        )

        self.stats_table.heading(
            "Value",
            text="Value"
        )


        self.stats_table.column(
            "Statistic",
            width=250
        )

        self.stats_table.column(
            "Value",
            width=300
        )


        self.stats_table.pack(
            padx=20,
            pady=15
        )


        # =====================================================
        # CORRELATION MATRIX
        # =====================================================

        corr_frame = tk.LabelFrame(
            self.analysis_frame,
            text=" Correlation Matrix ",
            font=("Arial", 12, "bold"),
            bg="white"
        )

        corr_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )


        self.corr_text = tk.Text(
            corr_frame,
            height=8,
            font=("Courier New", 9)
        )

        self.corr_text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )


        # =====================================================
        # BUTTONS
        # =====================================================

        button_frame = tk.Frame(
            self.analysis_frame,
            bg="#f0f4f8"
        )

        button_frame.pack(
            pady=10
        )


        tk.Button(
            button_frame,
            text="Export Statistics as CSV",
            font=("Arial", 10, "bold"),
            bg="#38a169",
            fg="white",
            padx=15,
            pady=7,
            command=self.export_statistics
        ).grid(
            row=0,
            column=0,
            padx=10
        )


        tk.Button(
            button_frame,
            text="Generate Summary",
            font=("Arial", 10, "bold"),
            bg="#805ad5",
            fg="white",
            padx=15,
            pady=7,
            command=self.generate_summary
        ).grid(
            row=0,
            column=1,
            padx=10
        )


        # Automatically calculate
        self.calculate_statistics()


    # =========================================================
    # GET DATA FOR SELECTED PERIOD
    # =========================================================

    def get_period_data(self):

        area = self.area_dropdown.get()

        element = self.element_dropdown.get()

        period = self.period_dropdown.get()


        # Filter Area and Element
        filtered = self.df[
            (self.df["Area"] == area) &
            (self.df["Element"] == element)
        ]


        if filtered.empty:

            return pd.Series(dtype=float)


        # Year columns
        year_columns = [
            col for col in self.df.columns
            if col.startswith("Y")
        ]


        # -----------------------------------------------------
        # ANNUAL
        # -----------------------------------------------------

        if period == "Annual":

            rows = filtered[
                filtered["Months"] == "Meteorological year"
            ]

            if rows.empty:

                return pd.Series(dtype=float)

            values = rows[year_columns].iloc[0]

            return pd.to_numeric(
                values,
                errors="coerce"
            ).dropna()


        # -----------------------------------------------------
        # JAN-FEB
        # -----------------------------------------------------

        elif period == "Jan-Feb":

            months = [
                "January",
                "February"
            ]


        # -----------------------------------------------------
        # MAR-MAY
        # -----------------------------------------------------

        elif period == "Mar-May":

            months = [
                "March",
                "April",
                "May"
            ]


        # -----------------------------------------------------
        # JUN-SEP
        # -----------------------------------------------------

        elif period == "Jun-Sep":

            months = [
                "June",
                "July",
                "August",
                "September"
            ]


        # -----------------------------------------------------
        # OCT-DEC
        # -----------------------------------------------------

        elif period == "Oct-Dec":

            months = [
                "October",
                "November",
                "December"
            ]


        # Calculate average for each year
        rows = filtered[
            filtered["Months"].isin(months)
        ]


        if rows.empty:

            return pd.Series(dtype=float)


        data = rows[year_columns].apply(
            pd.to_numeric,
            errors="coerce"
        )


        yearly_values = data.mean(
            axis=0
        )


        return yearly_values.dropna()


    # =========================================================
    # CALCULATE STATISTICS
    # =========================================================

    def calculate_statistics(self):

        try:

            data = self.get_period_data()


            if data.empty:

                messagebox.showwarning(
                    "No Data",
                    "No data found for the selected options."
                )

                return


            # Mean
            mean_val = data.mean()


            # Median
            median_val = data.median()


            # Mode
            mode_values = data.mode()

            if mode_values.empty:

                mode_val = "No mode"

            else:

                mode_val = ", ".join(
                    f"{x:.2f}"
                    for x in mode_values
                )


            # Variance
            variance_val = data.var()


            # Standard deviation
            std_val = data.std()


            # Minimum
            min_val = data.min()


            # Maximum
            max_val = data.max()


            # Range
            range_val = max_val - min_val


            # Store statistics
            self.statistics = {
                "Mean": mean_val,
                "Median": median_val,
                "Mode": mode_val,
                "Variance": variance_val,
                "Standard Deviation": std_val,
                "Minimum": min_val,
                "Maximum": max_val,
                "Range": range_val
            }


            self.selected_data = data


            # Clear old table
            for item in self.stats_table.get_children():

                self.stats_table.delete(item)


            # Insert statistics
            for name, value in self.statistics.items():

                if isinstance(value, str):

                    display_value = value

                else:

                    display_value = f"{value:.4f}"


                self.stats_table.insert(
                    "",
                    "end",
                    values=(
                        name,
                        display_value
                    )
                )


            # Calculate correlation matrix
            self.calculate_correlation()


            print("\n================================")
            print("STATISTICAL RESULTS")
            print("================================")

            print(
                "Area:",
                self.area_dropdown.get()
            )

            print(
                "Element:",
                self.element_dropdown.get()
            )

            print(
                "Period:",
                self.period_dropdown.get()
            )

            print(self.statistics)


        except Exception as e:

            messagebox.showerror(
                "Calculation Error",
                str(e)
            )


    # =========================================================
    # CORRELATION MATRIX
    # =========================================================

    def calculate_correlation(self):

        self.corr_text.delete(
            "1.0",
            tk.END
        )


        area = self.area_dropdown.get()

        element = self.element_dropdown.get()


        filtered = self.df[
            (self.df["Area"] == area) &
            (self.df["Element"] == element)
        ]


        year_columns = [
            col for col in self.df.columns
            if col.startswith("Y")
        ]


        # Create period values for every year
        period_data = {}


        periods = {
            "Annual": ["Meteorological year"],

            "Jan-Feb": [
                "January",
                "February"
            ],

            "Mar-May": [
                "March",
                "April",
                "May"
            ],

            "Jun-Sep": [
                "June",
                "July",
                "August",
                "September"
            ],

            "Oct-Dec": [
                "October",
                "November",
                "December"
            ]
        }


        for period_name, months in periods.items():

            rows = filtered[
                filtered["Months"].isin(months)
            ]


            if rows.empty:
                continue


            values = rows[year_columns].apply(
                pd.to_numeric,
                errors="coerce"
            )


            period_data[period_name] = values.mean(
                axis=0
            )


        if len(period_data) < 2:

            self.corr_text.insert(
                tk.END,
                "Not enough periods available to calculate correlation."
            )

            return


        # DataFrame
        corr_df = pd.DataFrame(
            period_data
        )


        correlation_matrix = corr_df.corr()


        self.corr_text.insert(
            tk.END,
            correlation_matrix.round(3).to_string()
        )


    # =========================================================
    # EXPORT STATISTICS AS CSV
    # =========================================================

    def export_statistics(self):

        if self.statistics is None:

            messagebox.showwarning(
                "No Results",
                "Please calculate statistics first."
            )

            return


        file_path = filedialog.asksaveasfilename(
            title="Save Statistics",
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ]
        )


        if not file_path:
            return


        export_df = pd.DataFrame({
            "Statistic": list(
                self.statistics.keys()
            ),
            "Value": list(
                self.statistics.values()
            )
        })


        export_df.to_csv(
            file_path,
            index=False
        )


        messagebox.showinfo(
            "Export Successful",
            "Statistics have been exported successfully."
        )


    # =========================================================
    # AUTO SUMMARY
    # =========================================================

    def generate_summary(self):

        if self.statistics is None:

            messagebox.showwarning(
                "No Results",
                "Please calculate statistics first."
            )

            return


        area = self.area_dropdown.get()

        element = self.element_dropdown.get()

        period = self.period_dropdown.get()


        mean_val = self.statistics["Mean"]

        median_val = self.statistics["Median"]

        min_val = self.statistics["Minimum"]

        max_val = self.statistics["Maximum"]

        range_val = self.statistics["Range"]

        std_val = self.statistics["Standard Deviation"]


        # Determine basic distribution
        if mean_val > median_val:

            distribution = (
                "The data is slightly positively skewed "
                "because the mean is higher than the median."
            )

        elif mean_val < median_val:

            distribution = (
                "The data is slightly negatively skewed "
                "because the mean is lower than the median."
            )

        else:

            distribution = (
                "The mean and median are approximately equal, "
                "suggesting a relatively balanced distribution."
            )


        summary = f"""
STATISTICAL SUMMARY
==============================

Area:
{area}

Element:
{element}

Period:
{period}

Number of observations:
{len(self.selected_data)}

Mean:
{mean_val:.2f}

Median:
{median_val:.2f}

Minimum:
{min_val:.2f}

Maximum:
{max_val:.2f}

Range:
{range_val:.2f}

Standard Deviation:
{std_val:.2f}

Interpretation:
{distribution}

Overall:
The selected weather data has an average value of
{mean_val:.2f} °C.

The values range from {min_val:.2f} to
{max_val:.2f} °C.

The standard deviation is {std_val:.2f},
which indicates the amount of variation in the
temperature values over the selected years.
"""


        # New summary window
        summary_window = tk.Toplevel(
            self.root
        )

        summary_window.title(
            "Automatic Statistical Summary"
        )

        summary_window.geometry(
            "650x550"
        )


        text = tk.Text(
            summary_window,
            font=("Arial", 11),
            wrap="word"
        )

        text.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


        text.insert(
            tk.END,
            summary
        )


        text.config(
            state="disabled"
        )


# =============================================================
# MAIN PROGRAM
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = WeatherApp(root)

    root.mainloop()

