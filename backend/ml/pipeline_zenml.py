import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from zenml import pipeline, step
from zenml.client import Client
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from backend.ml.preprocessing.data_cleaner import DataCleaner
from backend.ml.preprocessing.data_loader import DataLoader
from backend.ml.training.train import DataTraining, MLModelFactory, ModelType
from backend.ml.utils import TrainingRun, PromotionResult, wait_until_model_ready
import mlflow
from mlflow.data.pandas_dataset import from_pandas
import mlflow.sklearn as mlflow_sklearn
from backend.shared.loki_handler import get_loki_logger
load_dotenv()

ml_pipeline_logger = get_loki_logger("ml_pipeline", {"app": "ml_pipeline", "env": "prod"})
experiment_tracker = Client().active_stack.experiment_tracker

if experiment_tracker is None:
    raise RuntimeError("The active ZenML stack has no experiment tracker configured.")

model = MLModelFactory(ModelType.RANDOM_FOREST)

MODEL_NAME = model.model.value
PRODUCTION_ALIAS = "champion"
MODEL_ARTIFACT_PATH = "model"
SKOPS_TRUSTED_TYPES = [
    "sklearn.compose._column_transformer._RemainderColsList",
    "xgboost.core.Booster",
    "xgboost.sklearn.XGBRegressor",
]
MSE_METRIC_NAME = "mean_squared_error"
R2_METRIC_NAME = "r2_score"
TRAINING_MAE_METRIC_NAME = "training_mean_absolute_error"
TRAINING_MSE_METRIC_NAME = "training_mean_squared_error"
TRAINING_RMSE_METRIC_NAME = "training_root_mean_squared_error"
TRAINING_R2_METRIC_NAME = "training_r2_score"
STANDARDIZE_COLUMNS = [
    "house_money",
    "living_space",
    "internet_speed_telekom",
    "building_year",
    "property_space",
]
TARGET_COLUMN = "price"


def get_training_metrics(output) -> dict[str, float]:
    return {
        MSE_METRIC_NAME: output.mse,
        R2_METRIC_NAME: output.r2,
        TRAINING_MAE_METRIC_NAME: output.training_mean_absolute_error,
        TRAINING_MSE_METRIC_NAME: output.training_mean_squared_error,
        TRAINING_RMSE_METRIC_NAME: output.training_root_mean_squared_error,
        TRAINING_R2_METRIC_NAME: output.training_r2_score,
    }

@step(enable_cache=False)
def load_data():
    engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)
    data_loader = DataLoader(engine)

    df_apartments = data_loader.load_from_db(estate="apartments")
    df_houses = data_loader.load_from_db(estate="houses")

    return df_apartments, df_houses


@step(enable_cache=False)
def clean_rent_data(data):
    df_apartments, df_houses = data
    engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)

    data_cleaner_rent = DataCleaner(
        engine,
        numeric_cols=["living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money", "rent_complete", "rent_cold"],
        american_cols=["energy_demand"],
        bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
        drop_cols=["total_costs", "price_m2", "url", "general_description", "object_description", "place_description", "other_description", "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "price", "price_m2", "agency_id", "id", "title", "available_from", "rent_deposit", "ad_type", "listing_type", "rent_extra_costs"],
        drop_missing=["rent_complete", "estate_type"],
        fill_none_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source", "internet_speed_telekom"],
    )

    df_houses_rent = data_cleaner_rent.filter_listing_types(df_houses, data_cleaner_rent.RENT_LISTING_TYPES)
    df_apartments_rent = data_cleaner_rent.filter_listing_types(df_apartments, data_cleaner_rent.RENT_LISTING_TYPES)

    df_apartments_rent = data_cleaner_rent.preprocessing(df_apartments_rent)
    df_houses_rent = data_cleaner_rent.preprocessing(df_houses_rent)

    return data_cleaner_rent.postprocessing(df_apartments_rent, df_houses_rent)


@step(enable_cache=False)
def clean_buy_data(data):
    df_apartments, df_houses = data
    engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)

    data_cleaner_buy = DataCleaner(
        engine,
        numeric_cols=["property_space", "price", "living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money", "rent_complete", "rent_cold"],
        american_cols=["energy_demand"],
        bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
        drop_cols=["total_costs", "price_m2", "url", "general_description", "object_description", "place_description", "other_description", "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "agency_id", "id", "title", "available_from", "rent_deposit", "ad_type", "listing_type", "rent_extra_costs"],
        drop_missing=["estate_type", "price"],
        fill_none_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source", "internet_speed_telekom"],
    )

    df_houses_buy = data_cleaner_buy.filter_listing_types(df_houses, data_cleaner_buy.BUY_LISTING_TYPES)
    df_apartments_buy = data_cleaner_buy.filter_listing_types(df_apartments, data_cleaner_buy.BUY_LISTING_TYPES)

    df_apartments_buy = data_cleaner_buy.preprocessing(df_apartments_buy)
    df_houses_buy = data_cleaner_buy.preprocessing(df_houses_buy)

    df_buy = data_cleaner_buy.postprocessing(df_apartments_buy, df_houses_buy)
    data_cleaner_buy.store_in_db(df_buy)

    return df_buy


@step(experiment_tracker=experiment_tracker.name, enable_cache=False)
def train_buy_model(df_buy) -> TrainingRun:
    training = DataTraining(model, standardize_columns=STANDARDIZE_COLUMNS)

    output = training.train(df_buy, TARGET_COLUMN)

    active_run = mlflow.active_run()
    if active_run is None:
        raise RuntimeError("No active MLflow run found for the ZenML training step.")

    dataset = from_pandas( df_buy, name="clean_buy_training_dataset", targets=TARGET_COLUMN)
    mlflow.log_input(dataset, context="training")
    mlflow.log_param("training_rows", len(df_buy))
    mlflow.log_param("training_columns", len(df_buy.columns))

    metrics = get_training_metrics(output)
    if output.best_params:
        mlflow.log_params(output.best_params)

    if output.best_cv_score is not None:
        mlflow.log_metric("cv_mean_squared_error", output.best_cv_score)

    model_info = mlflow_sklearn.log_model(
        sk_model=output.model,
        name=MODEL_ARTIFACT_PATH,
        registered_model_name=MODEL_NAME,
        skops_trusted_types=SKOPS_TRUSTED_TYPES,
    )
    model_id = getattr(model_info, "model_id", None)
    if model_id is None:
        mlflow.log_metrics(metrics)
    else:
        mlflow.log_metrics(metrics, model_id=model_id)

    run_id = active_run.info.run_id
    registered_model_version = getattr(model_info, "registered_model_version", None)
    if registered_model_version is None:
        raise RuntimeError(f"Model was logged but not registered as '{MODEL_NAME}'.")

    return TrainingRun(
        mse=output.mse,
        r2=output.r2,
        training_mean_absolute_error=output.training_mean_absolute_error,
        training_mean_squared_error=output.training_mean_squared_error,
        training_root_mean_squared_error=output.training_root_mean_squared_error,
        training_r2_score=output.training_r2_score,
        run_id=run_id,
        model_uri=model_info.model_uri,
        registered_model_version=str(registered_model_version),
    )

@step(experiment_tracker=experiment_tracker.name, enable_cache=False)
def promote_buy_model(output: TrainingRun) -> PromotionResult:
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    client = MlflowClient()
    wait_until_model_ready(
        client=client,
        model_name=MODEL_NAME,
        version=output.registered_model_version,
    )
    client.set_model_version_tag(
        name=MODEL_NAME,
        version=output.registered_model_version,
        key=MSE_METRIC_NAME,
        value=str(output.mse),
    )
    client.set_model_version_tag(
        name=MODEL_NAME,
        version=output.registered_model_version,
        key=TRAINING_MSE_METRIC_NAME,
        value=str(output.training_mean_squared_error),
    )
    client.set_model_version_tag(
        name=MODEL_NAME,
        version=output.registered_model_version,
        key=TRAINING_MAE_METRIC_NAME,
        value=str(output.training_mean_absolute_error),
    )
    client.set_model_version_tag(
        name=MODEL_NAME,
        version=output.registered_model_version,
        key=TRAINING_RMSE_METRIC_NAME,
        value=str(output.training_root_mean_squared_error),
    )
    client.set_model_version_tag(
        name=MODEL_NAME,
        version=output.registered_model_version,
        key=TRAINING_R2_METRIC_NAME,
        value=str(output.training_r2_score),
    )

    client.set_model_version_tag(
        name=MODEL_NAME,
        version=output.registered_model_version,
        key=R2_METRIC_NAME,
        value=str(output.r2),
    )

    current_mse = float("inf")
    promotion_reason = "No current champion model found. Promoting current model."

    try:
        current_champion = client.get_model_version_by_alias(
            MODEL_NAME,
            PRODUCTION_ALIAS,
        )
        run_id = current_champion.run_id
        if run_id is None:
            raise ValueError("Current champion model has no run_id.")

        current_run = client.get_run(run_id)
        current_mse = current_run.data.metrics[MSE_METRIC_NAME]
        promotion_reason = (
            f"Candidate {MSE_METRIC_NAME} {output.mse} is lower than "
            f"champion {MSE_METRIC_NAME} {current_mse}."
        )
    except (MlflowException, KeyError, TypeError, ValueError):
        ml_pipeline_logger.exception(
            "No current champion model found or current champion could not be loaded. "
            "Promoting current model."
        )
        client.set_tag(output.run_id, "champion_lookup_status", "not_found_or_unavailable")

    if output.mse >= current_mse:
        client.set_tag(output.run_id, "promotion_status", "not_promoted")
        client.set_tag(
            output.run_id,
            "promotion_reason",
            f"{MSE_METRIC_NAME} {output.mse} >= champion {MSE_METRIC_NAME} {current_mse}",
        )
        return PromotionResult(
            promoted=False,
            candidate_mse=output.mse,
            current_champion_mse=current_mse,
            candidate_run_id=output.run_id,
            registered_model_version=output.registered_model_version,
        )

    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias=PRODUCTION_ALIAS,
        version=output.registered_model_version,
    )

    client.set_tag(output.run_id, "promotion_status", "promoted")
    client.set_tag(output.run_id, "production_alias", PRODUCTION_ALIAS)
    client.set_tag(output.run_id, "promotion_reason", promotion_reason)

    return PromotionResult(
        promoted=True,
        candidate_mse=output.mse,
        current_champion_mse=current_mse,
        candidate_run_id=output.run_id,
        registered_model_version=output.registered_model_version,
    )


@pipeline(enable_cache=False)
def ml_pipeline_zenml():
    try:
        data = load_data()

        #clean_rent_data(data)

        df_buy = clean_buy_data(data)
        output = train_buy_model(df_buy)
        promote_buy_model(output)
    except Exception as e:
        ml_pipeline_logger.error(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    ml_pipeline_zenml()
