import pandas as pd
from sqlalchemy import Engine

class DataLoader:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
    
    def load_from_db(self, estate: str) -> pd.DataFrame:
        sql_stmt = f"select * from {estate}"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df