from backend.ml.preprocessing.data_cleaner import DataCleaner
from backend.ml.preprocessing.feature_engineering import FeatureEngineering
import pandas as pd
from pathlib import Path

csv_path = Path(__file__).with_name("apartments.csv")
df = pd.read_csv(csv_path, delimiter=",", dtype={"zip_code": str})

feature_engineer = FeatureEngineering()

data_cleaner = DataCleaner(
    numeric_cols=["living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money"],
    american_cols=["energy_demand"],
    bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
    drop_cols=["url", 'general_description', 'object_description', 'place_description', 'other_description', "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "price", "price_m2", "agency_id", "id", "title", "available_from"],
    fill_none_cols = ["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source"],
)

df = data_cleaner.preprocessing(df)

if isinstance(df, pd.DataFrame):
    df = feature_engineer.one_hot_encoding(df)

    print(df.head())
    print(df.info(verbose=True))
    print(df.describe())
