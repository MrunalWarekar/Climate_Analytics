import os
import re
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor


# =========================================================
# 1. SETTINGS
# =========================================================

BASE_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_FILE = os.path.join(
    BASE_FOLDER,
    "DataSet.csv"
)

MODEL_FOLDER = os.path.join(
    BASE_FOLDER,
    "models",
    "yearly"
)

RESULT_FOLDER = os.path.join(
    BASE_FOLDER,
    "results",
    "yearly"
)

TRAIN_START_YEAR = 1966
TRAINING_END_YEAR = 2007

TEST_START_YEAR = 2008
TEST_END_YEAR = 2019

HISTORY_YEARS = 10

RIDGE_ALPHA = 1.0


# =========================================================
# 2. FOLDERS
# =========================================================

os.makedirs(
    MODEL_FOLDER,
    exist_ok=True
)

os.makedirs(
    RESULT_FOLDER,
    exist_ok=True
)


# =========================================================
# 3. FEATURES
# =========================================================

FEATURES = [

    "YEAR",

    "Lag_1",
    "Lag_2",
    "Lag_3",
    "Lag_4",
    "Lag_5",
    "Lag_6",
    "Lag_7",
    "Lag_8",
    "Lag_9",
    "Lag_10",

    "Mean_3",
    "Mean_5",
    "Mean_10",

    "Std_5",
    "Std_10",

    "Diff_1",
    "Diff_2",
    "Diff_3",
    "Diff_4",

    "Recent_Trend"

]

# Compatibility name used by prediction.py
FEATURE_COLUMNS = FEATURES.copy()


# =========================================================
# 4. SAFE COUNTRY NAME
# =========================================================

def make_safe_country_name(country):

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(country).strip().lower()
    )


# =========================================================
# 5. MODEL PATH
# =========================================================

def get_country_model_path(country):

    safe_country = make_safe_country_name(
        country
    )

    country_folder = os.path.join(
        MODEL_FOLDER,
        safe_country
    )

    os.makedirs(
        country_folder,
        exist_ok=True
    )

    return os.path.join(
        country_folder,
        "yearly_model.pkl"
    )


# =========================================================
# 6. RESULT FOLDER
# =========================================================

def get_country_result_folder(country):

    safe_country = make_safe_country_name(
        country
    )

    folder = os.path.join(
        RESULT_FOLDER,
        safe_country
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    return folder


# =========================================================
# 7. LOAD DATASET
# =========================================================

def load_dataset(
    filepath=DATASET_FILE
):

    if not os.path.isfile(filepath):

        raise FileNotFoundError(
            "DataSet.csv was not found.\n"
            f"Expected location:\n{filepath}"
        )

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
                filepath,
                encoding=encoding
            )

            df.columns = [
                str(column)
                .strip()
                .replace("\ufeff", "")
                for column in df.columns
            ]

            return df

        except Exception as error:

            last_error = error

    raise last_error


# =========================================================
# 8. GET COUNTRIES
# =========================================================

def get_available_countries(df):

    if isinstance(df, str):

        df = load_dataset(df)

    if "Area" not in df.columns:

        raise ValueError(
            "Area column was not found."
        )

    return sorted(
        df["Area"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )


# =========================================================
# 9. FIND COUNTRY
# =========================================================

def find_country(
    df,
    country_name
):

    countries = get_available_countries(
        df
    )

    requested = (
        str(country_name)
        .strip()
        .lower()
    )

    if not requested:

        raise ValueError(
            "Country name cannot be empty."
        )

    for country in countries:

        if country.lower() == requested:

            return country

    matches = [
        country
        for country in countries
        if requested in country.lower()
    ]

    if len(matches) == 1:

        return matches[0]

    if len(matches) > 1:

        raise ValueError(
            "Multiple countries matched:\n"
            +
            "\n".join(matches)
        )

    raise ValueError(
        f"Country '{country_name}' was not found."
    )


# =========================================================
# 10. DETECT YEAR COLUMNS
# =========================================================

def detect_year_columns(df):

    year_columns = {}

    for column in df.columns:

        text = str(column).strip()

        match = re.fullmatch(
            r"Y(\d{4})",
            text,
            re.IGNORECASE
        )

        if match:

            year_columns[
                int(match.group(1)
            )] = column

            continue

        if (
            text.isdigit()
            and
            len(text) == 4
        ):

            year = int(text)

            if (
                1800 <= year <= 2200
            ):

                year_columns[
                    year
                ] = column

    if not year_columns:

        raise ValueError(
            "No year columns were found."
        )

    return dict(
        sorted(
            year_columns.items()
        )
    )


# =========================================================
# 11. CREATE ANNUAL SERIES
# =========================================================

def create_annual_series(
    df,
    country,
    year_columns
):

    required_columns = [
        "Area",
        "Months",
        "Element"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing required columns: "
            +
            ", ".join(missing)
        )

    data = df[
        (
            df["Area"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            country.lower()
        )
        &
        (
            df["Months"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            "meteorological year"
        )
        &
        (
            df["Element"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            "temperature change"
        )
    ].copy()

    if data.empty:

        raise ValueError(
            "Annual temperature-change "
            "data was not found."
        )

    # -----------------------------------------------------
    # Convert year columns
    # -----------------------------------------------------

    for column in year_columns.values():

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Handle duplicate annual rows
    # -----------------------------------------------------

    annual_values = {}

    for year, column in year_columns.items():

        values = data[column].dropna()

        if not values.empty:

            annual_values[
                int(year)
            ] = float(
                values.mean()
            )

    annual_data = pd.Series(
        annual_values,
        dtype=float
    )

    annual_data.index = (
        annual_data.index.astype(int)
    )

    annual_data = annual_data.sort_index()

    if annual_data.empty:

        raise ValueError(
            "No usable annual temperature "
            "values were found."
        )

    return annual_data


# =========================================================
# 12. CREATE FEATURES
# =========================================================

def create_features(
    annual_data
):

    records = []

    first_year = (
        int(annual_data.index.min())
        +
        HISTORY_YEARS
    )

    last_year = min(
        int(annual_data.index.max()),
        TEST_END_YEAR
    )

    for year in range(
        first_year,
        last_year + 1
    ):

        required_years = [
            year - i
            for i in range(
                1,
                HISTORY_YEARS + 1
            )
        ]

        if not all(
            y in annual_data.index
            for y in required_years
        ):

            continue

        values = [
            float(
                annual_data[
                    year - i
                ]
            )
            for i in range(
                1,
                HISTORY_YEARS + 1
            )
        ]

        records.append({

            "YEAR":
                year,

            "Lag_1":
                values[0],

            "Lag_2":
                values[1],

            "Lag_3":
                values[2],

            "Lag_4":
                values[3],

            "Lag_5":
                values[4],

            "Lag_6":
                values[5],

            "Lag_7":
                values[6],

            "Lag_8":
                values[7],

            "Lag_9":
                values[8],

            "Lag_10":
                values[9],

            "Mean_3":
                np.mean(
                    values[:3]
                ),

            "Mean_5":
                np.mean(
                    values[:5]
                ),

            "Mean_10":
                np.mean(
                    values[:10]
                ),

            "Std_5":
                np.std(
                    values[:5]
                ),

            "Std_10":
                np.std(
                    values[:10]
                ),

            "Diff_1":
                values[0]
                -
                values[1],

            "Diff_2":
                values[1]
                -
                values[2],

            "Diff_3":
                values[2]
                -
                values[3],

            "Diff_4":
                values[3]
                -
                values[4],

            "Recent_Trend":
                np.mean(
                    values[:3]
                )
                -
                np.mean(
                    values[3:6]
                ),

            "Target":
                float(
                    annual_data[
                        year
                    ]
                )

        })

    model_data = pd.DataFrame(
        records
    )

    if model_data.empty:

        raise ValueError(
            "No usable annual records "
            "were created."
        )

    return model_data


# =========================================================
# 13. CREATE FIVE MODELS
# =========================================================

def create_models():

    models = {

        "Linear Regression":
            Pipeline([
                (
                    "scaler",
                    StandardScaler()
                ),
                (
                    "linear",
                    LinearRegression()
                )
            ]),

        "Ridge Regression":
            Pipeline([
                (
                    "scaler",
                    StandardScaler()
                ),
                (
                    "ridge",
                    Ridge(
                        alpha=RIDGE_ALPHA
                    )
                )
            ]),

        "Random Forest":
            RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                n_jobs=-1
            ),

        "Gradient Boosting":
            GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                random_state=42
            ),

        "XGBoost":
            XGBRegressor(
                n_estimators=300,
                learning_rate=0.03,
                max_depth=3,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="reg:squarederror",
                random_state=42,
                n_jobs=-1
            )
    }

    return models


# =========================================================
# 14. CREATE GRAPH
# =========================================================

def create_actual_vs_predicted_graph(
    results,
    country,
    model_name,
    output_path
):

    plt.figure(
        figsize=(12, 6)
    )

    plt.plot(
        results["YEAR"],
        results["ACTUAL"],
        label="Actual",
        linewidth=1.8
    )

    plt.plot(
        results["YEAR"],
        results["PREDICTED"],
        label="Predicted",
        linewidth=1.5
    )

    plt.title(
        "Yearly Temperature Change: "
        "Actual vs Predicted\n"
        f"{country} - {model_name}"
    )

    plt.xlabel(
        "Year"
    )

    plt.ylabel(
        "Temperature Change (°C)"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# =========================================================
# 15. TRAIN YEARLY MODEL
# =========================================================

def train_yearly_model(
    country,
    dataset_path=DATASET_FILE
):

    df = load_dataset(
        dataset_path
    )

    country = find_country(
        df,
        country
    )

    year_columns = detect_year_columns(
        df
    )

    annual_data = create_annual_series(
        df,
        country,
        year_columns
    )

    model_data = create_features(
        annual_data
    )

    # -----------------------------------------------------
    # TRAIN DATA
    # -----------------------------------------------------

    train = model_data[
        (
            model_data["YEAR"]
            >=
            TRAIN_START_YEAR
        )
        &
        (
            model_data["YEAR"]
            <=
            TRAINING_END_YEAR
        )
    ].copy()

    # -----------------------------------------------------
    # TEST DATA
    # -----------------------------------------------------

    test = model_data[
        (
            model_data["YEAR"]
            >=
            TEST_START_YEAR
        )
        &
        (
            model_data["YEAR"]
            <=
            TEST_END_YEAR
        )
    ].copy()

    if train.empty:

        raise ValueError(
            "Annual training data is empty."
        )

    if test.empty:

        raise ValueError(
            "Annual testing data is empty."
        )

    X_train = train[
        FEATURES
    ]

    y_train = train[
        "Target"
    ]

    X_test = test[
        FEATURES
    ]

    y_test = test[
        "Target"
    ]

    # -----------------------------------------------------
    # TRAIN ALL FIVE MODELS
    # -----------------------------------------------------

    models = create_models()

    comparison = []

    trained_models = {}

    predictions_by_model = {}

    print()
    print("=" * 75)
    print("YEARLY MODEL COMPARISON")
    print("=" * 75)

    for model_name, model in models.items():

        print()
        print(
            f"Training: {model_name}"
        )

        try:

            model.fit(
                X_train,
                y_train
            )

            predictions = np.asarray(
                model.predict(
                    X_test
                )
            )

            if not np.all(
                np.isfinite(
                    predictions
                )
            ):

                raise ValueError(
                    "Model produced "
                    "invalid predictions."
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

            r2 = r2_score(
                y_test,
                predictions
            )

            comparison.append({

                "Model":
                    model_name,

                "R2":
                    float(r2),

                "MAE":
                    float(mae),

                "MSE":
                    float(mse),

                "RMSE":
                    float(rmse)

            })

            trained_models[
                model_name
            ] = model

            predictions_by_model[
                model_name
            ] = predictions

            print(
                f"R²   : {r2:.4f}"
            )

            print(
                f"MAE  : {mae:.4f}"
            )

            print(
                f"MSE  : {mse:.4f}"
            )

            print(
                f"RMSE : {rmse:.4f}"
            )

        except Exception as error:

            print(
                f"FAILED: {error}"
            )

    if not comparison:

        raise RuntimeError(
            "None of the yearly models "
            "could be trained successfully."
        )

    # -----------------------------------------------------
    # COMPARISON TABLE
    # -----------------------------------------------------

    comparison_df = pd.DataFrame(
        comparison
    )

    # -----------------------------------------------------
    # BEST MODEL
    #
    # Lowest MAE = best model
    # -----------------------------------------------------

    comparison_df = comparison_df.sort_values(
        by="MAE",
        ascending=True
    ).reset_index(
        drop=True
    )

    best_model_name = comparison_df.iloc[0][
        "Model"
    ]

    best_model = trained_models[
        best_model_name
    ]

    best_predictions = predictions_by_model[
        best_model_name
    ]

    best_row = comparison_df.iloc[0]

    best_r2 = float(
        best_row["R2"]
    )

    best_mae = float(
        best_row["MAE"]
    )

    best_mse = float(
        best_row["MSE"]
    )

    best_rmse = float(
        best_row["RMSE"]
    )

    # -----------------------------------------------------
    # PRINT COMPARISON
    # -----------------------------------------------------

    print()
    print("=" * 75)
    print("MODEL COMPARISON RESULTS")
    print("=" * 75)

    print(
        comparison_df.to_string(
            index=False,
            float_format=lambda value:
                f"{value:.4f}"
        )
    )

    print()
    print(
        f"BEST MODEL: {best_model_name}"
    )

    print(
        f"Best MAE  : {best_mae:.4f}"
    )

    print(
        f"Best RMSE : {best_rmse:.4f}"
    )

    print(
        f"Best R²   : {best_r2:.4f}"
    )

    # -----------------------------------------------------
    # SAVE COMPARISON TABLE
    # -----------------------------------------------------

    result_folder = (
        get_country_result_folder(
            country
        )
    )

    comparison_csv_path = os.path.join(
        result_folder,
        "yearly_model_comparison.csv"
    )

    comparison_df.to_csv(
        comparison_csv_path,
        index=False
    )

    # -----------------------------------------------------
    # BEST MODEL TEST RESULTS
    # -----------------------------------------------------

    results = test[
        ["YEAR"]
    ].copy()

    results["ACTUAL"] = (
        y_test.values
    )

    results["PREDICTED"] = (
        best_predictions
    )

    results["ERROR"] = (
        results["ACTUAL"]
        -
        results["PREDICTED"]
    ).abs()

    csv_path = os.path.join(
        result_folder,
        "yearly_predictions.csv"
    )

    results.to_csv(
        csv_path,
        index=False
    )

    # -----------------------------------------------------
    # GRAPH
    # -----------------------------------------------------

    graph_path = os.path.join(
        result_folder,
        "01_actual_vs_predicted.png"
    )

    create_actual_vs_predicted_graph(
        results,
        country,
        best_model_name,
        graph_path
    )

    # -----------------------------------------------------
    # SAVE BEST MODEL
    # -----------------------------------------------------

    model_package = {

        "model":
            best_model,

        "model_name":
            best_model_name,

        "features":
            FEATURES.copy(),

        "country":
            country,

        "training_start_year":
            TRAIN_START_YEAR,

        "training_end_year":
            TRAINING_END_YEAR,

        "test_start_year":
            TEST_START_YEAR,

        "test_end_year":
            TEST_END_YEAR,

        "target":
            "Temperature change",

        "history_years":
            HISTORY_YEARS,

        "MAE":
            best_mae,

        "MSE":
            best_mse,

        "RMSE":
            best_rmse,

        "R2":
            best_r2,

        "model_comparison":
            comparison_df.to_dict(
                orient="records"
            ),

        "feature_version":
            "yearly_v3_five_model_comparison"

    }

    # Store Ridge alpha only when applicable
    if best_model_name == "Ridge Regression":

        model_package[
            "ridge_alpha"
        ] = RIDGE_ALPHA

    model_path = get_country_model_path(
        country
    )

    joblib.dump(
        model_package,
        model_path
    )

    print()
    print(
        f"Best model saved at:"
    )

    print(
        model_path
    )

    return {

        "country":
            country,

        "model_name":
            best_model_name,

        "r2":
            best_r2,

        "mae":
            best_mae,

        "mse":
            best_mse,

        "rmse":
            best_rmse,

        "model_path":
            model_path,

        "csv_path":
            csv_path,

        "comparison_csv_path":
            comparison_csv_path,

        "graph":
            graph_path,

        "graph_paths":
            [graph_path],

        "results":
            results,

        "comparison":
            comparison_df,

        "was_trained":
            True

    }


# =========================================================
# 16. VALIDATE MODEL PACKAGE
# =========================================================

def is_valid_model_package(
    package
):

    if not isinstance(
        package,
        dict
    ):

        return False

    if "model" not in package:

        return False

    if "model_name" not in package:

        return False

    if "features" not in package:

        return False

    if list(
        package.get(
            "features",
            []
        )
    ) != list(FEATURES):

        return False

    allowed_models = {

        "Linear Regression",
        "Ridge Regression",
        "Random Forest",
        "Gradient Boosting",
        "XGBoost"

    }

    if package.get(
        "model_name"
    ) not in allowed_models:

        return False

    if int(
        package.get(
            "history_years",
            -1
        )
    ) != HISTORY_YEARS:

        return False

    return True


# =========================================================
# 17. LOAD SAVED MODEL
# =========================================================

def load_yearly_model(
    country
):

    model_path = get_country_model_path(
        country
    )

    if not os.path.isfile(
        model_path
    ):

        return None

    try:

        package = joblib.load(
            model_path
        )

    except Exception:

        return None

    if not is_valid_model_package(
        package
    ):

        return None

    return package


# =========================================================
# 18. LOAD OR TRAIN
# =========================================================

def load_or_train_yearly_model(
    country,
    dataset_path=DATASET_FILE
):

    df = load_dataset(
        dataset_path
    )

    country = find_country(
        df,
        country
    )

    existing_model = load_yearly_model(
        country
    )

    if existing_model is not None:

        return (
            existing_model,
            False
        )

    train_yearly_model(
        country,
        dataset_path
    )

    package = load_yearly_model(
        country
    )

    if package is None:

        raise RuntimeError(
            "Yearly model training completed "
            "but a valid saved model could not "
            "be loaded."
        )

    return (
        package,
        True
    )


# =========================================================
# 19. RUN YEARLY ANALYSIS
# =========================================================

def run_yearly_analysis(
    country,
    dataset_path=DATASET_FILE
):

    df = load_dataset(
        dataset_path
    )

    country = find_country(
        df,
        country
    )

    model_package, was_trained = (
        load_or_train_yearly_model(
            country,
            dataset_path
        )
    )

    model = model_package[
        "model"
    ]

    year_columns = detect_year_columns(
        df
    )

    annual_data = create_annual_series(
        df,
        country,
        year_columns
    )

    model_data = create_features(
        annual_data
    )

    test = model_data[
        (
            model_data["YEAR"]
            >=
            TEST_START_YEAR
        )
        &
        (
            model_data["YEAR"]
            <=
            TEST_END_YEAR
        )
    ].copy()

    if test.empty:

        raise ValueError(
            "Annual testing data is empty."
        )

    X_test = test[
        FEATURES
    ]

    y_test = test[
        "Target"
    ]

    predictions = np.asarray(
        model.predict(
            X_test
        )
    )

    if not np.all(
        np.isfinite(
            predictions
        )
    ):

        raise ValueError(
            "Model produced invalid predictions."
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

    r2 = r2_score(
        y_test,
        predictions
    )

    results = test[
        ["YEAR"]
    ].copy()

    results["ACTUAL"] = (
        y_test.values
    )

    results["PREDICTED"] = (
        predictions
    )

    results["ERROR"] = (
        results["ACTUAL"]
        -
        results["PREDICTED"]
    ).abs()

    result_folder = (
        get_country_result_folder(
            country
        )
    )

    csv_path = os.path.join(
        result_folder,
        "yearly_predictions.csv"
    )

    results.to_csv(
        csv_path,
        index=False
    )

    graph_path = os.path.join(
        result_folder,
        "01_actual_vs_predicted.png"
    )

    create_actual_vs_predicted_graph(
        results,
        country,
        model_package.get(
            "model_name",
            "Best Model"
        ),
        graph_path
    )

    return {

        "country":
            country,

        "model_name":
            model_package.get(
                "model_name",
                "Best Model"
            ),

        "r2":
            float(r2),

        "mae":
            float(mae),

        "mse":
            float(mse),

        "rmse":
            float(rmse),

        "was_trained":
            was_trained,

        "model_path":
            get_country_model_path(
                country
            ),

        "csv_path":
            csv_path,

        # Important for your GUI
        "graph":
            graph_path,

        "graph_paths":
            [graph_path],

        "results":
            results,

        "comparison":
            model_package.get(
                "model_comparison",
                []
            )

    }


# =========================================================
# 20. CREATE FUTURE FEATURES
# =========================================================

def create_future_features(
    history,
    target_year
):

    if len(history) < HISTORY_YEARS:

        raise ValueError(
            "At least 10 previous yearly "
            "values are required."
        )

    values = []

    for i in range(
        1,
        HISTORY_YEARS + 1
    ):

        year = target_year - i

        if year not in history:

            raise ValueError(
                f"Missing historical value "
                f"for year {year}."
            )

        values.append(
            float(
                history[year]
            )
        )

    return {

        "YEAR":
            target_year,

        "Lag_1":
            values[0],

        "Lag_2":
            values[1],

        "Lag_3":
            values[2],

        "Lag_4":
            values[3],

        "Lag_5":
            values[4],

        "Lag_6":
            values[5],

        "Lag_7":
            values[6],

        "Lag_8":
            values[7],

        "Lag_9":
            values[8],

        "Lag_10":
            values[9],

        "Mean_3":
            np.mean(
                values[:3]
            ),

        "Mean_5":
            np.mean(
                values[:5]
            ),

        "Mean_10":
            np.mean(
                values[:10]
            ),

        "Std_5":
            np.std(
                values[:5]
            ),

        "Std_10":
            np.std(
                values[:10]
            ),

        "Diff_1":
            values[0]
            -
            values[1],

        "Diff_2":
            values[1]
            -
            values[2],

        "Diff_3":
            values[2]
            -
            values[3],

        "Diff_4":
            values[3]
            -
            values[4],

        "Recent_Trend":
            np.mean(
                values[:3]
            )
            -
            np.mean(
                values[3:6]
            )
    }


# =========================================================
# 21. PREDICT FUTURE YEAR
# =========================================================

def predict_future_temperature(
    country,
    target_year,
    dataset_path=DATASET_FILE
):

    target_year = int(
        target_year
    )

    if target_year <= 0:

        raise ValueError(
            "Target year must be valid."
        )

    df = load_dataset(
        dataset_path
    )

    country = find_country(
        df,
        country
    )

    model_package, was_trained = (
        load_or_train_yearly_model(
            country,
            dataset_path
        )
    )

    model = model_package[
        "model"
    ]

    year_columns = detect_year_columns(
        df
    )

    annual_data = create_annual_series(
        df,
        country,
        year_columns
    )

    history = {
        int(year):
            float(value)
        for year, value
        in annual_data.items()
        if pd.notna(value)
    }

    last_available_year = max(
        history.keys()
    )

    # -----------------------------------------------------
    # If target year is already available,
    # return a prediction based on the saved model
    # using historical information.
    # -----------------------------------------------------

    if target_year <= last_available_year:

        feature_row = create_future_features(
            history,
            target_year
        )

        X = pd.DataFrame(
            [feature_row]
        )[FEATURES]

        prediction = float(
            model.predict(X)[0]
        )

        return {

            "country":
                country,

            "year":
                target_year,

            "prediction":
                prediction,

            "model_name":
                model_package[
                    "model_name"
                ],

            "trained":
                was_trained,

            "historical_data":
                True

        }

    # -----------------------------------------------------
    # Future prediction
    #
    # Predict one year at a time.
    # A predicted year becomes part of the history
    # for the next predicted year.
    # -----------------------------------------------------

    current_year = (
        last_available_year + 1
    )

    prediction = None

    while current_year <= target_year:

        feature_row = create_future_features(
            history,
            current_year
        )

        X = pd.DataFrame(
            [feature_row]
        )[FEATURES]

        prediction = float(
            model.predict(X)[0]
        )

        if not np.isfinite(
            prediction
        ):

            raise ValueError(
                "Model produced an invalid "
                "future prediction."
            )

        history[
            current_year
        ] = prediction

        current_year += 1

    return {

        "country":
            country,

        "year":
            target_year,

        "prediction":
            float(prediction),

        "model_name":
            model_package[
                "model_name"
            ],

        "trained":
            was_trained,

        "historical_data":
            False

    }


# =========================================================
# 22. MAIN
# =========================================================

def main():

    print()
    print("=" * 75)
    print("YEARLY CLIMATE TEMPERATURE MODEL")
    print("=" * 75)

    try:

        df = load_dataset()

        countries = get_available_countries(
            df
        )

        print()

        print(
            f"Countries available: "
            f"{len(countries)}"
        )

        selected_input = input(
            "\nEnter country name: "
        ).strip()

        if not selected_input:

            print(
                "\nERROR: Country name cannot be empty."
            )

            return

        result = run_yearly_analysis(
            selected_input
        )

        print()
        print("=" * 75)
        print("TEMPERATURE CHANGE ANALYSIS")
        print("=" * 75)

        print()

        print(
            f"Country    : "
            f"{result['country']}"
        )

        print(
            f"Model Used : "
            f"{result['model_name']}"
        )

        print()

        print(
            f"R²         : "
            f"{result['r2']:.4f}"
        )

        print(
            f"MAE        : "
            f"{result['mae']:.4f}"
        )

        print(
            f"MSE        : "
            f"{result['mse']:.4f}"
        )

        print(
            f"RMSE       : "
            f"{result['rmse']:.4f}"
        )

        print()

        if result["was_trained"]:

            print(
                "✓ Five models were trained "
                "and compared."
            )

            print(
                "✓ Best model was selected "
                "and saved."
            )

        else:

            print(
                "✓ Existing best model "
                "was loaded."
            )

        print(
            "✓ Analysis completed successfully."
        )

        print(
            "✓ Graph is ready."
        )

        print()

        print(
            "Graph saved at:"
        )

        print(
            result["graph"]
        )

        print()

        print("=" * 75)

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )


# =========================================================
# 23. START
# =========================================================

if __name__ == "__main__":

    main()