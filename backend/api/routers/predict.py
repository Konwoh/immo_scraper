import os
from typing import Any, Protocol, cast

import mlflow
from fastapi import APIRouter, Body, HTTPException, status
from mlflow.exceptions import MlflowException
from backend.ml.preprocessing.prediction_cleaner import prepare_prediction_dataset
from backend.shared.helper import get_model_feature_columns
from backend.schemas.predict import PredictionResponse
import mlflow.sklearn as mlflow_sklearn

router = APIRouter(
    prefix="/predict",
    tags=["Price Prediction"]
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
