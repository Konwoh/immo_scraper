import os
from typing import Any
from backend.parser.factory import EstateParserCreator
import mlflow
from fastapi import APIRouter, Body, HTTPException, status
from mlflow.exceptions import MlflowException
from backend.ml.preprocessing.prediction_cleaner import PredictionCleaner, prepare_prediction_dataset
from backend.shared.helper import get_model_feature_columns
from backend.schemas.predict import PredictionPayload, PredictionResponse
import mlflow.sklearn as mlflow_sklearn

router = APIRouter(
    prefix="/predict",
    tags=["Price Prediction"]
)

prediction_cleaner = PredictionCleaner()

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

@router.post("/", status_code=status.HTTP_200_OK, response_model=PredictionResponse)
def predict_price(payload: dict[str, Any] = Body(...)) -> PredictionResponse:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MLFLOW_TRACKING_URI is not configured.",
        )

    mlflow.set_tracking_uri(tracking_uri)

    try:
        loaded_model = mlflow_sklearn.load_model("models:/RandomForest@champion")
    except MlflowException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not load prediction model: {exc}",
        ) from exc

    if loaded_model is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction model could not be loaded.",
        )

    feature_columns = get_model_feature_columns(loaded_model)

    try:
        df_features = prepare_prediction_dataset(
            payload,
            feature_columns=feature_columns,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not prepare prediction features: {exc}",
        ) from exc

    predictions = loaded_model.predict(df_features)
    return PredictionResponse(predicted_price=float(predictions[0]))

@router.post("/get_prediction_payload", status_code=status.HTTP_200_OK, response_model=PredictionPayload)
def get_prediction_payload(url: str) -> PredictionPayload:
    try: 
        if "immobilienscout24" in url:
            parser = EstateParserCreator().create_parser("immoScout")
        elif "kleinanzeigen" in url:
            parser = EstateParserCreator().create_parser("kleinanzeigen")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported URL. Only ImmoScout and Kleinanzeigen URLs are supported.",
            )
        
        estate = parser.build_estate(url)
        return estate_to_prediction_payload(estate)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not build prediction payload from URL: {e}",
        ) from e
