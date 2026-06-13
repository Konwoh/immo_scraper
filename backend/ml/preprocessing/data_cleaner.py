from datetime import datetime
import pandas as pd
import re
from typing import Callable, List
import logging
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

data_cleaner_logger = logging.getLogger("ML_data_cleaner")
engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)


FillStrategy = Callable[[pd.DataFrame, str], pd.Series]

class DataCleaner:
    DEFAULT_FILL_STRATEGIES: dict[str, FillStrategy] = {
        "available_from": lambda df, col: df[col].fillna(datetime.now()),
        "garage_parking_slots": lambda df, col: df[col].fillna(0),
        "total_costs": lambda df, col: df[col].fillna(df[col].mean()),
        "building_year": lambda df, col: df[col].fillna(df[col].mean()),
        "house_money": lambda df, col: df[col].fillna(df[col].mean()),
        "sleeping_rooms": lambda df, col: df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 1),
        "bathrooms": lambda df, col: df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 1),
        "floor": lambda df, col: df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 0),
        "energy_source": lambda df, col: df[col].fillna("Keine Angabe"),
        "rent_cold": lambda df, col: df[col].fillna(df["rent_complete"] * 0.75),
        "price": lambda df, col: df[col].fillna(df[col].mean()),
        "internet_speed_telekom": lambda df, col: df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 0)
    }
    
    MAPPING_DICT = { 
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/A-plus.png": "A+",
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/A.png" : "A",
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/B.png": "B",
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/C.png": "C",
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/D.png": "D",
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/E.png": "E",
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/F.png": "F",
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/G.png": "G",
        "https://is24-search-static.s3-eu-west-1.amazonaws.com/mobile-feed/energy-efficiency-labels/H.png": "H"
    }

    def __init__(
        self,
        american_cols: List[str] | None = None,
        numeric_cols: List[str] | None = None,
        date_cols: List[str] | None = None,
        drop_cols: List[str] | None = None,
        drop_missing: List[str] | None = None,
        bool_cols: List[str] | None = None,
        fill_none_cols: List[str] | None = None,
        fill_strategies: dict[str, FillStrategy] | None = None,
        mapping_dict: dict[str, str] | None = None
    ):
        self.american_cols  = list(american_cols or [])
        self.numeric_cols   = list(numeric_cols or [])
        self.date_cols      = list(date_cols or [])
        self.drop_cols      = list(drop_cols or [])
        self.bool_cols      = list(bool_cols or [])
        self.fill_none_cols = list(fill_none_cols or [])
        self.drop_missing   = list(drop_missing or [])
        self.fill_strategies = {
            **self.DEFAULT_FILL_STRATEGIES,
            **(fill_strategies or {}),
        }
        self.mapping_dict = {
            **self.MAPPING_DICT,
            **(mapping_dict or {})
        }
    
    # ----------------
    # Type Conversion
    # ----------------
    def _to_bool(self, df: pd.DataFrame, bool_cols: List[str]) -> pd.DataFrame:
        df = df.copy()

        for col in bool_cols:
            df[col] = df[col].astype('boolean')

        return df

    def _str_to_numeric(self, value):
        if pd.isna(value):
            return None
        if value == "Auf Anfrage":
            return None
        if isinstance(value, str) and ('€' in value or 'm²' in value or '%' in value or 'MBit/s' in value):
            return float(value.replace("\xa0", " ").replace(".", "").replace(",", ".").split(" ")[0])
        return float(value)

    def _floor_to_numeric(self, value):
        if pd.isna(value):
            return None
        if isinstance(value, str):
            if "von" in value:
                return float(value.split(" ")[0])
            else:
                return float(value)
        return float(value)

    def _building_year_to_numeric(self, value):
        if isinstance(value, str):
            if value.lower() == "unbekannt":
                return None
            return datetime.strptime(value, "%Y").year
        return value

    # ----------------
    # Date Handling
    # ----------------
    def _us_to_european(self, value):
        if isinstance(value, str):
            return value.replace(".", ",")
        return value
    
    def _detect_date_format(self, date_string):
        formats = [
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%Y-%m",
            "%Y",
            "%B %Y"
        ]

        if re.fullmatch(r"^(Winter|Sommer|Herbst|Frühling)\s\d{4}$", date_string):
            year = date_string.split(" ")[1]
            season = date_string.split(" ")[0]
            
            match season:
                case "Frühling":
                    return datetime.strptime(f"01.03.{year}", "%d.%m.%Y")
                case "Sommer":
                    return datetime.strptime(f"01.06.{year}", "%d.%m.%Y")
                case "Winter":
                    return datetime.strptime(f"01.12.{year}", "%d.%m.%Y")
                case "Herbst":
                    return datetime.strptime(f"01.09.{year}", "%d.%m.%Y")


        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
            except TypeError:
                continue
                    

        return None

    def _str_to_date(self, value):
        if pd.isna(value):
            return None

        if isinstance(value, str):
            if value.lower() in ["sofort", "sofort bezugsfertig", "ab sofort"]:
                return datetime.now()
            return self._detect_date_format(value)

        return value  
    # ----------------
    # Feature Mapping
    # ----------------
    def _transform_efficiency_class(self, value):
        
        if pd.isna(value):
            return None

        return self.mapping_dict.get(value, value)

    # ----------------
    # Missing Values
    # ----------------
    def _fill_none_values(self, df, fill_none_cols):
        df = df.copy()

        for col in fill_none_cols:
            if col not in df.columns:
                continue
            if col == "living_space":
                df = df.dropna(subset=[col])
            elif col in self.fill_strategies:
                df[col] = self.fill_strategies[col](df, col)
            elif df[col].dtype == "boolean":
                df[col] = df[col].fillna(False)
            elif df[col].nunique(dropna=True) <= 10 and df[col].notna().mean() > 0.25:
                df[col] = df[col].fillna(df[col].mode().iloc[0])

        return df
    
    def _drop_missing_values(self, df: pd.DataFrame, cols):
        return df.dropna(subset=cols)
    # ----------------
    # Column Operations
    # ----------------
    def _drop_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.drop(columns=self.drop_cols, errors="ignore")

        cols_to_drop = [
            col for col in df.columns
            if df[col].notna().sum() < 0.5 * len(df)
        ]

        df = df.drop(columns=cols_to_drop)
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame):
        numeric_cols = df.select_dtypes("float").columns
        for col in numeric_cols:
            lower_limit = df[col].quantile(0.01)
            upper_limit = df[col].quantile(0.99)

            outliers_low = df[col] < lower_limit
            outliers_high = df[col] > upper_limit
            
            keep_rows = (
                df[col].between(outliers_low, outliers_high)
                | df[col].isna()
            )

            df = df.loc[keep_rows]
            
        return df
    
    # ----------------
    # Main Pipeline
    # ----------------
    def preprocessing(self, df: pd.DataFrame) -> pd.DataFrame|None:
        try:
            df = df.copy()
            df = df[df["ad_type"] == "OFFERED"]
            
            df = self._to_bool(df, self.bool_cols)

            if "floor" in df.columns:
                df["floor"] = df["floor"].apply(self._floor_to_numeric)
            
            if "building_year" in df.columns:
                df["building_year"] = df["building_year"].apply(self._building_year_to_numeric)

            if "energy_efficiency_class" in df.columns:
                df["energy_efficiency_class"] = df["energy_efficiency_class"].apply(self._transform_efficiency_class)


            for col in self.american_cols:
                if col in df.columns:
                    df[col] = df[col].apply(self._us_to_european)
            
            for col in self.numeric_cols:
                if col in df.columns:
                    df[col] = df[col].apply(self._str_to_numeric)
            
            for col in self.date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col].apply(self._str_to_date), dayfirst=True)

            #fill_none_cols = self.bool_cols + ["available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "sleeping_rooms", "house_money", "bathrooms", "floor"]
            if self.fill_none_cols:
                df = self._fill_none_values(df, self.fill_none_cols)

            df = self._drop_columns(df)
            df = self._drop_missing_values(df, self.drop_missing)
            df = self._remove_outliers(df)
            
            return df
        
        except Exception as e:
            data_cleaner_logger.exception(f"Fehler beim Data Cleaning: {str(e)}")
            raise
    
    def store_in_db(self, db: pd.DataFrame) -> int|None:
        return db.to_sql(name="ml_training", con=engine, if_exists="replace")
