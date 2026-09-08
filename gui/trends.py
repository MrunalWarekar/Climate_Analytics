import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_FOLDER = os.path.join(BASE_DIR, "datasets")
GRAPHS_FOLDER = os.path.join(BASE_DIR, "graphs")
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")

graphs_folder = GRAPHS_FOLDER

os.makedirs(GRAPHS_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)


# ============================================================
# DATASETS
# ============================================================

DATASETS = [
    "Environment_Temperature_change_E_All_Data_NOFLAG.csv",
    "Monthly_Min_Temp_IMD-1901_to_2019_0.csv",
    "TEMP_ANNUAL_SEASONAL_MEAN.csv",
    "India_Max_Temperatures_1901-2012_1.xls",
    "Mean_Temperatures_India1901-2012.csv",
    "India_Min_Temperatures_1901-2012_1.xls"
]


# ============================================================
# TECHNO VIBRANT THEME
# ============================================================

TECH_BG = "#080B18"
TECH_PANEL = "#10162A"

CYAN = "#00F5FF"
BLUE = "#3B82F6"
PURPLE = "#A855F7"
PINK = "#FF2BD6"
GREEN = "#00FFA3"
ORANGE = "#FFB000"
RED = "#FF4D6D"

TEXT = "#F4F7FF"
MUTED = "#9BA7C7"
GRID = "#26304D"


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):
    """
    Normalizes text so that values such as:

    TEMPERATURE_CHANGE
    Temperature Change
    temperature change

    are treated as the same value.
    """

    if pd.isna(value):
        return ""

    text = str(value).strip()
    text = text.replace("\ufeff", "")
    text = text.replace("_", " ")
    text = text.replace("-", " ")

    return " ".join(text.upper().split())


# ============================================================
# GRAPH STYLE
# ============================================================

def setup_techno_style(title):

    fig, ax = plt.subplots(figsize=(12, 6))

    fig.patch.set_facecolor(TECH_BG)
    ax.set_facecolor(TECH_PANEL)

    ax.set_title(
        title,
        fontsize=18,
        fontweight="bold",
        color=TEXT,
        pad=18
    )

    ax.tick_params(colors=TEXT)

    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)

    for spine in ax.spines.values():
        spine.set_color(GRID)

    ax.grid(
        True,
        linestyle="--",
        alpha=0.35,
        color=GRID
    )

    return fig, ax


def save_techno_graph(fig, output_path):

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=300,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# READ DATASET
# ============================================================

def read_dataset(file_path):

    try:

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".csv":

            df = pd.read_csv(file_path)

        elif extension == ".xls":

            if "India_Min_Temperatures_1901-2012_1.xls" in file_path:

                df = pd.read_excel(
                    file_path,
                    engine="xlrd",
                    header=1
                )

            else:

                df = pd.read_excel(
                    file_path,
                    engine="xlrd"
                )

        elif extension == ".xlsx":

            df = pd.read_excel(
                file_path,
                engine="openpyxl"
            )

        else:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        # Remove completely empty rows and columns
        df = df.dropna(
            axis=0,
            how="all"
        )

        df = df.dropna(
            axis=1,
            how="all"
        )

        # Clean column names
        df.columns = [
            str(col).strip().replace("\ufeff", "")
            for col in df.columns
        ]

        return df

    except Exception as e:

        print(
            f"Error reading dataset {file_path}: {e}"
        )

        return None


# ============================================================
# FIND YEAR COLUMNS
# ============================================================

def get_year_columns(df):

    year_columns = []

    for col in df.columns:

        col_text = str(col).strip().replace("\ufeff", "")

        if col_text.upper().startswith("Y"):

            year_part = col_text[1:]

            if year_part.isdigit() and len(year_part) == 4:

                year_columns.append(col)

        elif col_text.isdigit() and len(col_text) == 4:

            year_columns.append(col)

    return year_columns


# ============================================================
# EXTRACT YEAR VALUE
# ============================================================

def extract_year_value(df, dataset_number=None):

    # --------------------------------------------------------
    # DATASET 1
    # Environment Temperature Change
    # --------------------------------------------------------

    if dataset_number == 1:

        normalized_columns = {}

        for col in df.columns:

            clean_col = (
                str(col)
                .strip()
                .replace("\ufeff", "")
                .upper()
                .replace(" ", "_")
            )

            normalized_columns[clean_col] = col

        required_columns = {
            "AREA",
            "MONTHS",
            "ELEMENT"
        }

        if not required_columns.issubset(
            set(normalized_columns.keys())
        ):

            raise ValueError(
                "Dataset 1 does not contain AREA, MONTHS and ELEMENT columns."
            )

        area_col = normalized_columns["AREA"]
        months_col = normalized_columns["MONTHS"]
        element_col = normalized_columns["ELEMENT"]

        area_values = df[area_col].map(normalize_text)
        months_values = df[months_col].map(normalize_text)
        element_values = df[element_col].map(normalize_text)

        # Match India + Temperature Change
        base_mask = (
            (area_values == "INDIA") &
            (element_values == "TEMPERATURE CHANGE")
        )

        # Prefer ANNUAL if available
        annual_mask = (
            base_mask &
            (months_values == "ANNUAL")
        )

        meteorological_mask = (
            base_mask &
            (months_values == "METEOROLOGICAL YEAR")
        )

        if annual_mask.any():

            selected_rows = df.loc[annual_mask]

        elif meteorological_mask.any():

            selected_rows = df.loc[meteorological_mask]

        else:

            selected_rows = df.loc[base_mask]

        if selected_rows.empty:

            raise ValueError(
                "Could not find India's annual temperature-change data."
            )

        year_columns = get_year_columns(selected_rows)

        if not year_columns:

            raise ValueError(
                "No yearly columns found in Dataset 1."
            )

        years = []
        values = []

        for col in year_columns:

            col_text = str(col).strip().replace("\ufeff", "")

            if col_text.upper().startswith("Y"):

                year = int(col_text[1:])

            else:

                year = int(col_text)

            numeric_values = pd.to_numeric(
                selected_rows[col],
                errors="coerce"
            )

            value = numeric_values.mean()

            if not pd.isna(value):

                years.append(year)
                values.append(value)

        return pd.DataFrame(
            {
                "YEAR": years,
                "VALUE": values
            }
        )


    # ========================================================
    # GENERAL CASE 1
    # YEAR column exists
    # ========================================================

    normalized_lookup = {}

    for col in df.columns:

        clean_col = (
            str(col)
            .strip()
            .replace("\ufeff", "")
            .upper()
        )

        normalized_lookup[clean_col] = col

    if "YEAR" in normalized_lookup:

        year_col = normalized_lookup["YEAR"]

        # Prefer ANNUAL column
        annual_col = None

        for key, original_col in normalized_lookup.items():

            if key == "ANNUAL":

                annual_col = original_col
                break

        if annual_col is not None:

            values = pd.to_numeric(
                df[annual_col],
                errors="coerce"
            )

        else:

            numeric_columns = df.select_dtypes(
                include=np.number
            ).columns

            possible_columns = []

            for col in numeric_columns:

                if col != year_col:

                    if df[col].notna().sum() > 5:

                        possible_columns.append(col)

            if not possible_columns:

                raise ValueError(
                    "No suitable numeric value column found."
                )

            values = pd.to_numeric(
                df[possible_columns[0]],
                errors="coerce"
            )

        years = pd.to_numeric(
            df[year_col],
            errors="coerce"
        )

        result = pd.DataFrame(
            {
                "YEAR": years,
                "VALUE": values
            }
        )

        result = result.dropna(
            subset=["YEAR", "VALUE"]
        )

        result["YEAR"] = result["YEAR"].astype(int)

        return result


    # ========================================================
    # GENERAL CASE 2
    # Y1961, Y1962 ... style columns
    # ========================================================

    year_columns = get_year_columns(df)

    if year_columns:

        years = []
        values = []

        for col in year_columns:

            col_text = str(col).strip().replace(
                "\ufeff",
                ""
            )

            if col_text.upper().startswith("Y"):

                year = int(col_text[1:])

            else:

                year = int(col_text)

            numeric_values = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            value = numeric_values.mean()

            if not pd.isna(value):

                years.append(year)
                values.append(value)

        if years:

            return pd.DataFrame(
                {
                    "YEAR": years,
                    "VALUE": values
                }
            )


    # ========================================================
    # GENERAL CASE 3
    # Search for year-like numeric column
    # ========================================================

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    year_column = None

    for col in numeric_columns:

        values = pd.to_numeric(
            df[col],
            errors="coerce"
        ).dropna()

        if len(values) > 5:

            if (
                values.min() >= 1800
                and values.max() <= 2100
            ):

                year_column = col
                break

    if year_column is not None:

        value_columns = [
            col
            for col in numeric_columns
            if col != year_column
        ]

        if value_columns:

            years = pd.to_numeric(
                df[year_column],
                errors="coerce"
            )

            values = pd.to_numeric(
                df[value_columns[0]],
                errors="coerce"
            )

            result = pd.DataFrame(
                {
                    "YEAR": years,
                    "VALUE": values
                }
            )

            result = result.dropna(
                subset=["YEAR", "VALUE"]
            )

            result["YEAR"] = result["YEAR"].astype(int)

            return result

    raise ValueError(
        "Unable to extract yearly temperature values."
    )


# ============================================================
# STATISTICAL CALCULATIONS
# ============================================================

def calculate_highest(data):

    index = data["VALUE"].idxmax()

    return (
        data.loc[index, "YEAR"],
        data.loc[index, "VALUE"]
    )


def calculate_lowest(data):

    index = data["VALUE"].idxmin()

    return (
        data.loc[index, "YEAR"],
        data.loc[index, "VALUE"]
    )


def calculate_decadal_average(data):

    temp = data.copy()

    temp["DECADE"] = (
        temp["YEAR"] // 10
    ) * 10

    decadal = (
        temp
        .groupby("DECADE")["VALUE"]
        .mean()
        .reset_index()
    )

    return decadal


def calculate_trend(data):

    years = data["YEAR"].values
    values = data["VALUE"].values

    if len(years) < 2:

        return 0, "Stable"

    slope, intercept = np.polyfit(
        years,
        values,
        1
    )

    if slope > 0.0001:

        direction = "Increasing"

    elif slope < -0.0001:

        direction = "Decreasing"

    else:

        direction = "Stable"

    return slope, direction


def calculate_moving_average(data, window=5):

    result = data.copy()

    result["MOVING_AVERAGE"] = (
        result["VALUE"]
        .rolling(window=window)
        .mean()
    )

    return result


def calculate_anomaly(data):

    result = data.copy()

    baseline = result["VALUE"].mean()

    result["ANOMALY"] = (
        result["VALUE"] - baseline
    )

    return result, baseline


# ============================================================
# TREND GRAPH
# ============================================================

def create_trend_graph(
    data,
    dataset_number,
    dataset_name,
    slope,
    highest,
    lowest
):

    fig, ax = setup_techno_style(
        f"Temperature Trend Analysis\n{dataset_name}"
    )

    years = data["YEAR"]
    values = data["VALUE"]

    ax.plot(
        years,
        values,
        color=CYAN,
        linewidth=1.5,
        alpha=0.8,
        label="Annual Temperature"
    )

    trend_values = (
        slope * years
        + (
            values.mean()
            - slope * years.mean()
        )
    )

    ax.plot(
        years,
        trend_values,
        color=PINK,
        linewidth=3,
        label="Linear Trend"
    )

    highest_year, highest_value = highest
    lowest_year, lowest_value = lowest

    ax.scatter(
        highest_year,
        highest_value,
        color=GREEN,
        s=80,
        zorder=5
    )

    ax.scatter(
        lowest_year,
        lowest_value,
        color=RED,
        s=80,
        zorder=5
    )

    ax.annotate(
        f"Highest\n{highest_year}: {highest_value:.2f}",
        xy=(highest_year, highest_value),
        xytext=(10, 20),
        textcoords="offset points",
        color=GREEN,
        fontsize=9,
        fontweight="bold"
    )

    ax.annotate(
        f"Lowest\n{lowest_year}: {lowest_value:.2f}",
        xy=(lowest_year, lowest_value),
        xytext=(10, -35),
        textcoords="offset points",
        color=RED,
        fontsize=9,
        fontweight="bold"
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Temperature Change")

    ax.legend(
        facecolor=TECH_PANEL,
        edgecolor=GRID,
        labelcolor=TEXT
    )

    output_path = os.path.join(
        GRAPHS_FOLDER,
        f"trend_{dataset_number}.png"
    )

    save_techno_graph(
        fig,
        output_path
    )


# ============================================================
# DECADAL GRAPH
# ============================================================

def create_decadal_graph(
    decadal,
    dataset_name
):

    fig, ax = setup_techno_style(
        f"Decadal Temperature Trend\n{dataset_name}"
    )

    ax.plot(
        decadal["DECADE"],
        decadal["VALUE"],
        color=PURPLE,
        linewidth=3,
        marker="o",
        markersize=7
    )

    ax.fill_between(
        decadal["DECADE"],
        decadal["VALUE"],
        alpha=0.15,
        color=PURPLE
    )

    ax.set_xlabel("Decade")
    ax.set_ylabel("Average Temperature")

    output_path = os.path.join(
        GRAPHS_FOLDER,
        "decadal_trend.png"
    )

    save_techno_graph(
        fig,
        output_path
    )


# ============================================================
# SEASONAL GRAPH
# ============================================================

def create_seasonal_graph(
    df,
    dataset_number,
    dataset_name
):

    normalized_lookup = {}

    for col in df.columns:

        clean_col = (
            str(col)
            .strip()
            .replace("\ufeff", "")
            .upper()
        )

        normalized_lookup[clean_col] = col

    if "YEAR" not in normalized_lookup:

        return

    year_col = normalized_lookup["YEAR"]

    seasonal_columns = [
        "JAN-FEB",
        "MAR-MAY",
        "JUN-SEP",
        "OCT-DEC"
    ]

    available_seasons = []

    for season in seasonal_columns:

        if season in normalized_lookup:

            available_seasons.append(
                (
                    season,
                    normalized_lookup[season]
                )
            )

    if not available_seasons:

        return

    fig, ax = setup_techno_style(
        f"Seasonal Temperature Trends\n{dataset_name}"
    )

    years = pd.to_numeric(
        df[year_col],
        errors="coerce"
    )

    for season_name, original_col in available_seasons:

        values = pd.to_numeric(
            df[original_col],
            errors="coerce"
        )

        valid = (
            years.notna()
            & values.notna()
        )

        ax.plot(
            years[valid],
            values[valid],
            linewidth=2,
            marker="o",
            markersize=4,
            label=season_name
        )

    ax.set_xlabel("Year")
    ax.set_ylabel("Temperature")

    ax.legend(
        facecolor=TECH_PANEL,
        edgecolor=GRID,
        labelcolor=TEXT
    )

    output_path = os.path.join(
        GRAPHS_FOLDER,
        f"seasonal_{dataset_number}.png"
    )

    save_techno_graph(
        fig,
        output_path
    )


# ============================================================
# MOVING AVERAGE GRAPH
# ============================================================

def create_moving_average_graph(
    data,
    dataset_number,
    dataset_name
):

    moving_data = calculate_moving_average(
        data,
        window=5
    )

    fig, ax = setup_techno_style(
        f"5-Year Moving Average\n{dataset_name}"
    )

    ax.plot(
        moving_data["YEAR"],
        moving_data["VALUE"],
        color=CYAN,
        linewidth=1.2,
        alpha=0.5,
        label="Annual Value"
    )

    ax.plot(
        moving_data["YEAR"],
        moving_data["MOVING_AVERAGE"],
        color=ORANGE,
        linewidth=3,
        label="5-Year Moving Average"
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Temperature")

    ax.legend(
        facecolor=TECH_PANEL,
        edgecolor=GRID,
        labelcolor=TEXT
    )

    output_path = os.path.join(
        GRAPHS_FOLDER,
        f"moving_average_{dataset_number}.png"
    )

    save_techno_graph(
        fig,
        output_path
    )


# ============================================================
# ANOMALY GRAPH
# ============================================================

def create_anomaly_graph(
    data,
    dataset_number,
    dataset_name
):

    anomaly_data, baseline = calculate_anomaly(
        data
    )

    fig, ax = setup_techno_style(
        f"Temperature Anomaly Analysis\n{dataset_name}"
    )

    ax.bar(
        anomaly_data["YEAR"],
        anomaly_data["ANOMALY"],
        alpha=0.8
    )

    ax.axhline(
        0,
        linewidth=1.5,
        color=TEXT
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Temperature Anomaly")

    output_path = os.path.join(
        GRAPHS_FOLDER,
        f"anomaly_{dataset_number}.png"
    )

    save_techno_graph(
        fig,
        output_path
    )


# ============================================================
# COMPARISON GRAPH
# ============================================================

def create_comparison_graph(results):

    if not results:

        return

    names = [
        result["dataset"]
        for result in results
    ]

    slopes = [
        result["slope"]
        for result in results
    ]

    fig, ax = setup_techno_style(
        "Climate Trend Comparison"
    )

    x = np.arange(len(names))

    bars = ax.bar(
        x,
        slopes,
        alpha=0.85
    )

    ax.axhline(
        0,
        color=TEXT,
        linewidth=1.2
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        [
            f"Dataset {i + 1}"
            for i in range(len(names))
        ]
    )

    ax.set_xlabel("Dataset")
    ax.set_ylabel("Trend Slope")

    # Dataset mapping
    mapping_text = "\n".join(
        [
            f"Dataset {i + 1}: {name}"
            for i, name in enumerate(names)
        ]
    )

    ax.text(
        1.02,
        0.98,
        mapping_text,
        transform=ax.transAxes,
        verticalalignment="top",
        color=TEXT,
        fontsize=8,
        bbox=dict(
            facecolor=TECH_PANEL,
            edgecolor=GRID,
            alpha=0.9
        )
    )

    for bar, slope in zip(bars, slopes):

        height = bar.get_height()

        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            height,
            f"{slope:.4f}",
            ha="center",
            va="bottom"
            if height >= 0
            else "top",
            color=TEXT,
            fontsize=9
        )

    output_path = os.path.join(
        GRAPHS_FOLDER,
        "comparison_chart.png"
    )

    save_techno_graph(
        fig,
        output_path
    )


# ============================================================
# INSIGHTS
# ============================================================

def generate_insights(
    data,
    slope,
    direction,
    highest,
    lowest,
    baseline
):

    start_year = int(
        data["YEAR"].min()
    )

    end_year = int(
        data["YEAR"].max()
    )

    highest_year, highest_value = highest
    lowest_year, lowest_value = lowest

    insights = []

    if direction == "Increasing":

        insights.append(
            "The temperature trend is increasing over the analyzed period."
        )

    elif direction == "Decreasing":

        insights.append(
            "The temperature trend is decreasing over the analyzed period."
        )

    else:

        insights.append(
            "The temperature trend remains relatively stable over the analyzed period."
        )

    insights.append(
        f"The highest value was {highest_value:.2f} in {int(highest_year)}."
    )

    insights.append(
        f"The lowest value was {lowest_value:.2f} in {int(lowest_year)}."
    )

    insights.append(
        f"The baseline average temperature value was {baseline:.2f}."
    )

    insights.append(
        f"The calculated linear trend slope was {slope:.4f} per year."
    )

    insights.append(
        f"The analysis covers the period from {start_year} to {end_year}."
    )

    return " ".join(insights)


# ============================================================
# PROCESS DATASET
# ============================================================

def process_dataset(
    file_path,
    dataset_number
):

    dataset_name = os.path.basename(
        file_path
    )

    print(
        f"\nProcessing Dataset {dataset_number}: {dataset_name}"
    )

    df = read_dataset(
        file_path
    )

    if df is None:

        return None

    try:

        data = extract_year_value(
            df,
            dataset_number
        )

        data = data.sort_values(
            "YEAR"
        ).reset_index(
            drop=True
        )

        if data.empty:

            raise ValueError(
                "No valid yearly data found."
            )

        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        highest = calculate_highest(
            data
        )

        lowest = calculate_lowest(
            data
        )

        slope, direction = calculate_trend(
            data
        )

        _, baseline = calculate_anomaly(
            data
        )

        decadal = calculate_decadal_average(
            data
        )

        # ----------------------------------------------------
        # PRINT RESULTS
        # ----------------------------------------------------

        print(
            f"Start Year      : {int(data['YEAR'].min())}"
        )

        print(
            f"End Year        : {int(data['YEAR'].max())}"
        )

        print(
            f"Highest Value   : {highest[1]:.4f} ({int(highest[0])})"
        )

        print(
            f"Lowest Value    : {lowest[1]:.4f} ({int(lowest[0])})"
        )

        print(
            f"Slope           : {slope:.6f}"
        )

        print(
            f"Trend Direction : {direction}"
        )

        print(
            f"Baseline        : {baseline:.4f}"
        )

        # ----------------------------------------------------
        # GRAPHS
        # ----------------------------------------------------

        create_trend_graph(
            data,
            dataset_number,
            dataset_name,
            slope,
            highest,
            lowest
        )

        create_moving_average_graph(
            data,
            dataset_number,
            dataset_name
        )

        create_anomaly_graph(
            data,
            dataset_number,
            dataset_name
        )

        # ----------------------------------------------------
        # SEASONAL GRAPH
        # ----------------------------------------------------

        normalized_columns = {
            str(col)
            .strip()
            .replace("\ufeff", "")
            .upper()
            for col in df.columns
        }

        required_seasonal = {
            "YEAR",
            "JAN-FEB",
            "MAR-MAY",
            "JUN-SEP",
            "OCT-DEC"
        }

        if (
            "YEAR" in normalized_columns
            and
            any(
                season in normalized_columns
                for season in [
                    "JAN-FEB",
                    "MAR-MAY",
                    "JUN-SEP",
                    "OCT-DEC"
                ]
            )
        ):

            create_seasonal_graph(
                df,
                dataset_number,
                dataset_name
            )

        # ----------------------------------------------------
        # INSIGHTS
        # ----------------------------------------------------

        insight = generate_insights(
            data,
            slope,
            direction,
            highest,
            lowest,
            baseline
        )

        print(
            f"\nInsight:\n{insight}"
        )

        return {
            "dataset": dataset_name,
            "start_year": int(
                data["YEAR"].min()
            ),
            "end_year": int(
                data["YEAR"].max()
            ),
            "highest_year": int(
                highest[0]
            ),
            "highest_value": float(
                highest[1]
            ),
            "lowest_year": int(
                lowest[0]
            ),
            "lowest_value": float(
                lowest[1]
            ),
            "slope": float(
                slope
            ),
            "trend_direction": direction,
            "baseline": float(
                baseline
            ),
            "insight": insight
        }

    except Exception as e:

        print(
            f"Error processing Dataset {dataset_number}: {e}"
        )

        return None


# ============================================================
# SAVE REPORTS
# ============================================================

def save_reports(results):

    if not results:

        return

    results_df = pd.DataFrame(
        results
    )

    csv_path = os.path.join(
        REPORTS_FOLDER,
        "climate_analysis_results.csv"
    )

    xlsx_path = os.path.join(
        REPORTS_FOLDER,
        "climate_analysis_results.xlsx"
    )

    results_df.to_csv(
        csv_path,
        index=False
    )

    results_df.to_excel(
        xlsx_path,
        index=False
    )

    print(
        f"\nCSV Report saved: {csv_path}"
    )

    print(
        f"Excel Report saved: {xlsx_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "CLIMATE ANALYTICS SYSTEM"
    )

    print(
        "TREND & CLIMATE ANALYSIS"
    )

    print(
        "=" * 70
    )

    results = []

    all_decadal = []

    # --------------------------------------------------------
    # PROCESS ALL DATASETS
    # --------------------------------------------------------

    for index, dataset in enumerate(
        DATASETS,
        start=1
    ):

        file_path = os.path.join(
            DATASET_FOLDER,
            dataset
        )

        if not os.path.exists(file_path):

            print(
                f"\nDataset not found: {file_path}"
            )

            continue

        result = process_dataset(
            file_path,
            index
        )

        if result is not None:

            results.append(
                result
            )

            # Get decadal data
            try:

                df = read_dataset(
                    file_path
                )

                data = extract_year_value(
                    df,
                    index
                )

                data = data.sort_values(
                    "YEAR"
                )

                decadal = calculate_decadal_average(
                    data
                )

                all_decadal.append(
                    (
                        dataset,
                        decadal
                    )
                )

            except Exception as e:

                print(
                    f"Could not calculate decadal data: {e}"
                )

    # --------------------------------------------------------
    # DECADAL GRAPH
    # --------------------------------------------------------

    if all_decadal:

        first_dataset, first_decadal = (
            all_decadal[0]
        )

        create_decadal_graph(
            first_decadal,
            first_dataset
        )

    # --------------------------------------------------------
    # COMPARISON GRAPH
    # --------------------------------------------------------

    if results:

        create_comparison_graph(
            results
        )

    # --------------------------------------------------------
    # SAVE REPORTS
    # --------------------------------------------------------

    save_reports(
        results
    )

    # --------------------------------------------------------
    # FINAL MESSAGE
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "CLIMATE ANALYSIS COMPLETED SUCCESSFULLY"
    )

    print(
        "=" * 70
    )

    print(
        f"Datasets processed: {len(results)}"
    )

    print(
        f"Graphs saved in: {GRAPHS_FOLDER}"
    )

    print(
        f"Reports saved in: {REPORTS_FOLDER}"
    )

    print(
        "=" * 70
    )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()