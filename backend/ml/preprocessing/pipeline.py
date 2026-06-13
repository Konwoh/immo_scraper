from backend.ml.preprocessing.data_cleaner import DataCleaner
from backend.ml.preprocessing.feature_engineering import FeatureEngineering
import pandas as pd
from pathlib import Path

csv_path = Path(__file__).with_name("apartments.csv")
df = pd.read_csv(csv_path, delimiter=",", dtype={"zip_code": str})
df_rent = df[df["listing_type"].isin(["Mietwohnungen", "wohnung_miete", "haus_miete"])]
df_buy = df[df["listing_type"].isin(["Eigentumswohnungen", "wohnung_kauf", "haus_kauf"])]

feature_engineer = FeatureEngineering()

data_cleaner_rent = DataCleaner(
    numeric_cols=["living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money", "rent_complete","rent_cold"],
    american_cols=["energy_demand"],
    bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
    drop_cols=["price_m2", "url", 'general_description', 'object_description', 'place_description', 'other_description', "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "price", "price_m2", "agency_id", "id", "title", "available_from",  "rent_deposit", "ad_type", "listing_type", "rent_extra_costs"],
    drop_missing= ["rent_complete", "estate_type"],
    fill_none_cols = ["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source", "internet_speed_telekom"],
)

data_cleaner_buy = DataCleaner(
    numeric_cols=["price", "living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money", "rent_complete","rent_cold" ],
    american_cols=["energy_demand"],
    bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
    drop_cols=["price_m2", "url", 'general_description', 'object_description', 'place_description', 'other_description', "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "agency_id", "id", "title", "available_from",  "rent_deposit", "ad_type", "listing_type", "rent_extra_costs"],
    drop_missing= ["estate_type"],
    fill_none_cols = ["price", "lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source", "internet_speed_telekom"],
)

df_rent = data_cleaner_rent.preprocessing(df_rent)
df_buy = data_cleaner_buy.preprocessing(df_buy)

print(data_cleaner_buy.store_in_db(df_buy))

# print(df_rent.head())
# print(df_rent.info(verbose=True))
# print(df_rent.describe())

# if isinstance(df_rent, pd.DataFrame):
#     df_rent = feature_engineer.one_hot_encoding(df_rent)

#     print(df_rent.head())
#     print(df_rent.info(verbose=True))
#     print(df_rent.describe())

# if isinstance(df_buy, pd.DataFrame):
#     df_buy = feature_engineer.one_hot_encoding(df_buy)

#     print(df_buy.head())
#     print(df_buy.info(verbose=True))
#     print(df_buy.describe())
