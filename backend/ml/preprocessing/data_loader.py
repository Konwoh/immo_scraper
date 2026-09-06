import pandas as pd
from sqlalchemy.engine import Engine

class DataLoader:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
    
    def load_from_db(self, estate: str) -> pd.DataFrame:
        sql_stmt = f"select * from {estate}"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df
    
    def load_house_favorites_from_db(self) -> pd.DataFrame:
        sql_stmt = f"SELECT h.* FROM favorites f LEFT JOIN houses h ON h.id = f.house_id where f.house_id IS NOT Null"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df

    def load_apartment_favorites_from_db(self) -> pd.DataFrame:
        sql_stmt = f"SELECT a.** FROM favorites f LEFT JOIN apartments a ON a.id = f.apartment_id where f.apartment_id IS NOT Null"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df

    def load_property_favorites_from_db(self) -> pd.DataFrame:
        sql_stmt = f"SELECT p.* FROM favorites f LEFT JOIN property p ON p.id = f.property_id where f.property_id IS NOT Null"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df
