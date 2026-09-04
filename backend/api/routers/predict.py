import os
from functools import lru_cache
from typing import Any
from urllib.parse import urlparse

import mlflow
import mlflow.sklearn as mlflow_sklearn
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Request, status
from mlflow.exceptions import MlflowException

from backend.database.models import User
from backend.api.auth.oauth2 import get_current_user
from backend.api.rate_limit import limiter
from backend.parser.factory import EstateParserCreator
from backend.ml.preprocessing.prediction_cleaner import PredictionCleaner, prepare_prediction_dataset
from backend.schemas.predict import PredictionPayload, PredictionResponse
from backend.shared.helper import get_model_feature_columns
from backend.shared.loki_handler import get_loki_logger

router = APIRouter(
    prefix="/predict",
    tags=["Price Prediction"]
)

predict_logger = get_loki_logger("predict", {"app": "api", "env": os.getenv("ENV", "dev")})

prediction_cleaner = PredictionCleaner()

# Host allowlist for get_prediction_payload: keyed on the exact hostname (not a
# substring match), value is the parser key expected by EstateParserCreator.
ALLOWED_ESTATE_HOSTS = {
    "www.immobilienscout24.de": "immoScout",
    "immobilienscout24.de": "immoScout",
    "www.kleinanzeigen.de": "kleinanzeigen",
    "kleinanzeigen.de": "kleinanzeigen",
}

def estate_to_prediction_payload(estate: Any) -> PredictionPayload:
    is_online = getattr(estate, "is_online", None)
    building_year = prediction_cleaner._building_year_to_numeric_or_none(
        getattr(estate, "building_year", None)
    )

    return PredictionPayload(
        estate_type=getattr(estate, "estate_type", None),
        rent_cold=prediction_cleaner._to_numeric(getattr(estate, "rent_cold", None)),
        rent_complete=prediction_cleaner._to_numeric(getattr(estate, "rent_complete", None)),
        house_money=prediction_cleaner._to_numeric(getattr(estate, "house_money", None)),
        rent_heating_costs=prediction_cleaner._to_numeric(getattr(estate, "rent_heating_costs", None)),
        zip_code=getattr(estate, "zip_code", None),
        rooms=prediction_cleaner._to_numeric(getattr(estate, "rooms", None)),
        sleeping_rooms=prediction_cleaner._to_numeric(getattr(estate, "sleeping_rooms", None)),
        bathrooms=prediction_cleaner._to_numeric(getattr(estate, "bathrooms", None)),
        floor=prediction_cleaner._floor_to_numeric_or_none(getattr(estate, "floor", None)),
        living_space=prediction_cleaner._to_numeric(getattr(estate, "living_space", None)),
        garage_parking_slots=prediction_cleaner._to_numeric(getattr(estate, "garage_parking_slots", None)),
        lift=getattr(estate, "lift", None),
        barrier_free=getattr(estate, "barrier_free", None),
        garden=getattr(estate, "garden", None),
        internet_speed_telekom=prediction_cleaner._to_numeric(getattr(estate, "internet_speed_telekom", None)),
        fitted_kitchen=getattr(estate, "fitted_kitchen", None),
        basement=getattr(estate, "basement", None),
        rented=getattr(estate, "rented", None),
        provision=getattr(estate, "provision", None),
        rent_income=prediction_cleaner._to_numeric(getattr(estate, "rent_income", None)),
        building_year=float(building_year) if building_year is not None else None,
        estate_condition=getattr(estate, "estate_condition", None),
        interior_quality=getattr(estate, "interior_quality", None),
        heating_type=getattr(estate, "heating_type", None),
        energy_performance_certificate_type=getattr(estate, "energy_performance_certificate_type", None),
        energy_source=getattr(estate, "energy_source", None),
        energy_demand=prediction_cleaner._to_numeric(getattr(estate, "energy_demand", None)),
        energy_efficiency_class=prediction_cleaner.data_cleaner._transform_efficiency_class(
            getattr(estate, "energy_efficiency_class", None)
        ),
        is_online=True if is_online is None else is_online,
        property_space=prediction_cleaner._to_numeric(getattr(estate, "property_space", None)),
    )

@lru_cache(maxsize=1)
def _load_champion_models(tracking_uri: str) -> tuple[Any, Any, Any]:
    """Load the champion models once per API process and reuse them.

    Cached for the lifetime of the process (keyed on tracking_uri, which is
    effectively constant) so a request no longer re-downloads all three
    models from MLflow/S3 on every call. A newly promoted @champion model
    only takes effect after the API process restarts. A failed load is not
    cached, so the next request retries.
    """
    mlflow.set_tracking_uri(tracking_uri)
    return (
        mlflow_sklearn.load_model("models:/RandomForest@champion"),
        mlflow_sklearn.load_model("models:/AdaBoost@champion"),
        mlflow_sklearn.load_model("models:/XGB@champion"),
    )

@router.post("/", status_code=status.HTTP_200_OK, response_model=PredictionResponse)
@limiter.limit("20/minute")
def predict_price(
    request: Request,
    payload: PredictionPayload,
    current_user: User = Depends(get_current_user),
) -> PredictionResponse:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MLFLOW_TRACKING_URI is not configured.",
        )

    try:
        loaded_model_rf, loaded_model_ada, loaded_model_xgb = _load_champion_models(tracking_uri)
    except MlflowException as exc:
        predict_logger.error("Could not load prediction models: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction models are currently unavailable.",
        ) from exc

    feature_columns_rf = get_model_feature_columns(loaded_model_rf)
    feature_columns_ada = get_model_feature_columns(loaded_model_ada)
    feature_columns_xgb = get_model_feature_columns(loaded_model_xgb)

    payload_dict = payload.model_dump()

    try:
        df_features_rf = prepare_prediction_dataset(payload_dict, feature_columns=feature_columns_rf)
        df_features_ada = prepare_prediction_dataset(payload_dict, feature_columns=feature_columns_ada)
        df_features_xbg = prepare_prediction_dataset(payload_dict, feature_columns=feature_columns_xgb)
    except (KeyError, TypeError, ValueError) as exc:
        predict_logger.error("Could not prepare prediction features: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not prepare prediction features from the given payload.",
        ) from exc

    prediction_list = []
    prediction_rf = loaded_model_rf.predict(df_features_rf)[0]
    prediction_ada = loaded_model_ada.predict(df_features_ada)[0]
    prediction_xgb = loaded_model_xgb.predict(df_features_xbg)[0]
    prediction_list.extend([prediction_rf, prediction_ada, prediction_xgb])

    return PredictionResponse(
            predicted_price_all=float(np.mean(prediction_list)),
            predicted_price_rf=prediction_rf,
            predicted_price_xgb=prediction_xgb,
            predicted_price_ada=prediction_ada
           )

@router.post("/get_prediction_payload", status_code=status.HTTP_200_OK, response_model=PredictionPayload)
@limiter.limit("20/minute")
def get_prediction_payload(
    request: Request,
    url: str,
    current_user: User = Depends(get_current_user),
) -> PredictionPayload:
    hostname = (urlparse(url).hostname or "").lower()
    parser_key = ALLOWED_ESTATE_HOSTS.get(hostname)

    if parser_key is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported URL. Only ImmoScout and Kleinanzeigen URLs are supported.",
        )

    try:
        parser = EstateParserCreator().create_parser(parser_key)
        estate = parser.build_estate(url)
        return estate_to_prediction_payload(estate)
    except HTTPException:
        raise
    except Exception as exc:
        predict_logger.error("Could not build prediction payload from url=%s: %s", url, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not build prediction payload from the given URL.",
        ) from exc
