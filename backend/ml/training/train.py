from __future__ import annotations
from typing import cast

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor
import numpy as np
from backend.ml.utils import ModelType, TrainingOutput, prefix_model_params
import pandas as pd
from xgboost import XGBRegressor

PARAM_GRID_RF = { 'n_estimators': np.arange(50, 300, 50), 'max_depth': [None, 10, 20, 30], 'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4], 'bootstrap': [True, False]}
PARAM_GRID_AB = { "n_estimators": [50, 100, 200], "learning_rate": [0.01, 0.05, 0.1, 0.5, 1.0], "loss": ["linear", "square"], "estimator__max_depth": [2, 3, 4], "estimator__min_samples_leaf": [1, 5, 10],}
PARAM_GRID_XGB = { "n_estimators": [100, 300, 500], "learning_rate": [0.01, 0.05, 0.1], "max_depth": [3, 5, 7], "subsample": [0.8, 1.0], "colsample_bytree": [0.8, 1.0], "reg_lambda": [1, 5, 10],}

class MLModelFactory:
    def __init__(self, model: ModelType):
        self.model = model
    
    def create_model(self):
        match self.model:
            case ModelType.LINEAR_REGRESSION:
                return LinearRegression()
            case ModelType.RANDOM_FOREST:
                return RandomForestRegressor(random_state=42)
            case ModelType.ADA_BOOST:
                return AdaBoostRegressor(
                    estimator=DecisionTreeRegressor(random_state=42),
                    random_state=42,
                )
            case ModelType.XGB:
                return XGBRegressor(objective='reg:squarederror', random_state=42)
            case _:
                raise ValueError("Unknown ML Model")

    def get_param_distributions(self) -> dict:
        match self.model:
            case ModelType.RANDOM_FOREST:
                return prefix_model_params(PARAM_GRID_RF)
            case ModelType.ADA_BOOST:
                return prefix_model_params(PARAM_GRID_AB)
            case ModelType.XGB:
                return prefix_model_params(PARAM_GRID_XGB)
            case ModelType.LINEAR_REGRESSION:
                return {}
            case _:
                raise ValueError("Unknown ML Model")

class DataTraining:
    def __init__(self, model: MLModelFactory, standardize_columns: list[str] | None = None):
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
    
    def train(self, df: pd.DataFrame, target_col: str):
        df = df.dropna(subset=[target_col])
        X = df.drop(labels=target_col, axis=1)
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

        pipeline = self._build_pipeline(X_train)
        param_distributions = self.model.get_param_distributions()

        if param_distributions:
            search = RandomizedSearchCV(
                estimator=pipeline,
                param_distributions=param_distributions,
                n_iter=30,
                scoring="neg_mean_squared_error",
                cv=5,
                random_state=42,
                n_jobs=-1,
                refit=True,
            )

            search.fit(X=X_train, y=y_train)
            ml_model: Pipeline = cast(Pipeline, search.best_estimator_)
            best_params = search.best_params_
            best_cv_score = float(-search.best_score_)
        else:
            ml_model = pipeline
            ml_model.fit(X=X_train, y=y_train)
            best_params = {}
            best_cv_score = None

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
            best_params=best_params,
            best_cv_score=best_cv_score,
        )
