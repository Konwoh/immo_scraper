from __future__ import annotations

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
import numpy as np
from xgboost import XGBRegressor
from backend.ml.utils import ModelType, TrainingOutput
    
class MLModelFactory:
    def __init__(self, model: ModelType):
        self.model = model
    
    def create_model(self) -> LinearRegression | RandomForestRegressor | AdaBoostRegressor | XGBRegressor:
        match self.model:
            case ModelType.LINEAR_REGRESSION:
                return LinearRegression()
            case ModelType.RANDOM_FOREST:
                return RandomForestRegressor()
            case ModelType.ADA_BOOST:
                return AdaBoostRegressor()
            case ModelType.XGB:
                if XGBRegressor is None:
                    raise ImportError("xgboost is required to train an XGB model.")
                return XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
            case _:
                raise ValueError("Unknown ML Model")

class DataTraining:
    def __init__(self, model, standardize_columns: list[str] | None = None):
        self.model = model
        self.standardize_columns = standardize_columns or []

    def _build_pipeline(self, X) -> Pipeline:
        categorical_columns = list(X.select_dtypes(include=["object", "string", "category"]).columns)
        standardize_columns = [
            column
            for column in self.standardize_columns
            if column in X.columns
        ]

        transformers = []

        if standardize_columns:
            transformers.append(
                (
                    "log_standardized_numeric",
                    Pipeline(
                        steps=[
                            ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    standardize_columns,
                )
            )

        if categorical_columns:
            transformers.append(
                (
                    "categorical",
                    OneHotEncoder(
                        sparse_output=False,
                        min_frequency=20,
                        handle_unknown="infrequent_if_exist",
                    ),
                    categorical_columns,
                )
            )

        preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder="passthrough",
            verbose_feature_names_out=False,
        )

        return Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", self.model.create_model()),
            ]
        )
    
    def train(self, df, target_col):
        df = df.dropna(subset=[target_col])
        X = df.drop(labels=target_col, axis=1)
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
        ml_model = self._build_pipeline(X_train)
        ml_model.fit(X=X_train, y=y_train)
        y_train_pred = ml_model.predict(X_train)
        y_pred = ml_model.predict(X_test)
        training_mean_squared_error = float(mean_squared_error(y_train, y_train_pred))
        mse = float(mean_squared_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))
        return TrainingOutput(
            model=ml_model,
            mse=mse,
            r2=r2,
            training_mean_absolute_error=float(mean_absolute_error(y_train, y_train_pred)),
            training_mean_squared_error=training_mean_squared_error,
            training_root_mean_squared_error=float(np.sqrt(training_mean_squared_error)),
            training_r2_score=float(r2_score(y_train, y_train_pred)),
            x_train=X_train,
            x_test=X_test,
            y_train=y_train,
            y_test=y_test,
            y_pred=y_pred,
        )
