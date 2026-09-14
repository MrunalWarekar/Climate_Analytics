import pandas as pd


class DataManager:
    """Central data manager for the Climate Analytics System."""

    def __init__(self):
        # =========================================================
        # MASTER DATASET
        # =========================================================

        self.master_df = None

        # Currently selected/processed dataset
        self.processed_df = None

        # Dataset information
        self.file_path = None
        self.file_name = None
        self.metadata = {}

        # =========================================================
        # DYNAMICALLY DETECTED OPTIONS
        # =========================================================

        self.areas = []
        self.elements = []
        self.months = []
        self.year_columns = []

        # =========================================================
        # CURRENT USER SELECTION
        # =========================================================

        self.selected_country = None
        self.selected_element = None
        self.selected_month = None
        self.start_year = None
        self.end_year = None

        # =========================================================
        # RESULTS PRODUCED BY OTHER MODULES
        # =========================================================

        self.statistics_result = None
        self.trend_result = None
        self.ml_result = None
        self.prediction_result = None

    # =========================================================
    # LOAD DATASET
    # =========================================================

    def load_dataset(self, file_path):
        """Load the master CSV/Excel dataset."""

        if file_path.lower().endswith(".csv"):

            df = pd.read_csv(
                file_path,
                encoding="latin1"
            )

        elif file_path.lower().endswith((".xlsx", ".xls")):

            df = pd.read_excel(file_path)

        else:

            raise ValueError(
                "Unsupported file format. Please select a CSV or Excel file."
            )

        if df.empty:
            raise ValueError(
                "The selected dataset is empty."
            )

        # Store master dataset
        self.master_df = df

        self.file_path = file_path

        self.file_name = (
            file_path.replace("\\", "/").split("/")[-1]
        )

        # Detect dataset structure
        self.detect_dataset_structure()

        return self.master_df

    # =========================================================
    # VALIDATE DATASET
    # =========================================================

    def validate_dataset(self):
        """Validate whether the loaded dataset has the expected structure."""

        if self.master_df is None:
            raise ValueError(
                "No dataset has been loaded."
            )

        df = self.master_df

        required_columns = [
            "Area",
            "Element"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            return {
                "valid": False,
                "message": (
                    "Missing required columns: "
                    + ", ".join(missing_columns)
                )
            }

        if not self.year_columns:

            return {
                "valid": False,
                "message": "No valid year columns were detected."
            }

        return {
            "valid": True,
            "message": "Dataset structure is valid.",
            "rows": len(df),
            "columns": len(df.columns),
            "areas": len(self.areas),
            "elements": len(self.elements),
            "first_year": self.metadata.get("first_year"),
            "last_year": self.metadata.get("last_year")
        }

    # =========================================================
    # DETECT DATASET STRUCTURE
    # =========================================================

    def detect_dataset_structure(self):
        """Automatically detect important columns and values."""

        if self.master_df is None:
            return

        df = self.master_df

        # ---------------------------------------------------------
        # Detect Area / Country column
        # ---------------------------------------------------------

        if "Area" in df.columns:

            self.areas = sorted(
                df["Area"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

        # ---------------------------------------------------------
        # Detect measurement / Element
        # ---------------------------------------------------------

        if "Element" in df.columns:

            self.elements = sorted(
                df["Element"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

        # ---------------------------------------------------------
        # Detect months
        # ---------------------------------------------------------

        if "Months" in df.columns:

            self.months = sorted(
                df["Months"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

        # ---------------------------------------------------------
        # Detect year columns dynamically
        # ---------------------------------------------------------

        self.year_columns = []

        for column in df.columns:

            column_str = str(column).strip()

            # Format:
            # 1961

            if column_str.isdigit():

                year = int(column_str)

                if 1900 <= year <= 2100:

                    self.year_columns.append(
                        column
                    )

            # Format:
            # Y1961

            elif (
                column_str.startswith("Y")
                and column_str[1:].isdigit()
            ):

                year = int(
                    column_str[1:]
                )

                if 1900 <= year <= 2100:

                    self.year_columns.append(
                        column
                    )

        # ---------------------------------------------------------
        # Sort year columns chronologically
        # ---------------------------------------------------------

        self.year_columns.sort(
            key=lambda x: int(
                str(x).strip().replace("Y", "")
            )
        )

        # ---------------------------------------------------------
        # Update metadata
        # ---------------------------------------------------------

        self.update_metadata()

    # =========================================================
    # METADATA
    # =========================================================

    def update_metadata(self):
        """Store useful information about the master dataset."""

        if self.master_df is None:
            return

        # Convert detected year columns into integer years
        years = []

        for column in self.year_columns:

            column_str = str(column).strip()

            if column_str.startswith("Y"):

                years.append(
                    int(column_str[1:])
                )

            else:

                years.append(
                    int(column_str)
                )

        self.metadata = {

            "rows": len(self.master_df),

            "columns": len(
                self.master_df.columns
            ),

            "column_names": (
                self.master_df.columns.tolist()
            ),

            "areas": len(self.areas),

            "elements": self.elements,

            "months": self.months,

            "first_year": (
                min(years)
                if years
                else None
            ),

            "last_year": (
                max(years)
                if years
                else None
            ),
        }

    # =========================================================
    # CREATE ANALYTICAL DATASET
    # =========================================================

    def create_analytical_dataset(
        self,
        area,
        element="Temperature change",
        month=None,
        start_year=None,
        end_year=None
    ):
        """
        Convert the selected wide-format records into
        an analysis-ready YEAR + VALUE dataset.
        """

        if self.master_df is None:

            raise ValueError(
                "No dataset has been loaded."
            )

        df = self.master_df.copy()

        # ---------------------------------------------------------
        # 1. Filter by area
        # ---------------------------------------------------------

        if "Area" in df.columns:

            df = df[
                df["Area"]
                .astype(str)
                .str.strip()
                ==
                str(area).strip()
            ]

        # ---------------------------------------------------------
        # 2. Filter by measurement / Element
        # ---------------------------------------------------------

        if (
            "Element" in df.columns
            and element
        ):

            df = df[
                df["Element"]
                .astype(str)
                .str.strip()
                .str.lower()
                ==
                str(element)
                .strip()
                .lower()
            ]

        # ---------------------------------------------------------
        # 3. Filter by month / period
        # ---------------------------------------------------------

        if (
            "Months" in df.columns
            and month
        ):

            df = df[
                df["Months"]
                .astype(str)
                .str.strip()
                ==
                str(month).strip()
            ]

        if df.empty:

            raise ValueError(
                "No records found for the selected options."
            )

        # ---------------------------------------------------------
        # 4. Determine available years
        # ---------------------------------------------------------

        selected_year_columns = []

        for column in self.year_columns:

            column_str = str(column).strip()

            # Dataset format:
            # 1961

            if column_str.isdigit():

                year = int(column_str)

            # Dataset format:
            # Y1961

            elif (
                column_str.startswith("Y")
                and column_str[1:].isdigit()
            ):

                year = int(
                    column_str[1:]
                )

            else:

                continue

            # Apply requested start year

            if start_year is not None:

                if year < int(start_year):
                    continue

            # Apply requested end year

            if end_year is not None:

                if year > int(end_year):
                    continue

            selected_year_columns.append(
                (column, year)
            )

        if not selected_year_columns:

            raise ValueError(
                "No years are available for the selected range."
            )

        # ---------------------------------------------------------
        # 5. Convert wide format → long format
        # ---------------------------------------------------------

        rows = []

        for _, record in df.iterrows():

            for column, year in selected_year_columns:

                value = pd.to_numeric(
                    record[column],
                    errors="coerce"
                )

                if pd.notna(value):

                    rows.append({

                        "Area": area,

                        "Months": month,

                        "Element": element,

                        "YEAR": year,

                        "VALUE": float(value)
                    })

        if not rows:

            raise ValueError(
                "No valid numerical observations were found."
            )

        # ---------------------------------------------------------
        # 6. Create processed DataFrame
        # ---------------------------------------------------------

        processed = pd.DataFrame(
            rows
        )

        # Sort chronologically

        processed = (
            processed
            .sort_values("YEAR")
            .reset_index(drop=True)
        )

        # ---------------------------------------------------------
        # 7. Add decade
        # ---------------------------------------------------------

        processed["DECADE"] = (
            processed["YEAR"] // 10
        ) * 10

        # ---------------------------------------------------------
        # 8. Store current selection
        # ---------------------------------------------------------

        self.selected_country = area

        self.selected_element = element

        self.selected_month = month

        self.start_year = (
            int(start_year)
            if start_year is not None
            else None
        )

        self.end_year = (
            int(end_year)
            if end_year is not None
            else None
        )

        # ---------------------------------------------------------
        # 9. Store processed dataset
        # ---------------------------------------------------------

        self.processed_df = processed

        return self.processed_df

    # =========================================================
    # DATA ACCESS METHODS
    # =========================================================

    def get_processed_data(self):
        """
        Return the current analysis-ready dataset.

        VisualizationPage and other analysis modules
        use this method to access the shared processed data.
        """

        return self.processed_df

    def get_selected_country(self):
        """
        Return the currently selected country / area.
        """

        return self.selected_country

    # =========================================================
    # YEAR FILTERING
    # =========================================================

    def filter_by_year(
        self,
        start_year,
        end_year
    ):
        """Filter the current analytical dataset by year."""

        if self.processed_df is None:

            raise ValueError(
                "No analytical dataset is available."
            )

        return self.processed_df[
            (
                self.processed_df["YEAR"]
                >= int(start_year)
            )
            &
            (
                self.processed_df["YEAR"]
                <= int(end_year)
            )
        ].copy()

    # =========================================================
    # STATE / RESULTS
    # =========================================================

    def has_dataset(self):
        """Return True if a master dataset is loaded."""

        return (
            self.master_df is not None
            and not self.master_df.empty
        )

    def has_processed_data(self):
        """Return True if an analytical dataset exists."""

        return (
            self.processed_df is not None
            and not self.processed_df.empty
        )

    def clear_results(self):
        """Clear previous analysis results."""

        self.statistics_result = None

        self.trend_result = None

        self.ml_result = None

        self.prediction_result = None