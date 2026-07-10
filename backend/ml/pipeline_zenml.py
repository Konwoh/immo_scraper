import os
import time
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from zenml import pipeline, step
from zenml.client import Client
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from backend.ml.preprocessing.data_cleaner import DataCleaner
from backend.ml.preprocessing.data_loader import DataLoader
from backend.ml.training.train import DataTraining, MLModelFactory, ModelType
from backend.ml.utils import TrainingRun, PromotionResult, get_mlflow_tracking_uri
import mlflow
import mlflow.sklearn as mlflow_sklearn
load_dotenv()

ml_pipeline_logger = logging.getLogger("ML_pipeline")
experiment_tracker = Client().active_stack.experiment_tracker

if experiment_tracker is None:
    raise RuntimeError("The active ZenML stack has no experiment tracker configured.")

MODEL_NAME = "immo_scraper"
PRODUCTION_ALIAS = "champion"
MODEL_ARTIFACT_PATH = "model"
MSE_METRIC_NAME = "mean_squared_error"
R2_METRIC_NAME = "r2_score"
STANDARDIZE_COLUMNS = [
    "house_money",
    "living_space",
    "internet_speed_telekom",
    "building_year",
    "property_space",
]

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
    model = MLModelFactory(ModelType.LINEAR_REGRESSION)
    training = DataTraining(model, standardize_columns=STANDARDIZE_COLUMNS)

    output = training.train(df_buy, "price")

    active_run = mlflow.active_run()
    if active_run is None:
        raise RuntimeError("No active MLflow run found for the ZenML training step.")

    mlflow.log_metric(MSE_METRIC_NAME, output.mse)
    mlflow.log_metric(R2_METRIC_NAME, output.r2)
    model_info = mlflow_sklearn.log_model(
        sk_model=output.model,
        artifact_path=MODEL_ARTIFACT_PATH,
        registered_model_name=MODEL_NAME,
    )

    run_id = active_run.info.run_id
    registered_model_version = getattr(model_info, "registered_model_version", None)
    if registered_model_version is None:
        raise RuntimeError(f"Model was logged but not registered as '{MODEL_NAME}'.")

    return TrainingRun(
        mse=output.mse,
        r2=output.r2,
        run_id=run_id,
        model_uri=model_info.model_uri,
        registered_model_version=str(registered_model_version),
    )

def wait_until_model_ready(
    client: MlflowClient,
    model_name: str,
    version: str,
    timeout_seconds: int = 60,
) -> None:
    start = time.time()

    while time.time() - start < timeout_seconds:
        model_version = client.get_model_version(model_name, version)

        if model_version.status == "READY":
            return

        if "FAILED" in model_version.status:
            raise RuntimeError(
                f"Model registration failed: {model_version.status_message}"
            )

        time.sleep(2)

    raise TimeoutError(f"Model version {version} was not ready in time.")


@step(experiment_tracker=experiment_tracker.name, enable_cache=False)
def promote_buy_model(output: TrainingRun) -> PromotionResult:
    tracking_uri = get_mlflow_tracking_uri(experiment_tracker)
    client = MlflowClient(tracking_uri=tracking_uri)
    wait_until_model_ready(
        client=client,
        model_name=MODEL_NAME,
        version=output.registered_model_version,
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
    data = load_data()

    #clean_rent_data(data)

    df_buy = clean_buy_data(data)
    output = train_buy_model(df_buy)
    promote_buy_model(output)


if __name__ == "__main__":
    ml_pipeline_zenml()
