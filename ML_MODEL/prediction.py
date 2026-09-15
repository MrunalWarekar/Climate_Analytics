import os

from train_model import (
    DATASET_FILE,
    load_yearly_model,
    train_yearly_model
)

from monthly_training import (
    load_monthly_model,
    train_monthly_model,
    predict_future_temperature as monthly_predict_future_temperature
)


# =========================================================
# YEARLY PREDICTION
# =========================================================

def predict_yearly_temperature(
    country,
    target_year,
    dataset_path=DATASET_FILE
):

    # -----------------------------------------------------
    # Check whether saved yearly model exists
    # -----------------------------------------------------

    package = load_yearly_model(
        country
    )

    trained = False

    # -----------------------------------------------------
    # Automatically train if model does not exist
    # -----------------------------------------------------

    if package is None:

        train_yearly_model(
            country,
            dataset_path
        )

        package = load_yearly_model(
            country
        )

        trained = True

    # -----------------------------------------------------
    # Make sure model exists
    # -----------------------------------------------------

    if package is None:

        raise RuntimeError(
            "Yearly model could not be loaded or trained."
        )

    # -----------------------------------------------------
    # Import yearly prediction function
    # -----------------------------------------------------

    import train_model

    if hasattr(
        train_model,
        "predict_future_temperature"
    ):

        result = (
            train_model
            .predict_future_temperature(
                country,
                target_year,
                dataset_path
            )
        )

        if isinstance(
            result,
            dict
        ):

            result["trained"] = trained

            return result

        return {

            "country":
                country,

            "year":
                target_year,

            "prediction":
                float(result),

            "trained":
                trained

        }

    # -----------------------------------------------------
    # If yearly prediction function doesn't exist
    # -----------------------------------------------------

    raise RuntimeError(
        "train_model.py does not contain "
        "predict_future_temperature()."
    )


# =========================================================
# MONTHLY PREDICTION
# =========================================================

def predict_monthly_temperature(
    country,
    target_year,
    target_month,
    dataset_path=DATASET_FILE
):

    # -----------------------------------------------------
    # Check whether saved monthly model exists
    # -----------------------------------------------------

    package = load_monthly_model(
        country
    )

    trained = False

    # -----------------------------------------------------
    # Automatically train if model does not exist
    # -----------------------------------------------------

    if package is None:

        train_monthly_model(
            country,
            dataset_path
        )

        package = load_monthly_model(
            country
        )

        trained = True

    # -----------------------------------------------------
    # Make sure model exists
    # -----------------------------------------------------

    if package is None:

        raise RuntimeError(
            "Monthly model could not be loaded or trained."
        )

    # -----------------------------------------------------
    # Make prediction
    # -----------------------------------------------------

    result = monthly_predict_future_temperature(
        country,
        target_year,
        target_month,
        dataset_path
    )

    # -----------------------------------------------------
    # Return dictionary result
    # -----------------------------------------------------

    if isinstance(
        result,
        dict
    ):

        result["trained"] = trained

        return result

    return {

        "country":
            country,

        "year":
            target_year,

        "month":
            target_month,

        "prediction":
            float(result),

        "trained":
            trained

    }


# =========================================================
# GENERIC PREDICTION FUNCTION
# =========================================================

def predict_temperature(
    country,
    target_year,
    mode="yearly",
    month=None,
    dataset_path=DATASET_FILE
):

    mode = str(
        mode
    ).strip().lower()

    # -----------------------------------------------------
    # YEARLY
    # -----------------------------------------------------

    if mode == "yearly":

        return predict_yearly_temperature(
            country,
            target_year,
            dataset_path
        )

    # -----------------------------------------------------
    # MONTHLY
    # -----------------------------------------------------

    if mode == "monthly":

        if month is None:

            raise ValueError(
                "Month is required for monthly prediction."
            )

        return predict_monthly_temperature(
            country,
            target_year,
            month,
            dataset_path
        )

    # -----------------------------------------------------
    # Invalid mode
    # -----------------------------------------------------

    raise ValueError(
        "Mode must be either 'yearly' or 'monthly'."
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "prediction.py is ready."
    )