from dataclasses import dataclass
import mlflow
from typing import Any
from dataclasses import dataclass
from sklearn.pipeline import Pipeline
from enum import StrEnum

def get_mlflow_tracking_uri(experiment_tracker) -> str:
    get_tracking_uri = getattr(experiment_tracker, "get_tracking_uri", None)
    if get_tracking_uri is None:
        raise RuntimeError(
            "The active ZenML experiment tracker is not an MLflow experiment tracker."
        )

    tracking_uri = get_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)
    return tracking_uri

class ModelType(StrEnum):
    LINEAR_REGRESSION = "LinearRegression"
    RANDOM_FOREST = "RandomForest"
    ADA_BOOST = "AdaBoost"
    XGB = "XGB"

@dataclass
class TrainingOutput:
    model: Pipeline
    mse: float
    r2: float
    training_mean_absolute_error: float
    training_mean_squared_error: float
    training_root_mean_squared_error: float
    training_r2_score: float
    x_train: Any
    x_test: Any
    y_train: Any
    y_test: Any
    y_pred: Any

@dataclass
class TrainingRun:
    mse: float
    r2: float
    training_mean_absolute_error: float
    training_mean_squared_error: float
    training_root_mean_squared_error: float
    training_r2_score: float
    run_id: str
    model_uri: str
    registered_model_version: str


@dataclass
class PromotionResult:
    promoted: bool
    candidate_mse: float
    current_champion_mse: float
    candidate_run_id: str
    registered_model_version: str | None = None
