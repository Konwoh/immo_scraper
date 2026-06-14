from backend.ml.preprocessing.data_cleaner import DataCleaner
from backend.ml.preprocessing.data_loader import DataLoader
from backend.ml.preprocessing.feature_engineering import FeatureEngineering
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)

data_loader = DataLoader(engine)

df_apartments = data_loader.load_from_db(estate="apartments")
df_houses = data_loader.load_from_db(estate="houses")

df_houses_rent = df_houses[df_houses["listing_type"].isin(["Mietwohnungen", "wohnung_miete", "haus_miete"])]
df_houses_buy = df_houses[df_houses["listing_type"].isin(["Eigentumswohnungen", "wohnung_kauf", "haus_kauf"])]
df_apartments_rent = df_apartments[df_apartments["listing_type"].isin(["Mietwohnungen", "wohnung_miete", "haus_miete"])]
df_apartments_buy = df_apartments[df_apartments["listing_type"].isin(["Eigentumswohnungen", "wohnung_kauf", "haus_kauf"])]

data_cleaner_rent = DataCleaner(
    engine,
    numeric_cols=["living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money", "rent_complete","rent_cold"],
    american_cols=["energy_demand"],
    bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
    drop_cols=["price_m2", "url", 'general_description', 'object_description', 'place_description', 'other_description', "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "price", "price_m2", "agency_id", "id", "title", "available_from",  "rent_deposit", "ad_type", "listing_type", "rent_extra_costs"],
    drop_missing= ["rent_complete", "estate_type"],
    fill_none_cols = ["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source", "internet_speed_telekom"],
)

data_cleaner_buy = DataCleaner(
    engine,
    numeric_cols=["property_space", "price", "living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money", "rent_complete","rent_cold" ],
    american_cols=["energy_demand"],
    bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
    drop_cols=["price_m2", "url", 'general_description', 'object_description', 'place_description', 'other_description', "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "agency_id", "id", "title", "available_from",  "rent_deposit", "ad_type", "listing_type", "rent_extra_costs"],
    drop_missing= ["estate_type"],
    fill_none_cols = ["price", "lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source", "internet_speed_telekom"],
)

df_apartments_buy = data_cleaner_buy.preprocessing(df_apartments_buy)
df_houses_buy = data_cleaner_buy.preprocessing(df_houses_buy)

df_buy = pd.concat([df_apartments_buy, df_houses_buy], ignore_index=True)

numeric_cols = df_buy.select_dtypes(["float", "int"]).columns
string_cols = df_buy.select_dtypes(["object", "string"]).columns

df_buy[numeric_cols] = df_buy[numeric_cols].fillna(0)
df_buy[string_cols] = df_buy[string_cols].fillna("Missing")
    
data_cleaner_buy.store_in_db(df_buy)

feature_engineer = FeatureEngineering()
# if isinstance(df_rent, pd.DataFrame):
#     df_rent = feature_engineer.one_hot_encoding(df_rent)

#     print(df_rent.head())
#     print(df_rent.info(verbose=True))
#     print(df_rent.describe())

if isinstance(df_buy, pd.DataFrame):
    df_buy = feature_engineer.one_hot_encoding(df_buy)

    print(df_buy.head())
    print(df_buy.info(verbose=True))
    print(df_buy.describe())
