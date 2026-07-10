from dataclasses import dataclass
import mlflow

def get_mlflow_tracking_uri(experiment_tracker) -> str:
    get_tracking_uri = getattr(experiment_tracker, "get_tracking_uri", None)
    if get_tracking_uri is None:
        raise RuntimeError(
            "The active ZenML experiment tracker is not an MLflow experiment tracker."
        )

    tracking_uri = get_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)
    return tracking_uri


@dataclass
class TrainingRun:
    mse: float
    r2: float
    run_id: str
    model_uri: str


@dataclass
class PromotionResult:
    promoted: bool
    candidate_mse: float
    current_champion_mse: float
    candidate_run_id: str
    registered_model_version: str | None = None