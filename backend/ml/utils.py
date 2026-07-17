from dataclasses import dataclass
from typing import Any
from sklearn.pipeline import Pipeline
from enum import StrEnum
from mlflow import MlflowClient
import time

def prefix_model_params(param_grid: dict) -> dict:
    return {
        f"model__{key}": value
        for key, value in param_grid.items()
    }

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
    best_params: dict[str, Any] | None = None
    best_cv_score: float | None = None

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
    candidate_r2: float
    current_champion_r2: float
    candidate_run_id: str
    registered_model_version: str | None = None
