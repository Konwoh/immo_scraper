from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, cast

import pandas as pd
from sqlalchemy.engine import Engine
from backend.ml.preprocessing.data_cleaner import DataCleaner

PREDICTION_FEATURE_COLUMNS: tuple[str, ...] = (
    "estate_type",
    "rent_cold",
    "rent_complete",
    "house_money",
    "rent_heating_costs",
    "zip_code",
    "rooms",
    "sleeping_rooms",
    "bathrooms",
    "floor",
    "living_space",
    "garage_parking_slots",
    "lift",
    "barrier_free",
    "garden",
    "internet_speed_telekom",
    "fitted_kitchen",
    "basement",
    "rented",
    "provision",
    "rent_income",
    "building_year",
    "estate_condition",
    "interior_quality",
    "heating_type",
    "energy_performance_certificate_type",
    "energy_source",
    "energy_demand",
    "energy_efficiency_class",
    "is_online",
    "property_space",
)

NUMERIC_COLUMNS: tuple[str, ...] = (
    "rent_cold",
    "rent_complete",
    "house_money",
    "rooms",
    "sleeping_rooms",
    "bathrooms",
    "floor",
    "living_space",
    "garage_parking_slots",
    "internet_speed_telekom",
    "rent_income",
    "building_year",
    "energy_demand",
    "property_space",
)

BOOLEAN_COLUMNS: tuple[str, ...] = (
    "lift",
    "barrier_free",
    "garden",
    "fitted_kitchen",
    "basement",
    "rented",
    "is_online",
)

CATEGORICAL_COLUMNS: tuple[str, ...] = tuple(
    column
    for column in PREDICTION_FEATURE_COLUMNS
    if column not in NUMERIC_COLUMNS and column not in BOOLEAN_COLUMNS
)

TRUE_VALUES = {"true", "1", "yes", "y", "ja", "j", "wahr"}
FALSE_VALUES = {"false", "0", "no", "n", "nein", "falsch"}


class PredictionCleaner:
    def __init__(
        self,
        feature_columns: Sequence[str] = PREDICTION_FEATURE_COLUMNS,
        numeric_defaults: Mapping[str, float] | None = None,
        categorical_default: str = "Missing",
    ) -> None:
        self.feature_columns = tuple(feature_columns)
        self.numeric_defaults = dict(numeric_defaults or {})
        self.categorical_default = categorical_default
        self.data_cleaner = DataCleaner(engine=cast(Engine, None))

    def prepare(self, data: pd.DataFrame | Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> pd.DataFrame:
        df = self._to_dataframe(data)
        df = self._ensure_feature_columns(df)
        df = self._normalize_special_columns(df)
        df = self._convert_types(df)
        df = self._fill_missing_values(df)

        return df.loc[:, list(self.feature_columns)]

    def _to_dataframe(
        self,
        data: pd.DataFrame | Mapping[str, Any] | Iterable[Mapping[str, Any]],
    ) -> pd.DataFrame:
        if isinstance(data, pd.DataFrame):
            return data.copy()

        if isinstance(data, Mapping):
            return pd.DataFrame([data])

        return pd.DataFrame(list(data))

    def _ensure_feature_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for column in self.feature_columns:
            if column not in df.columns:
                df[column] = pd.NA

        return df

    def _normalize_special_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "energy_efficiency_class" in df.columns:
            df["energy_efficiency_class"] = df["energy_efficiency_class"].map(
                self.data_cleaner._transform_efficiency_class
            )

        return df

    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "floor" in df.columns:
            df["floor"] = df["floor"].map(self._floor_to_numeric_or_none)

        if "building_year" in df.columns:
            df["building_year"] = df["building_year"].map(self._building_year_to_numeric_or_none)

        for column in NUMERIC_COLUMNS:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column].map(self._to_numeric), errors="coerce")

        for column in BOOLEAN_COLUMNS:
            if column in df.columns:
                df[column] = df[column].map(self._to_bool).astype("boolean")

        return df

    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "rent_cold" in df.columns and "rent_complete" in df.columns:
            df["rent_cold"] = df["rent_cold"].fillna(df["rent_complete"] * 0.75)

        for column in NUMERIC_COLUMNS:
            if column in df.columns:
                df[column] = df[column].fillna(self.numeric_defaults.get(column, 0.0))

        for column in BOOLEAN_COLUMNS:
            if column in df.columns:
                df[column] = df[column].fillna(False)

        for column in CATEGORICAL_COLUMNS:
            if column in df.columns:
                df[column] = df[column].fillna(self.categorical_default)

        return df

    def _to_numeric(self, value: Any) -> float | None:
        if pd.isna(value):
            return None

        if isinstance(value, str):
            value = value.strip()

            if not value or value == "Auf Anfrage":
                return None

            value = value.replace("EUR", "\u20ac").replace("Euro", "\u20ac")

        try:
            numeric_value = self.data_cleaner._str_to_numeric(value)
        except (TypeError, ValueError):
            return None

        if numeric_value is None:
            return None

        return float(numeric_value)

    def _floor_to_numeric_or_none(self, value: Any) -> float | None:
        try:
            return self.data_cleaner._floor_to_numeric(value)
        except (TypeError, ValueError):
            return None

    def _building_year_to_numeric_or_none(self, value: Any) -> float | None:
        try:
            return self.data_cleaner._building_year_to_numeric(value)
        except (TypeError, ValueError):
            return None

    def _to_bool(self, value: Any) -> bool | None:
        if pd.isna(value):
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        if isinstance(value, str):
            normalized_value = value.strip().lower()

            if normalized_value in TRUE_VALUES:
                return True

            if normalized_value in FALSE_VALUES:
                return False

        return None


def prepare_prediction_dataset(
    data: pd.DataFrame | Mapping[str, Any] | Iterable[Mapping[str, Any]],
    feature_columns: Sequence[str] = PREDICTION_FEATURE_COLUMNS,
) -> pd.DataFrame:
    return PredictionCleaner(feature_columns=feature_columns).prepare(data)
