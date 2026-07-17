from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
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
    model = mlflow_sklearn.load_model("models:/RandomForest@champion")
    feature_columns = get_model_feature_columns(model)

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

    predictions = model.predict(df_features)
    return PredictionResponse(predicted_price=float(predictions[0]))
