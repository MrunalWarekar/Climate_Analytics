import os
import re
import pickle
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import Ridge
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

warnings.filterwarnings("ignore")


# =========================================================
# PATHS
# =========================================================

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

DATASET_FILE = os.path.join(
    BASE_FOLDER,
    "DataSet.csv"
)

MODEL_FOLDER = os.path.join(
    BASE_FOLDER,
    "models",
    "monthly"
)

RESULT_FOLDER = os.path.join(
    BASE_FOLDER,
    "results",
    "monthly"
)

os.makedirs(MODEL_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


# =========================================================
# SETTINGS
# =========================================================

TRAIN_START_YEAR = 1966
TRAIN_END_YEAR = 2007

TEST_START_YEAR = 2008
TEST_END_YEAR = 2019

RIDGE_ALPHA = 50.0


# =========================================================
# MONTH ORDER
# =========================================================

MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset(file_path=DATASET_FILE):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1"
    ]

    last_error = None

    for encoding in encodings:

        try:

            df = pd.read_csv(
                file_path,
                encoding=encoding
            )

            break

        except Exception as e:

            last_error = e

    else:

        raise last_error

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


# =========================================================
# FIND YEAR COLUMNS
# =========================================================

def get_year_columns(df):

    year_columns = {}

    for column in df.columns:

        column_string = str(column).strip()

        match = re.fullmatch(
            r"Y(\d{4})",
            column_string
        )

        if match:

            year = int(match.group(1))

            year_columns[year] = column

            continue

        match = re.fullmatch(
            r"(\d{4})",
            column_string
        )

        if match:

            year = int(match.group(1))

            year_columns[year] = column

    if not year_columns:

        raise ValueError(
            "No year columns such as Y1961, Y1962, etc. were found."
        )

    return dict(
        sorted(
            year_columns.items()
        )
    )


# =========================================================
# SAFE COUNTRY NAME
# =========================================================

def safe_country_name(country):

    return re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        str(country).strip()
    ).strip("_").lower()


# =========================================================
# GET AVAILABLE COUNTRIES
# =========================================================

def get_available_countries(
    data_source=DATASET_FILE
):
    """
    Returns all countries available in the dataset.

    Accepts either:
        - pandas DataFrame
        - dataset file path
    """

    if isinstance(
        data_source,
        pd.DataFrame
    ):

        df = data_source

    else:

        df = load_dataset(
            data_source
        )

    if "Area" not in df.columns:

        raise ValueError(
            "Area column was not found."
        )

    countries = (

        df["Area"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()

    )

    return sorted(
        countries
    )


# =========================================================
# GET AVAILABLE MONTHS
# =========================================================

def get_available_months(
    data_source=DATASET_FILE
):
    """
    Returns the calendar months available
    in the dataset in chronological order.

    Only the 12 calendar months are returned.
    Entries such as 'Meteorological year'
    are ignored.
    """

    if isinstance(
        data_source,
        pd.DataFrame
    ):

        df = data_source

    else:

        df = load_dataset(
            data_source
        )

    if "Months" not in df.columns:

        raise ValueError(
            "Months column was not found."
        )

    available_months = (

        df["Months"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()

    )

    normalized_months = {

        str(month).strip().lower():
            str(month).strip()

        for month in available_months

    }

    result = []

    for month in MONTH_ORDER:

        if month.lower() in normalized_months:

            result.append(month)

    return result


# =========================================================
# FIND COUNTRY
# =========================================================

def find_country(
    df,
    country_name
):

    countries = get_available_countries(
        df
    )

    if country_name not in countries:

        raise ValueError(
            f"Country '{country_name}' was not found."
        )

    country_df = df[
        df["Area"].astype(str).str.strip()
        == str(country_name).strip()
    ].copy()

    return country_df


# =========================================================
# GET TEMPERATURE DATA
# =========================================================

def get_temperature_data(
    country_df
):

    if "Element" not in country_df.columns:

        raise ValueError(
            "Element column was not found."
        )

    temperature_df = country_df[
        country_df["Element"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "temperature change"
    ].copy()

    if temperature_df.empty:

        raise ValueError(
            "Temperature change data was not found."
        )

    if "Months" not in temperature_df.columns:

        raise ValueError(
            "Months column was not found."
        )

    year_columns = get_year_columns(
        temperature_df
    )

    records = []

    for _, row in temperature_df.iterrows():

        month = str(
            row["Months"]
        ).strip()

        if month not in MONTH_ORDER:

            continue

        for year, column in year_columns.items():

            value = row[column]

            try:

                value = float(value)

            except:

                continue

            if np.isnan(value):

                continue

            records.append({

                "YEAR": year,
                "MONTH": month,
                "TEMPERATURE": value

            })

    result = pd.DataFrame(
        records
    )

    if result.empty:

        raise ValueError(
            "No temperature-change records were found."
        )

    month_mapping = {
        month: index + 1
        for index, month
        in enumerate(MONTH_ORDER)
    }

    result["MONTH_NUMBER"] = (
        result["MONTH"]
        .map(month_mapping)
    )

    result = result.sort_values(
        ["YEAR", "MONTH_NUMBER"]
    ).reset_index(
        drop=True
    )

    return result


# =========================================================
# CREATE FEATURES
# =========================================================

def create_features(
    temperature_df
):

    df = temperature_df.copy()

    df = df.sort_values(
        ["YEAR", "MONTH_NUMBER"]
    ).reset_index(
        drop=True
    )

    # -----------------------------------------------------
    # Calendar features
    # -----------------------------------------------------

    df["SIN_MONTH"] = np.sin(
        2 * np.pi *
        df["MONTH_NUMBER"] / 12
    )

    df["COS_MONTH"] = np.cos(
        2 * np.pi *
        df["MONTH_NUMBER"] / 12
    )

    # -----------------------------------------------------
    # Previous month
    # -----------------------------------------------------

    df["PREVIOUS_MONTH"] = (
        df["TEMPERATURE"].shift(1)
    )

    # -----------------------------------------------------
    # Previous 2 months
    # -----------------------------------------------------

    df["TWO_MONTHS_AGO"] = (
        df["TEMPERATURE"].shift(2)
    )

    # -----------------------------------------------------
    # Previous 3 months
    # -----------------------------------------------------

    df["THREE_MONTHS_AGO"] = (
        df["TEMPERATURE"].shift(3)
    )

    # -----------------------------------------------------
    # Previous 4 months
    # -----------------------------------------------------

    df["FOUR_MONTHS_AGO"] = (
        df["TEMPERATURE"].shift(4)
    )

    # -----------------------------------------------------
    # Same month previous years
    # -----------------------------------------------------

    temperature_lookup = {

        (
            int(row.YEAR),
            int(row.MONTH_NUMBER)
        ): row.TEMPERATURE

        for row in df.itertuples()

    }

    for years_back in range(1, 6):

        values = []

        for row in df.itertuples():

            previous_year = (
                int(row.YEAR)
                - years_back
            )

            value = temperature_lookup.get(
                (
                    previous_year,
                    int(row.MONTH_NUMBER)
                ),
                np.nan
            )

            values.append(value)

        df[
            f"SAME_MONTH_{years_back}Y"
        ] = values

    # -----------------------------------------------------
    # Rolling features
    # -----------------------------------------------------

    df["ROLLING_MEAN_3M"] = (
        df["TEMPERATURE"]
        .shift(1)
        .rolling(3)
        .mean()
    )

    df["ROLLING_MEAN_6M"] = (
        df["TEMPERATURE"]
        .shift(1)
        .rolling(6)
        .mean()
    )

    df["ROLLING_MEAN_12M"] = (
        df["TEMPERATURE"]
        .shift(1)
        .rolling(12)
        .mean()
    )

    # -----------------------------------------------------
    # Momentum
    #
    # Uses only information before target month.
    # -----------------------------------------------------

    df["MOMENTUM_1M"] = (
        df["PREVIOUS_MONTH"]
        - df["TWO_MONTHS_AGO"]
    )

    # -----------------------------------------------------
    # Year-over-year change
    #
    # Uses previous month's value and previous
    # year's same-month value.
    # -----------------------------------------------------

    df["YEAR_OVER_YEAR_CHANGE"] = (
        df["PREVIOUS_MONTH"]
        - df["SAME_MONTH_1Y"]
    )

    return df


# =========================================================
# FEATURE COLUMNS
# =========================================================

FEATURE_COLUMNS = [

    "YEAR",
    "MONTH_NUMBER",
    "SIN_MONTH",
    "COS_MONTH",

    "PREVIOUS_MONTH",
    "TWO_MONTHS_AGO",
    "THREE_MONTHS_AGO",
    "FOUR_MONTHS_AGO",

    "SAME_MONTH_1Y",
    "SAME_MONTH_2Y",
    "SAME_MONTH_3Y",
    "SAME_MONTH_4Y",
    "SAME_MONTH_5Y",

    "ROLLING_MEAN_3M",
    "ROLLING_MEAN_6M",
    "ROLLING_MEAN_12M",

    "MOMENTUM_1M",
    "YEAR_OVER_YEAR_CHANGE"

]


# =========================================================
# MODEL PATH
# =========================================================

def get_model_path(country):

    country_folder = os.path.join(
        MODEL_FOLDER,
        safe_country_name(country)
    )

    os.makedirs(
        country_folder,
        exist_ok=True
    )

    return os.path.join(
        country_folder,
        "ridge_strong_monthly_model.pkl"
    )


# =========================================================
# RESULT FOLDER
# =========================================================

def get_result_folder(country):

    folder = os.path.join(
        RESULT_FOLDER,
        safe_country_name(country)
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    return folder


# =========================================================
# TRAIN MONTHLY MODEL
# =========================================================

def train_monthly_model(
    country,
    dataset_path=DATASET_FILE
):

    df = load_dataset(
        dataset_path
    )

    country_df = find_country(
        df,
        country
    )

    temperature_df = get_temperature_data(
        country_df
    )

    feature_df = create_features(
        temperature_df
    )

    train_df = feature_df[
        (
            feature_df["YEAR"]
            >= TRAIN_START_YEAR
        )
        &
        (
            feature_df["YEAR"]
            <= TRAIN_END_YEAR
        )
    ].copy()

    test_df = feature_df[
        (
            feature_df["YEAR"]
            >= TEST_START_YEAR
        )
        &
        (
            feature_df["YEAR"]
            <= TEST_END_YEAR
        )
    ].copy()

    # -----------------------------------------------------
    # Remove rows with missing feature values
    # -----------------------------------------------------

    train_df = train_df.dropna(
        subset=FEATURE_COLUMNS + [
            "TEMPERATURE"
        ]
    )

    test_df = test_df.dropna(
        subset=FEATURE_COLUMNS + [
            "TEMPERATURE"
        ]
    )

    if train_df.empty:

        raise ValueError(
            "Training data is empty."
        )

    if test_df.empty:

        raise ValueError(
            "Testing data is empty."
        )

    X_train = train_df[
        FEATURE_COLUMNS
    ]

    y_train = train_df[
        "TEMPERATURE"
    ]

    X_test = test_df[
        FEATURE_COLUMNS
    ]

    y_test = test_df[
        "TEMPERATURE"
    ]

    # -----------------------------------------------------
    # Ridge Strong
    # -----------------------------------------------------

    model = Ridge(
        alpha=RIDGE_ALPHA
    )

    model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # Predictions
    # -----------------------------------------------------

    predictions = model.predict(
        X_test
    )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    r2 = r2_score(
        y_test,
        predictions
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    mse = mean_squared_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mse
    )

    # -----------------------------------------------------
    # Save model package
    # -----------------------------------------------------

    model_package = {

        "model": model,

        "feature_columns":
            FEATURE_COLUMNS,

        "model_name":
            "Ridge Strong",

        "alpha":
            RIDGE_ALPHA,

        "country":
            country

    }

    model_path = get_model_path(
        country
    )

    with open(
        model_path,
        "wb"
    ) as file:

        pickle.dump(
            model_package,
            file
        )

    # -----------------------------------------------------
    # Actual vs Predicted graph
    # -----------------------------------------------------

    result_folder = get_result_folder(
        country
    )

    graph_path = os.path.join(
        result_folder,
        "01_actual_vs_predicted.png"
    )

    plt.figure(
        figsize=(12, 6)
    )

    plt.plot(
        range(len(y_test)),
        y_test.values,
        label="Actual"
    )

    plt.plot(
        range(len(predictions)),
        predictions,
        label="Predicted"
    )

    plt.title(
        f"{country} - Monthly Temperature Change\n"
        "Ridge Strong"
    )

    plt.xlabel(
        "Test observations"
    )

    plt.ylabel(
        "Temperature change"
    )

    plt.legend()

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        graph_path,
        dpi=150
    )

    plt.close()

    return {

        "country":
            country,

        "model":
            "Ridge Strong",

        "r2":
            r2,

        "mae":
            mae,

        "mse":
            mse,

        "rmse":
            rmse,

        "graph":
            graph_path,

        "model_path":
            model_path

    }


# =========================================================
# LOAD SAVED MODEL
# =========================================================

def load_monthly_model(
    country
):

    model_path = get_model_path(
        country
    )

    if not os.path.exists(
        model_path
    ):

        return None

    with open(
        model_path,
        "rb"
    ) as file:

        package = pickle.load(
            file
        )

    return package


# =========================================================
# LOAD OR TRAIN
# =========================================================

def load_or_train_monthly_model(
    country,
    dataset_path=DATASET_FILE
):

    package = load_monthly_model(
        country
    )

    if package is not None:

        return package, False

    train_monthly_model(
        country,
        dataset_path
    )

    package = load_monthly_model(
        country
    )

    if package is None:

        raise RuntimeError(
            "Monthly model could not be created."
        )

    return package, True


# =========================================================
# CREATE PREDICTION FEATURES
# =========================================================

def create_prediction_features(
    history_df,
    target_year,
    target_month_number
):

    history = history_df.copy()

    history = history.sort_values(
        ["YEAR", "MONTH_NUMBER"]
    ).reset_index(
        drop=True
    )

    target_month_name = MONTH_ORDER[
        target_month_number - 1
    ]

    # -----------------------------------------------------
    # Previous month
    # -----------------------------------------------------

    previous_month_value = np.nan

    if not history.empty:

        previous_month_value = (
            history.iloc[-1]["TEMPERATURE"]
        )

    # -----------------------------------------------------
    # Two months ago
    # -----------------------------------------------------

    two_months_ago = np.nan

    if len(history) >= 2:

        two_months_ago = (
            history.iloc[-2]["TEMPERATURE"]
        )

    # -----------------------------------------------------
    # Three months ago
    # -----------------------------------------------------

    three_months_ago = np.nan

    if len(history) >= 3:

        three_months_ago = (
            history.iloc[-3]["TEMPERATURE"]
        )

    # -----------------------------------------------------
    # Four months ago
    # -----------------------------------------------------

    four_months_ago = np.nan

    if len(history) >= 4:

        four_months_ago = (
            history.iloc[-4]["TEMPERATURE"]
        )

    # -----------------------------------------------------
    # Lookup same month previous years
    # -----------------------------------------------------

    lookup = {

        (
            int(row.YEAR),
            int(row.MONTH_NUMBER)
        ):
            float(row.TEMPERATURE)

        for row in history.itertuples()

    }

    same_month_values = []

    for years_back in range(1, 6):

        value = lookup.get(
            (
                target_year - years_back,
                target_month_number
            ),
            np.nan
        )

        same_month_values.append(
            value
        )

    # -----------------------------------------------------
    # Rolling means
    # -----------------------------------------------------

    recent_values = history[
        "TEMPERATURE"
    ].tolist()

    rolling_3 = np.nan
    rolling_6 = np.nan
    rolling_12 = np.nan

    if len(recent_values) >= 3:

        rolling_3 = np.mean(
            recent_values[-3:]
        )

    if len(recent_values) >= 6:

        rolling_6 = np.mean(
            recent_values[-6:]
        )

    if len(recent_values) >= 12:

        rolling_12 = np.mean(
            recent_values[-12:]
        )

    # -----------------------------------------------------
    # Momentum
    # -----------------------------------------------------

    momentum = np.nan

    if (
        not np.isnan(previous_month_value)
        and
        not np.isnan(two_months_ago)
    ):

        momentum = (
            previous_month_value
            - two_months_ago
        )

    # -----------------------------------------------------
    # Year-over-year change
    # -----------------------------------------------------

    previous_year_same_month = (
        same_month_values[0]
    )

    yoy_change = np.nan

    if (
        not np.isnan(previous_month_value)
        and
        not np.isnan(previous_year_same_month)
    ):

        yoy_change = (
            previous_month_value
            - previous_year_same_month
        )

    # -----------------------------------------------------
    # Create feature row
    # -----------------------------------------------------

    row = {

        "YEAR":
            target_year,

        "MONTH_NUMBER":
            target_month_number,

        "SIN_MONTH":
            np.sin(
                2 * np.pi *
                target_month_number / 12
            ),

        "COS_MONTH":
            np.cos(
                2 * np.pi *
                target_month_number / 12
            ),

        "PREVIOUS_MONTH":
            previous_month_value,

        "TWO_MONTHS_AGO":
            two_months_ago,

        "THREE_MONTHS_AGO":
            three_months_ago,

        "FOUR_MONTHS_AGO":
            four_months_ago,

        "SAME_MONTH_1Y":
            same_month_values[0],

        "SAME_MONTH_2Y":
            same_month_values[1],

        "SAME_MONTH_3Y":
            same_month_values[2],

        "SAME_MONTH_4Y":
            same_month_values[3],

        "SAME_MONTH_5Y":
            same_month_values[4],

        "ROLLING_MEAN_3M":
            rolling_3,

        "ROLLING_MEAN_6M":
            rolling_6,

        "ROLLING_MEAN_12M":
            rolling_12,

        "MOMENTUM_1M":
            momentum,

        "YEAR_OVER_YEAR_CHANGE":
            yoy_change

    }

    return pd.DataFrame(
        [row]
    )


# =========================================================
# MONTHLY PREDICTION
# =========================================================

def predict_future_temperature(
    country,
    target_year,
    target_month,
    dataset_path=DATASET_FILE
):

    # -----------------------------------------------------
    # Convert month
    # -----------------------------------------------------

    if isinstance(
        target_month,
        str
    ):

        target_month = target_month.strip()

        if target_month not in MONTH_ORDER:

            raise ValueError(
                f"Invalid month: {target_month}"
            )

        target_month_number = (
            MONTH_ORDER.index(
                target_month
            ) + 1
        )

    else:

        target_month_number = int(
            target_month
        )

        if not (
            1 <= target_month_number <= 12
        ):

            raise ValueError(
                "Month number must be between 1 and 12."
            )

        target_month = MONTH_ORDER[
            target_month_number - 1
        ]

    # -----------------------------------------------------
    # Load or train model
    # -----------------------------------------------------

    package, trained = (
        load_or_train_monthly_model(
            country,
            dataset_path
        )
    )

    model = package[
        "model"
    ]

    # -----------------------------------------------------
    # Load historical data
    # -----------------------------------------------------

    df = load_dataset(
        dataset_path
    )

    country_df = find_country(
        df,
        country
    )

    history = get_temperature_data(
        country_df
    )

    # -----------------------------------------------------
    # Predict future months sequentially
    #
    # This allows future predictions to use earlier
    # predicted values when necessary.
    # -----------------------------------------------------

    last_year = int(
        history["YEAR"].max()
    )

    last_month = int(
        history[
            history["YEAR"] == last_year
        ]["MONTH_NUMBER"].max()
    )

    predictions = {}

    current_history = history.copy()

    # -----------------------------------------------------
    # If target is in the past
    # -----------------------------------------------------

    if (
        target_year < last_year
        or
        (
            target_year == last_year
            and
            target_month_number <= last_month
        )
    ):

        prediction_features = (
            create_prediction_features(
                current_history,
                target_year,
                target_month_number
            )
        )

        prediction_features = (
            prediction_features[
                FEATURE_COLUMNS
            ]
        )

        prediction_features = (
            prediction_features.fillna(
                current_history[
                    "TEMPERATURE"
                ].mean()
            )
        )

        prediction = model.predict(
            prediction_features
        )[0]

        return {

            "country":
                country,

            "year":
                target_year,

            "month":
                target_month,

            "prediction":
                float(prediction),

            "trained":
                trained

        }

    # -----------------------------------------------------
    # Predict month-by-month until target
    # -----------------------------------------------------

    for year in range(
        last_year,
        target_year + 1
    ):

        start_month = 1

        if year == last_year:

            start_month = (
                last_month + 1
            )

        for month_number in range(
            start_month,
            13
        ):

            if (
                year == target_year
                and
                month_number >
                target_month_number
            ):

                break

            features = (
                create_prediction_features(
                    current_history,
                    year,
                    month_number
                )
            )

            X = features[
                FEATURE_COLUMNS
            ]

            # -------------------------------------------------
            # Fill unavailable early features using historical
            # mean. Normally this is only relevant at the very
            # beginning of a prediction sequence.
            # -------------------------------------------------

            X = X.fillna(
                current_history[
                    "TEMPERATURE"
                ].mean()
            )

            prediction = model.predict(
                X
            )[0]

            new_row = {

                "YEAR":
                    year,

                "MONTH":
                    MONTH_ORDER[
                        month_number - 1
                    ],

                "MONTH_NUMBER":
                    month_number,

                "TEMPERATURE":
                    float(prediction)

            }

            current_history = pd.concat(
                [
                    current_history,
                    pd.DataFrame(
                        [new_row]
                    )
                ],
                ignore_index=True
            )

            predictions[
                (
                    year,
                    month_number
                )
            ] = float(
                prediction
            )

    final_prediction = predictions[
        (
            target_year,
            target_month_number
        )
    ]

    return {

        "country":
            country,

        "year":
            target_year,

        "month":
            target_month,

        "prediction":
            final_prediction,

        "trained":
            trained

    }


# =========================================================
# RUN MONTHLY ANALYSIS
# =========================================================

def run_monthly_analysis(
    country,
    dataset_path=DATASET_FILE,
    selected_month=None
):

    # -----------------------------------------------------
    # Train/load model
    # -----------------------------------------------------

    package, trained = (
        load_or_train_monthly_model(
            country,
            dataset_path
        )
    )

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------

    df = load_dataset(
        dataset_path
    )

    country_df = find_country(
        df,
        country
    )

    temperature_df = get_temperature_data(
        country_df
    )

    feature_df = create_features(
        temperature_df
    )

    # -----------------------------------------------------
    # If a month is selected, filter it
    # -----------------------------------------------------

    if selected_month is not None:

        selected_month = (
            str(selected_month)
            .strip()
        )

        if selected_month not in MONTH_ORDER:

            raise ValueError(
                f"Invalid month: {selected_month}"
            )

        feature_df = feature_df[
            feature_df["MONTH"]
            == selected_month
        ].copy()

    # -----------------------------------------------------
    # Test data
    # -----------------------------------------------------

    test_df = feature_df[
        (
            feature_df["YEAR"]
            >= TEST_START_YEAR
        )
        &
        (
            feature_df["YEAR"]
            <= TEST_END_YEAR
        )
    ].copy()

    test_df = test_df.dropna(
        subset=FEATURE_COLUMNS + [
            "TEMPERATURE"
        ]
    )

    if test_df.empty:

        raise ValueError(
            "No test data available for the selected month."
        )

    model = package[
        "model"
    ]

    X_test = test_df[
        FEATURE_COLUMNS
    ]

    y_test = test_df[
        "TEMPERATURE"
    ]

    predictions = model.predict(
        X_test
    )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    r2 = r2_score(
        y_test,
        predictions
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    mse = mean_squared_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mse
    )

    # -----------------------------------------------------
    # Graph
    # -----------------------------------------------------

    result_folder = get_result_folder(
        country
    )

    if selected_month:

        graph_name = (
            "01_actual_vs_predicted_"
            + safe_country_name(
                selected_month
            )
            + ".png"
        )

    else:

        graph_name = (
            "01_actual_vs_predicted.png"
        )

    graph_path = os.path.join(
        result_folder,
        graph_name
    )

    plt.figure(
        figsize=(12, 6)
    )

    plt.plot(
        test_df["YEAR"].values,
        y_test.values,
        marker="o",
        label="Actual"
    )

    plt.plot(
        test_df["YEAR"].values,
        predictions,
        marker="o",
        label="Predicted"
    )

    title = (
        f"{country} - Monthly Temperature Change"
    )

    if selected_month:

        title += (
            f" - {selected_month}"
        )

    title += "\nRidge Strong"

    plt.title(
        title
    )

    plt.xlabel(
        "Year"
    )

    plt.ylabel(
        "Temperature change"
    )

    plt.legend()

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        graph_path,
        dpi=150
    )

    plt.close()

    return {

        "country":
            country,

        "month":
            selected_month,

        "model":
            "Ridge Strong",

        "r2":
            r2,

        "mae":
            mae,

        "mse":
            mse,

        "rmse":
            rmse,

        "graph":
            graph_path,

        "model_path":
            get_model_path(
                country
            ),

        "trained":
            trained

    }


# =========================================================
# COMMAND LINE
# =========================================================

if __name__ == "__main__":

    print(
        "\nMonthly Temperature Model"
    )

    df = load_dataset()

    countries = get_available_countries(
        df
    )

    print(
        "\nAvailable countries:"
    )

    for index, country in enumerate(
        countries,
        start=1
    ):

        print(
            f"{index}. {country}"
        )

    country = input(
        "\nEnter country: "
    ).strip()

    months = get_available_months(
        df
    )

    print(
        "\nAvailable months:"
    )

    for index, month in enumerate(
        months,
        start=1
    ):

        print(
            f"{index}. {month}"
        )

    selected_month = input(
        "\nEnter month: "
    ).strip()

    result = run_monthly_analysis(
        country,
        DATASET_FILE,
        selected_month
    )

    print(
        "\n--------------------------------"
    )

    print(
        f"Country    : {result['country']}"
    )

    print(
        f"Model Used : {result['model']}"
    )

    print(
        f"Month      : {result['month']}"
    )

    print()

    print(
        f"R²         : {result['r2']:.4f}"
    )

    print(
        f"MAE        : {result['mae']:.4f}"
    )

    print(
        f"MSE        : {result['mse']:.4f}"
    )

    print(
        f"RMSE       : {result['rmse']:.4f}"
    )

    print()

    print(
        "✓ Analysis completed successfully."
    )

    print(
        "✓ Graph is ready."
    )