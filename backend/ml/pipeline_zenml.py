import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from zenml import pipeline, step
from sklearn.metrics import mean_squared_error, r2_score
from backend.ml.preprocessing.data_cleaner import DataCleaner
from backend.ml.preprocessing.data_loader import DataLoader
from backend.ml.preprocessing.feature_engineering import FeatureEngineering
from backend.ml.training.train import DataTraining, MLModelFactory, ModelType, TrainingOutput

load_dotenv()


@step
def load_data():
    engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)
    data_loader = DataLoader(engine)

    df_apartments = data_loader.load_from_db(estate="apartments")
    df_houses = data_loader.load_from_db(estate="houses")

    return df_apartments, df_houses


@step
def clean_rent_data(data):
    df_apartments, df_houses = data
    engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)

    data_cleaner_rent = DataCleaner(
        engine,
        numeric_cols=["living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money", "rent_complete", "rent_cold"],
        american_cols=["energy_demand"],
        bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
        drop_cols=["total_costs", "price_m2", "url", "general_description", "object_description", "place_description", "other_description", "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "price", "price_m2", "agency_id", "id", "title", "available_from", "rent_deposit", "ad_type", "listing_type", "rent_extra_costs"],
        drop_missing=["rent_complete", "estate_type"],
        fill_none_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source", "internet_speed_telekom"],
    )

    df_houses_rent = data_cleaner_rent.filter_listing_types(df_houses, data_cleaner_rent.RENT_LISTING_TYPES)
    df_apartments_rent = data_cleaner_rent.filter_listing_types(df_apartments, data_cleaner_rent.RENT_LISTING_TYPES)

    df_apartments_rent = data_cleaner_rent.preprocessing(df_apartments_rent)
    df_houses_rent = data_cleaner_rent.preprocessing(df_houses_rent)

    return data_cleaner_rent.postprocessing(df_apartments_rent, df_houses_rent)


@step
def clean_buy_data(data):
    df_apartments, df_houses = data
    engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)

    data_cleaner_buy = DataCleaner(
        engine,
        numeric_cols=["property_space", "price", "living_space", "rent_income", "brokerage_commission", "notary_fees", "land_registry_entry", "energy_demand", "internet_speed_telekom", "house_money", "rent_complete", "rent_cold"],
        american_cols=["energy_demand"],
        bool_cols=["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"],
        drop_cols=["total_costs", "price_m2", "url", "general_description", "object_description", "place_description", "other_description", "created_at", "updated_at", "city", "address", "incidental_purchase_costs", "property_acquisition_tax", "brokerage_commission", "notary_fees", "land_registry_entry", "agency_id", "id", "title", "available_from", "rent_deposit", "ad_type", "listing_type", "rent_extra_costs"],
        drop_missing=["estate_type"],
        fill_none_cols=["price", "lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented", "available_from", "garage_parking_slots", "estate_condition", "interior_quality", "heating_type", "energy_performance_certificate_type", "energy_efficiency_class", "energy_demand", "total_costs", "building_year", "living_space", "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor", "energy_source", "internet_speed_telekom"],
    )

    df_houses_buy = data_cleaner_buy.filter_listing_types(df_houses, data_cleaner_buy.BUY_LISTING_TYPES)
    df_apartments_buy = data_cleaner_buy.filter_listing_types(df_apartments, data_cleaner_buy.BUY_LISTING_TYPES)

    df_apartments_buy = data_cleaner_buy.preprocessing(df_apartments_buy)
    df_houses_buy = data_cleaner_buy.preprocessing(df_houses_buy)

    df_buy = data_cleaner_buy.postprocessing(df_apartments_buy, df_houses_buy)
    data_cleaner_buy.store_in_db(df_buy)

    return df_buy

@step
def one_hot_encoding(df_buy):
    feature_engineer = FeatureEngineering()
    df_buy = feature_engineer.one_hot_encoding(df_buy)
    return df_buy

@step
def standardization(df_buy):
    feature_engineer = FeatureEngineering()
    df_buy = feature_engineer.standardization(
        df_buy,
        columns=["house_money", "living_space", "internet_speed_telekom", "building_year", "property_space"],
    )
    return df_buy

@step
def train_buy_model(df_buy_standardized) -> TrainingOutput:
    model = MLModelFactory(ModelType.LINEAR_REGRESSION)
    training = DataTraining(model)
    output = training.train(df_buy_standardized, "price")
    return output

def evaluate_model(y_pred, y_test):
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    return mse, r2

@pipeline
def ml_pipeline_zenml():
    data = load_data()

    #clean_rent_data(data)

    df_buy = clean_buy_data(data)
    df_buy = one_hot_encoding(df_buy)
    df_buy_standardized = standardization(df_buy)
    output: TrainingOutput = train_buy_model(df_buy_standardized)
    evaluate_model(output.y_pred, output.y_test)
    
if __name__ == "__main__":
    ml_pipeline_zenml()
