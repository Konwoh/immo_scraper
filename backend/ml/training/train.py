from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from  xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
from enum import StrEnum
from typing import Any
from dataclasses import dataclass

class ModelType(StrEnum):
    LINEAR_REGRESSION = "LinearRegression"
    RANDOM_FOREST = "RandomForest"
    ADA_BOOST = "AdaBoost"
    XGB = "XGB"
    
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
            case ModelType.ADA_BOOST:
                return XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
            case _:
                raise ValueError("Unknown ML Model")
@dataclass
class TrainingOutput:
    model: LinearRegression | RandomForestRegressor | AdaBoostRegressor | XGBRegressor
    mse: float
    r2: float
    x_train: Any
    x_test: Any
    y_train: Any
    y_test: Any
    y_pred: Any

class DataTraining:
    def __init__(self, model):
        self.model = model
    
    def train(self, df, target_col):
        ml_model = self.model.create_model()
        X = df.drop(labels=target_col, axis=1)
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
        ml_model.fit(X=X_train, y=y_train)
        y_pred = ml_model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        return TrainingOutput(ml_model, mse, r2, X_train, X_test, y_train, y_test, y_pred)
